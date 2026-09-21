"""DOES `All filters` DECLARE A SANCTIONED DISCLOSURE SHAPE? READ, NEVER PRESS.

This probe answers condition 2 of `_audit/2026-09-19-the-disclosing-press-ruling.md`
for the one control that twelve census rows sit behind, and it answers a second,
cheaper question beside it: **does the filter vocabulary ship in the page's bytes
even where the DOM draws no control for it?** If it does, some of those rows are
reachable with no press at all.

**IT PRESSES NOTHING, CLICKS NOTHING AND TYPES NOTHING.** There is no `.click`,
no `keyboard`, no `fill` and no `press` in this file. Condition 2 is a question
about ATTRIBUTES, and an attribute is read, not activated. A probe may click
freely under `tests/test_probe_interaction_budget.py`; this one does not, because
the question it was sent to answer is a precondition for pressing and answering a
precondition by taking the act is not an answer.

## WHY A NEW READER EXISTS AT ALL, AND WHAT IT BORROWS

The shipped `dom.FILTER_PANEL_JS` returns COUNTS PER TERM and nothing else. That
is exactly right for the shaper and useless here: a count cannot say whether the
control it counted carries `aria-expanded`. So this adds the attribute half --
and it does NOT write a second matcher. `normaliseLabel` and `matchPhrase` are
LIFTED VERBATIM out of the shipped script through
`search_results.filter_normaliser_source()` / `filter_matcher_source()`, so a
match here is a match by the shipped rule, character for character. This
repository has a scar for writing a second copy of a check it already ships.

## WHAT MAY CROSS BACK, AND IT IS STRICTER THAN THE SHIPPED ALPHABET

**INTEGERS, BOOLEANS AND NULL. NO STRING AT ALL EXCEPT THIS FILE'S OWN KEY
NAMES.** Every attribute VALUE is mapped to an index in a closed vocabulary
inside the page, so even `aria-haspopup="menu"` crosses as `1`, and a value off
the vocabulary crosses as `-2` rather than as itself. A label never crosses on
any path. The gate at the bottom re-derives that claim over the finished payload
and refuses it rather than printing it.

**THE HAZARD THIS SURFACE ACTUALLY HAS.** The shipped label source is
`getAttribute("aria-label") || textContent`, and `textContent` is unconditional:
it folds in `aria-hidden` copies and clip-styled screen-reader copies, and on
THIS page the screen-reader copy of a result card carries the employer name while
the visible copy does not. So every phrase is matched TWICE -- once under the
shipped label source and once under a HIDDEN-EXCLUDED one that skips text whose
ancestor chain is `aria-hidden`, `display:none`, `visibility:hidden` or
clip-styled. A phrase that matches under both is a control; a phrase that matches
only under the shipped source is hidden text, which is the exact class that made
`N 82` unbankable.

## THE CONTROLS, BECAUSE A READING THAT CANNOT DISCRIMINATE IS NOT EVIDENCE

    positive   `next`          whole-label equality, measured 1 on this page by
                               a prior wave -- proves the equality path is live
    negative   `school anise`  synthetic, must read 0 -- proves it is not saluting
    shut       `show results`  the panel's submit; 0 while the panel is shut and
                               it is never pressed open, so 0 is the expectation
    cross-page the feed        the same code, the same call, a different page

## THE PAYLOAD HALF

`page.content()` is taken into a Python string, normalised two ways, and each
phrase COUNTED in it. The string is never printed, never written and never
returned. Two normalisations because a payload key is `currentCompany` where a
label is `Current company`: the TIGHT form drops every non-alphanumeric so
camelCase, kebab-case and spaced all collapse to one needle, and the SPACED form
is the conservative one. `school anise` prices the false-positive rate of both.

**A NONZERO PAYLOAD COUNT DOES NOT BANK A ROW.** It says the vocabulary is in the
bytes. It does not say this server ships a reader that can reach it, and a census
row is about what this server can reach. What it re-prices is the BLOCKER.

Run::

    set LINKEDIN_CDP_ATTACH=1
    venv\\Scripts\\python.exe scripts/_probe_all_filters_disclosure_shape.py

ATTACH ONLY. It refuses to run otherwise: launching a second Chrome against the
persistent profile costs the signed-in session and only a human can put it back.
Opens its OWN tab and closes it in a `finally` -- the page, never the context.

Writes its record under gitignored `_state/`. Prints integers.
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import pathlib
import re
import subprocess
import sys
import time

REPO = pathlib.Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from linkedin_server import config, dom, press, readonly, search_results  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402

#: THE VOCABULARY SHIPPED IN. Index is the contract; the page returns positions
#: in this tuple and never a word. The three controls are first so a reader
#: meets them before the census terms.
PROBE_PHRASES: tuple[str, ...] = (
    "all filters",          # 0  THE CONTROL UNDER TEST
    "next",                 # 1  positive control -- equality path, live
    "school anise",         # 2  negative control -- synthetic, must be 0
    "show results",         # 3  the panel's submit; 0 while the panel is shut
    "current company",      # 4  N 84
    "connections of",       # 5  N 85
    "followers of",         # 6  N 86
    "past company",         # 7  N 87
    "profile language",     # 8  N 90
    "open to volunteering", # 9  N 91
    "service categories",   # 10 N 92
    "locations",            # 11 N 83 -- BANKED; reproduces a known positive
    "school",               # 12 N 88
    "industry",             # 13 N 89
    "people",               # 14 N 80
    "connections",          # 15 N 81
    "keywords",             # 16 N 93
    "actively hiring",      # 17 N 82 -- reproduces a known nonzero
)

#: The census row each phrase serves, or "" for a control. Checked against the
#: shaper's own ledger below rather than against memory.
PROBE_PHRASE_ROWS: tuple[str, ...] = (
    "", "", "", "",
    "N 84", "N 85", "N 86", "N 87", "N 90", "N 91", "N 92",
    "N 83", "N 88", "N 89", "N 80", "N 81", "N 93", "N 82",
)

#: CLOSED VOCABULARIES FOR THE TWO SANCTIONED ATTRIBUTES. A value is reported as
#: its INDEX here; -1 means the attribute is absent and -2 means present with a
#: value off this list. Never the value itself.
EXPANDED_VALUES: tuple[str, ...] = ("true", "false")
HASPOPUP_VALUES: tuple[str, ...] = (
    "true", "menu", "listbox", "tree", "grid", "dialog", "false",
)

ABSENT = -1
OFF_VOCABULARY = -2

#: Every key this probe's payload may carry. The gate refuses anything else, and
#: refuses EVERY string that is not one of these.
_OWN_KEYS: frozenset[str] = frozenset({
    "provenance", "head", "sha256_press", "sha256_search_results", "sha256_dom",
    "mode", "taken_at", "surfaces", "surface_index", "landed_where_it_was_sent",
    "panel", "controls_seen", "matched_controls", "unmatched_controls",
    "empty_labels", "values_refused", "polls", "settled", "controls_first",
    "controls_last", "stable_reads_required", "poll_ms", "max_polls",
    "zero_polls", "panel_wait", "counts",
    "shape", "controls_scanned", "expanded_nodes", "haspopup_nodes",
    "dialogs", "menus", "menuitems", "listboxes",
    "matched_shipped_label", "matched_hidden_excluded",
    "matched_with_aria_label",
    "with_aria_expanded", "with_aria_haspopup",
    "first_expanded_value", "first_haspopup_value",
    "first_expanded_index", "first_haspopup_index",
    "payload", "tight_hits", "spaced_hits", "code_blocks", "html_length",
    "doc_hits", "data_hits", "doc_bodies", "data_bodies", "doc_bytes",
    "data_bytes", "unreadable",
    "counter", "invitations", "gate_raised", "error_type",
    "phrase_count", "row_ledger_agrees",
})

SURFACES: tuple[str, ...] = ("people_search", "feed")


def say(line: str = "") -> None:
    print(line, flush=True)


def phrase_index() -> list[list]:
    """``[[phrase, index], ...]`` SORTED LONGEST-FIRST -- the shipped ordering.

    Same key as `search_results.filter_phrase_index`, and for the same reason:
    `connections` is a PREFIX of `connections of`, and they are different rows.
    The page loop takes the order as given and must not re-sort.
    """
    pairs = [(phrase, index) for index, phrase in enumerate(PROBE_PHRASES)]
    pairs.sort(key=lambda pair: (-len(pair[0].split()), -len(pair[0]), pair[0]))
    return [[phrase, index] for phrase, index in pairs]


def row_ledger_agrees() -> bool:
    """Does every census row this probe claims to serve exist in the shaper's
    own `FILTER_TERM_ROWS`? A term that serves a row nobody enumerated is a
    term nobody asked for.
    """
    claimed = {row for row in PROBE_PHRASE_ROWS if row}
    return claimed.issubset(set(search_results.FILTER_TERM_ROWS))


SHAPE_JS_TEMPLATE = """
(args) => {
  __NORMALISER__;
  __MATCHER__;
  const phrases = args.phrases || [];
  const termCount = args.termCount || 0;
  const expandedValues = args.expandedValues || [];
  const haspopupValues = args.haspopupValues || [];
  const ABSENT = -1;
  const OFF = -2;

  // THE SHIPPED CONTROL SELECTOR, character for character.
  const controls = Array.from(
    document.querySelectorAll(
      "button, [role='button'], [role='radio'], [role='checkbox'], " +
      "[role='tab'], select, fieldset legend, [aria-label]"
    )
  );
  const expandedNodes = Array.from(document.querySelectorAll("[aria-expanded]"));
  const haspopupNodes = Array.from(document.querySelectorAll("[aria-haspopup]"));

  // IS THIS NODE HIDDEN FROM A SIGHTED READER OR MARKED HIDDEN FROM THE
  // ACCESSIBILITY TREE? Either way its text is not the control's visible label,
  // and `textContent` folds it in regardless.
  const isHiddenish = (node) => {
    if (!node || node.nodeType !== 1) return false;
    if (node.getAttribute("aria-hidden") === "true") return true;
    let style = null;
    try { style = window.getComputedStyle(node); } catch (e) { return false; }
    if (!style) return false;
    if (style.display === "none") return true;
    if (style.visibility === "hidden") return true;
    // The clip-styled screen-reader pattern, in its two spellings.
    if (style.clipPath && style.clipPath !== "none") return true;
    if (style.clip && style.clip !== "auto") return true;
    return false;
  };

  // The label with every hidden subtree subtracted. Walks TEXT NODES so a
  // hidden ancestor removes its whole subtree, which is how the pattern is
  // actually written.
  const visibleText = (root) => {
    let out = "";
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null);
    while (walker.nextNode()) {
      const textNode = walker.currentNode;
      let hidden = false;
      let parent = textNode.parentNode;
      while (parent && parent !== root.parentNode) {
        if (isHiddenish(parent)) { hidden = true; break; }
        parent = parent.parentNode;
      }
      if (!hidden) out += " " + (textNode.nodeValue || "");
    }
    return out;
  };

  const zeros = () => Array.from({ length: termCount }, () => 0);
  const absents = () => Array.from({ length: termCount }, () => ABSENT);

  const matchedShipped = zeros();
  const matchedVisible = zeros();
  // HOW MANY MATCHES CARRIED AN EXPLICIT `aria-label`. Without this the
  // hidden-excluded column is UNINTERPRETABLE on a live page: both label
  // sources prefer `aria-label`, so where one exists the two columns agree by
  // construction and their agreement proves nothing about hidden text.
  const withAriaLabel = zeros();
  const withExpanded = zeros();
  const withHaspopup = zeros();
  const firstExpandedValue = absents();
  const firstHaspopupValue = absents();
  const firstExpandedIndex = absents();
  const firstHaspopupIndex = absents();

  const classify = (raw, vocabulary) => {
    if (raw === null || raw === undefined) return ABSENT;
    const index = vocabulary.indexOf(String(raw).toLowerCase());
    return index >= 0 ? index : OFF;
  };

  for (const node of controls) {
    const shippedRaw = node.getAttribute("aria-label") || node.textContent || "";
    const label = normaliseLabel(shippedRaw);
    if (!label) continue;
    let index = -1;
    for (const pair of phrases) {
      if (matchPhrase(label, pair[0])) { index = pair[1]; break; }
    }
    if (index < 0 || index >= termCount) continue;
    matchedShipped[index] += 1;

    // THE SAME MATCH UNDER A LABEL SOURCE THAT EXCLUDES HIDDEN TEXT.
    const visibleRaw =
      node.getAttribute("aria-label") || visibleText(node) || "";
    if (matchPhrase(normaliseLabel(visibleRaw), phrases.find(
          (pair) => pair[1] === index)[0])) {
      matchedVisible[index] += 1;
    }

    if (node.getAttribute("aria-label")) withAriaLabel[index] += 1;
    const expandedAttribute = node.getAttribute("aria-expanded");
    const haspopupAttribute = node.getAttribute("aria-haspopup");
    if (expandedAttribute !== null) withExpanded[index] += 1;
    if (haspopupAttribute !== null) withHaspopup[index] += 1;
    if (matchedShipped[index] === 1) {
      firstExpandedValue[index] = classify(expandedAttribute, expandedValues);
      firstHaspopupValue[index] = classify(haspopupAttribute, haspopupValues);
      firstExpandedIndex[index] = expandedNodes.indexOf(node);
      firstHaspopupIndex[index] = haspopupNodes.indexOf(node);
    }
  }

  return {
    controls_scanned: controls.length,
    expanded_nodes: expandedNodes.length,
    haspopup_nodes: haspopupNodes.length,
    dialogs: document.querySelectorAll("[role='dialog']").length,
    menus: document.querySelectorAll("[role='menu']").length,
    menuitems: document.querySelectorAll("[role='menuitem']").length,
    listboxes: document.querySelectorAll("[role='listbox']").length,
    matched_shipped_label: matchedShipped,
    matched_hidden_excluded: matchedVisible,
    matched_with_aria_label: withAriaLabel,
    with_aria_expanded: withExpanded,
    with_aria_haspopup: withHaspopup,
    first_expanded_value: firstExpandedValue,
    first_haspopup_value: firstHaspopupValue,
    first_expanded_index: firstExpandedIndex,
    first_haspopup_index: firstHaspopupIndex,
  };
}
"""


def shape_js() -> str:
    """The script, with the SHIPPED matcher and normaliser spliced in.

    Lifted rather than retyped: `filter_matcher_source()` returns the exact
    characters the shipped panel script compares labels with, so a match here
    cannot drift from a match there.
    """
    return (
        SHAPE_JS_TEMPLATE
        .replace("__NORMALISER__", search_results.filter_normaliser_source())
        .replace("__MATCHER__", search_results.filter_matcher_source())
    )


async def read_shape(page) -> dict:
    """Attribute facts per phrase. Integers only."""
    raw = await page.evaluate(  # readonly-ok: reads attributes, presses nothing
        shape_js(),
        {
            "phrases": phrase_index(),
            "termCount": len(PROBE_PHRASES),
            "expandedValues": list(EXPANDED_VALUES),
            "haspopupValues": list(HASPOPUP_VALUES),
        },
    )
    return raw if isinstance(raw, dict) else {}


_TIGHT = re.compile(r"[^a-z0-9]+")


def count_in_payload(html: str) -> dict:
    """Count each shipped-in phrase in the page's own bytes. INTEGERS ONLY.

    `html` is never printed, never written and never returned. Two
    normalisations: TIGHT drops every non-alphanumeric so `currentCompany`,
    `current-company` and `Current company` collapse to one needle; SPACED is
    the conservative word-boundary form.
    """
    lowered = html.lower()
    tight = _TIGHT.sub("", lowered)
    spaced = " " + _TIGHT.sub(" ", lowered).strip() + " "
    return {
        "tight_hits": [tight.count(p.replace(" ", "")) for p in PROBE_PHRASES],
        "spaced_hits": [spaced.count(" " + p + " ") for p in PROBE_PHRASES],
        "code_blocks": lowered.count("<code"),
        "html_length": len(html),
    }


#: WHICH RESPONSE BUCKETS ARE COUNTED, and they are kept APART on purpose.
#: A filter name appearing in a 2 MB JavaScript bundle says the product has such
#: a filter somewhere; a filter name in THIS page's data responses says the
#: vocabulary was delivered for THIS search. Summing them would answer the
#: second question with the first one's evidence.
_DOCUMENT_TYPES = frozenset({"document"})
_DATA_TYPES = frozenset({"xhr", "fetch"})


class WireCounter:
    """Counts the shipped-in phrases across RESPONSE BODIES. Integers only.

    **NO BODY IS STORED, PRINTED OR RETURNED.** Each body is counted and
    dropped inside the handler. A body on this surface is denser in third-party
    identity than anything else on the platform, which is why the only thing
    that survives this object is an array of integers.

    A body that cannot be read is COUNTED AS UNREADABLE, never as a zero -- a
    reading that did not happen and a reading that saw nothing are different
    facts and only one of them is evidence.
    """

    def __init__(self) -> None:
        self.doc_hits = [0] * len(PROBE_PHRASES)
        self.data_hits = [0] * len(PROBE_PHRASES)
        self.doc_bodies = 0
        self.data_bodies = 0
        self.doc_bytes = 0
        self.data_bytes = 0
        self.unreadable = 0

    async def consume(self, response) -> None:
        try:
            kind = response.request.resource_type
        except Exception:  # noqa: BLE001
            self.unreadable += 1
            return
        if kind not in _DOCUMENT_TYPES and kind not in _DATA_TYPES:
            return
        try:
            body = await response.text()
        except Exception:  # noqa: BLE001 - type is not even kept; a failed
            # body read is an outage, and an outage filed as an absence is the
            # error this repository has a test for.
            self.unreadable += 1
            return
        counts = count_in_payload(body)["tight_hits"]
        size = len(body)
        del body
        if kind in _DOCUMENT_TYPES:
            self.doc_bodies += 1
            self.doc_bytes += size
            for index, value in enumerate(counts):
                self.doc_hits[index] += value
        else:
            self.data_bodies += 1
            self.data_bytes += size
            for index, value in enumerate(counts):
                self.data_hits[index] += value

    def payload(self) -> dict:
        return {
            "doc_hits": self.doc_hits,
            "data_hits": self.data_hits,
            "doc_bodies": self.doc_bodies,
            "data_bodies": self.data_bodies,
            "doc_bytes": self.doc_bytes,
            "data_bytes": self.data_bytes,
            "unreadable": self.unreadable,
        }


def _as_int(value):
    """An int, or None. NEVER a zero standing in for an unread counter.

    Digit-scraped rather than `int()`-cast: `int("Jane Smith")` quotes the value
    it refused verbatim into its own ValueError, which is how a name left this
    process on 2026-09-20.
    """
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    digits = "".join(ch for ch in str(value) if ch.isdigit())
    return int(digits) if digits else None


async def read_counter(page) -> dict:
    """The outward counter, read for the RECORD of condition 3.

    Readability is NOT condition 3 -- the 2026-09-19 amendment says a merely
    readable counter prices nothing. This is here so the report can state
    whether an outward counter is even available on this surface, which is a
    different fact and the one a future ruling would need.
    """
    try:
        badge = await dom.read_invitation_badge(page)
        label = badge.get("label") if isinstance(badge, dict) else None
        return {"invitations": _as_int(label)}
    except Exception as exc:  # noqa: BLE001 - type only, never the message
        say(f"    invitation badge raised {type(exc).__name__}")
        return {"invitations": None}


def _gate(payload: object, where: str = "") -> None:
    """Refuse any string outside this file's own key names. NEVER PRINTS IT.

    Stricter than the shipped alphabet gate: this payload is supposed to carry
    NO page-derived string at all, so the allowed set is the key names and
    nothing else. On a violation it names the FIELD PATH only -- on this surface
    an unexpected string is a person's name until shown otherwise, and "show me
    what leaked" is how it leaks a second time.
    """
    if isinstance(payload, dict):
        for key, value in payload.items():
            if not isinstance(key, str) or key not in _OWN_KEYS:
                raise ValueError(f"UNVOCABULARY KEY at {where or '<root>'}")
            _gate(value, f"{where}.{key}" if where else key)
        return
    if isinstance(payload, (list, tuple)):
        for position, value in enumerate(payload):
            _gate(value, f"{where}[{position}]")
        return
    if isinstance(payload, str):
        if payload not in _OWN_KEYS:
            raise ValueError(f"UNVOCABULARY STRING at {where or '<root>'}")
        return
    if isinstance(payload, (int, float, bool)) or payload is None:
        return
    raise ValueError(f"UNEXPECTED TYPE {type(payload).__name__} at {where}")


def _sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _head() -> str:
    """The commit this code is, or a LOUD marker naming why it is unknown.

    Never an empty string: an outage and an absence are different findings, and
    returning a falsy datum out of an exception handler files the first as the
    second.
    """
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(REPO), capture_output=True, text=True, timeout=20,
        )
    except Exception as exc:  # noqa: BLE001
        return f"HEAD-UNKNOWN-{type(exc).__name__}"
    head = (out.stdout or "").strip()
    return head if head else "HEAD-UNKNOWN-EMPTY"


def provenance() -> dict:
    return {
        "head": _head(),
        "sha256_press": _sha(REPO / "linkedin_server" / "press.py"),
        "sha256_search_results": _sha(
            REPO / "linkedin_server" / "search_results.py"
        ),
        "sha256_dom": _sha(REPO / "linkedin_server" / "dom.py"),
        "mode": "attach" if config.CDP_ATTACH else "launch",
    }


def _print_shape(record: dict) -> None:
    shape = record["shape"]
    say(
        "    controls=%d  [aria-expanded]=%d  [aria-haspopup]=%d  "
        "dialogs=%d menus=%d menuitems=%d listboxes=%d"
        % (
            shape["controls_scanned"], shape["expanded_nodes"],
            shape["haspopup_nodes"], shape["dialogs"], shape["menus"],
            shape["menuitems"], shape["listboxes"],
        )
    )
    say(
        "      %-4s %-22s %-5s %-5s %-5s %-6s %-7s %-6s %-7s %-6s %-7s"
        % ("idx", "row", "ship", "vis", "aria", "hasEx", "hasPop", "exVal",
           "popVal", "exIdx", "popIdx")
    )
    for index in range(len(PROBE_PHRASES)):
        say(
            "      %-4d %-22s %-5d %-5d %-5d %-6d %-7d %-6d %-7d %-6d %-7d"
            % (
                index,
                PROBE_PHRASE_ROWS[index] or "-control-",
                shape["matched_shipped_label"][index],
                shape["matched_hidden_excluded"][index],
                shape["matched_with_aria_label"][index],
                shape["with_aria_expanded"][index],
                shape["with_aria_haspopup"][index],
                shape["first_expanded_value"][index],
                shape["first_haspopup_value"][index],
                shape["first_expanded_index"][index],
                shape["first_haspopup_index"][index],
            )
        )


def _print_payload(record: dict) -> None:
    payload = record["payload"]
    say(
        "    dom_html=%d code_blocks=%d | doc bodies=%d bytes=%d | "
        "data bodies=%d bytes=%d | unreadable=%d"
        % (
            payload["html_length"], payload["code_blocks"],
            payload["doc_bodies"], payload["doc_bytes"],
            payload["data_bodies"], payload["data_bytes"],
            payload["unreadable"],
        )
    )
    say(
        "      %-4s %-22s %-7s %-7s %-7s %-7s"
        % ("idx", "row", "domTgt", "domSpc", "wireDoc", "wireData")
    )
    for index in range(len(PROBE_PHRASES)):
        say(
            "      %-4d %-22s %-7d %-7d %-7d %-7d"
            % (
                index,
                PROBE_PHRASE_ROWS[index] or "-control-",
                payload["tight_hits"][index],
                payload["spaced_hits"][index],
                payload["doc_hits"][index],
                payload["data_hits"][index],
            )
        )


async def one_surface(page, url: str, surface_index: int) -> dict:
    # THE WIRE LISTENER GOES ON BEFORE THE NAVIGATION, because a response that
    # has already arrived cannot be listened for. The first run of this probe
    # measured `code_blocks` 0 on both surfaces -- the serialized DOM carries no
    # hydration payload at all -- so "the vocabulary is not in the page" was a
    # claim about the post-hydration document and NOT about the bytes.
    wire = WireCounter()

    def _on_response(response) -> None:
        asyncio.ensure_future(wire.consume(response))

    page.on("response", _on_response)
    try:
        landed = await BROWSER.goto(page, url)
        matched = str(landed).rstrip("/") == url.rstrip("/")
        settled = await search_results.read_filters_when_settled(page)
        shape = await read_shape(page)
        html = await page.content()
        payload = count_in_payload(html)
        del html
        counter = await read_counter(page)
        # LET THE IN-FLIGHT BODY READS FINISH before the listener comes off.
        # Without this the wire counts are a race against teardown, and a race
        # reports fewer bodies on a fast box than on a slow one.
        await asyncio.sleep(2.0)
    finally:
        page.remove_listener("response", _on_response)
    payload.update(wire.payload())
    return {
        "surface_index": surface_index,
        "landed_where_it_was_sent": matched,
        "panel": {
            "controls_seen": settled.get("controls_seen"),
            "matched_controls": settled.get("matched_controls"),
            "unmatched_controls": settled.get("unmatched_controls"),
            "empty_labels": settled.get("empty_labels"),
            "values_refused": settled.get("values_refused"),
            "panel_wait": settled.get("panel_wait"),
        },
        "shape": shape,
        "payload": payload,
        "counter": counter,
    }


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--out",
        default=str(REPO / "_state" / "all-filters-disclosure-shape.json"),
    )
    parser.add_argument(
        "--skip-feed-control",
        action="store_true",
        help="run WITHOUT the cross-page control. Output cannot re-price a row.",
    )
    args = parser.parse_args()

    if not config.CDP_ATTACH:
        say("REFUSING: LINKEDIN_CDP_ATTACH is not set.")
        say("This probe attaches to a Chrome that is already running. Launching")
        say("a second one against the persistent profile costs the signed-in")
        say("session, and only a human can put it back.")
        return 2

    people = search_results.PEOPLE_SEARCH_URL
    if not readonly.is_read_url(people):
        say("REFUSING: the people-search address is not on the read allowlist.")
        return 2

    record = {
        "provenance": provenance(),
        "taken_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "phrase_count": len(PROBE_PHRASES),
        "row_ledger_agrees": row_ledger_agrees(),
        "surfaces": [],
    }

    say("PROVENANCE -- which code actually ran")
    for key, value in record["provenance"].items():
        say(f"  {key:<24} {value}")
    say(f"  {'phrases':<24} {record['phrase_count']}")
    say(f"  {'row_ledger_agrees':<24} {record['row_ledger_agrees']}")
    say(f"  {'sanctioned_shapes':<24} {list(press.SANCTIONED_SHAPES)}")
    say()

    try:
        await BROWSER.start()
    except Exception as exc:  # noqa: BLE001 - type only, never the message
        say(f"COULD NOT ATTACH: {type(exc).__name__}")
        return 2

    # OUR tab, held so the finally can close it. THE PAGE, NEVER THE CONTEXT --
    # in attach mode the context is a real signed-in Chrome and closing it takes
    # that browser down.
    tab = None
    try:
        async with BROWSER.session() as page:
            tab = page
            targets = [(people, 0)]
            if not args.skip_feed_control:
                targets.append((f"{config.BASE_URL}/feed/", 1))
            for url, surface_index in targets:
                say(f"SURFACE {surface_index} -- {SURFACES[surface_index]}")
                one = await one_surface(page, url, surface_index)
                _gate(one, f"surface{surface_index}")
                record["surfaces"].append(one)
                say(f"    landed where sent: {one['landed_where_it_was_sent']}")
                wait = one["panel"]["panel_wait"] or {}
                say(
                    "    panel: settled=%s polls=%s first=%s last=%s"
                    % (
                        wait.get("settled"), wait.get("polls"),
                        wait.get("controls_first"), wait.get("controls_last"),
                    )
                )
                say(
                    "    invitation counter reads: %s"
                    % (one["counter"]["invitations"],)
                )
                _print_shape(one)
                _print_payload(one)
                say()
    except ValueError as exc:
        say(f"PROBE REFUSED ITS OWN OUTPUT: {exc}")
        say("A string outside this file's key names reached the payload. The")
        say("value is deliberately not printed. Treat it as a leak until shown")
        say("otherwise, and do not re-run to 'see what it was'.")
        record["gate_raised"] = True
        _write(args.out, record)
        return 1
    except Exception as exc:  # noqa: BLE001 - type only, never the message
        say(f"PROBE FAILED: {type(exc).__name__}")
        record["error_type"] = type(exc).__name__
        _write(args.out, record)
        return 1
    finally:
        if tab is not None and not tab.is_closed():
            await tab.close()
        await BROWSER.stop()

    _write(args.out, record)
    say(f"WROTE {pathlib.Path(args.out).name} under _state/ (gitignored)")
    return 0


def _write(out: str, record: dict) -> None:
    path = pathlib.Path(out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2), encoding="ascii")


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
