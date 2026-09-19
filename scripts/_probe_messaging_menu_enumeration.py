"""ENUMERATE the messaging menus without any label leaving the browser.

WHAT THIS ADDS TO THE PREDECESSOR, and it is one thing.
``scripts/_probe_messaging_surface_census.py`` counted this surface under a
rule it stated plainly: **no page string enters the process.** It was right,
and this probe keeps that rule byte for byte. What it could not then do was say
what the menus CONTAIN, and it named that gap as the cheapest open item in the
whole family (``_audit/2026-09-05-messaging-rows.md`` section 7):

    "whether the 12 role=menuitem elements and the 12 React-labelled controls
    are the same twelve ... It is the only thing standing between rows
    17/67/76 and a clean retirement recommendation."

**THE MOVE IS TO CLASSIFY IN THE PAGE AND CARRY BACK ONLY THE VERDICT.** The
accessible names stay in the browser. What crosses the CDP boundary is an
integer index into a phrase list THIS FILE WROTE, and Python turns that index
into a term from ``linkedin_server.menus.VOCABULARY``. So the enumeration is
real and the standing rule is untouched: every string printed is one written
here or in that module.

## THE TWELVE-VERSUS-TWELVE QUESTION IS ANSWERED BY IDENTITY, NOT BY COUNTS

The predecessor declined to spend one observation twice and said so:
**an equal count is a correlation, not an identity.** So this probe does not
compare 12 with 12. It takes the two element sets in the page, intersects them
AS ELEMENTS, and returns the size of the intersection. Two sets of twelve that
share nothing and two sets of twelve that are the same twelve are different
numbers here, which is the entire point.

## THE PARITY CONTROL, WHICH RUNS BEFORE ANY CLASSIFICATION IS BELIEVED

Matching now exists twice -- once in ``menus._contains_phrase`` and once in the
JavaScript below -- and two implementations of one rule is how a checker
quietly stops agreeing with itself. **So the first thing this probe does on the
page is run MY OWN corpus through the JavaScript and compare every verdict
against Python's.** The corpus is a list of strings written in this file,
including the two that caught the real defect in the Python matcher
(a single-word term must be the WHOLE label, because a name adds tokens).

**IF PARITY FAILS, THE PROBE REFUSES TO REPORT ANY CLASSIFICATION AT ALL** and
prints the disagreeing INDEX -- never the string, though in that one case the
string is mine. A control that cannot stop the run is decoration.

## WHAT IT WILL NOT DO

**IT PRESSES NOTHING AND IT SENDS NOTHING.** The predecessor's ruling stands
and is not mine to overturn: every click in this package is gated through
``readonly.SANCTIONED_MUTATIONS`` and an overflow menu on a real conversation
is a plausible home for ``Delete``. The items were measured to be in the DOM
with nothing pressed, so the press is unnecessary as well as unsanctioned.

Opening a menu to enumerate it would be a read. **Clicking an item in it is
not, and no code path here can do either.**

Run:  LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224 \
      ./venv/Scripts/python.exe scripts/_probe_messaging_menu_enumeration.py

Writes NOTHING. Sends NOTHING. Presses NOTHING. Types NOTHING.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import dom, menus, shape  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import FEED_URL, MESSAGING_URL  # noqa: E402

#: The ordered phrase list handed to the page. Index N here is index N there,
#: and the term it resolves to is looked up on THIS side.
_PHRASES: list[str] = [phrase for phrase, _term in menus._PHRASE_INDEX]
_TERMS: list[str] = [term for _phrase, term in menus._PHRASE_INDEX]

#: THE PARITY CORPUS. Every string is written here. The first two are the pair
#: that convicted the Python matcher's first version, kept because a corpus
#: that only contains cases the author already handles is the probe set this
#: repository has been caught by three times.
_PARITY_CORPUS: list[str] = [
    "Star Anise",
    "Marketing Analytics",
    "Delete conversation",
    "Delete this conversation",
    "Mark as unread",
    "Mark as read",
    "React",
    "React to message",
    "More",
    "Show more options",
    "Focused",
    "Other",
    "Archive",
    "Unarchive",
    "Report this message",
    "Translate",
    "Star",
    "Like",
    "Celebrate",
    "Message requests",
    "Open emoji keyboard",
    "Attach a file",
    "Send",
    "",
    "   ",
    "Delete/Archive",
]

#: THE ELEMENT GROUPS. Structural first, vocabulary second -- the same ordering
#: discipline the predecessor used, for the same reason: a zero on a structural
#: selector is about LinkedIn, a zero on a vocabulary selector is about me.
_GROUPS: list[tuple[str, str]] = [
    ("CONTROL button", "button"),
    ("role=menu", '[role="menu"]'),
    ("role=menuitem", '[role="menuitem"]'),
    ("button[aria-expanded]", "button[aria-expanded]"),
    ("label contains React", '[aria-label*="React"]'),
    ("role=tab", '[role="tab"]'),
    ("role=listitem", '[role="listitem"]'),
]

#: The two sets whose INTERSECTION is the open question.
_OVERLAP_PAIRS: list[tuple[str, str, str]] = [
    ("role=menuitem", '[role="menuitem"]', '[aria-label*="React"]'),
]

# ---------------------------------------------------------------------------
# THE IN-PAGE MATCHER. It mirrors ``menus._contains_phrase`` and the parity
# control exists because it mirrors it BY HAND.
# ---------------------------------------------------------------------------
_JS_MATCHER = """
(args) => {
  const phrases = args.phrases;
  const normalise = (s) => {
    let out = "";
    let space = true;
    const low = String(s).toLowerCase();
    for (const ch of low) {
      if ((ch >= 'a' && ch <= 'z') || (ch >= '0' && ch <= '9')) {
        out += ch; space = false;
      } else if (!space) { out += ' '; space = true; }
    }
    return out.trim();
  };
  const matchIndex = (label) => {
    if (label === null || label === undefined) return -2;
    const raw = String(label).slice(0, args.maxChars);
    if (!raw.trim()) return -2;
    const norm = normalise(raw);
    if (!norm) return -2;
    const words = norm.split(' ').filter(Boolean);
    for (let i = 0; i < phrases.length; i++) {
      const needle = phrases[i].split(' ').filter(Boolean);
      if (!needle.length || needle.length > words.length) continue;
      if (needle.length === 1) {
        if (words.length === 1 && words[0] === needle[0]) return i;
        continue;
      }
      for (let s = 0; s + needle.length <= words.length; s++) {
        let ok = true;
        for (let k = 0; k < needle.length; k++) {
          if (words[s + k] !== needle[k]) { ok = false; break; }
        }
        if (ok) return i;
      }
    }
    return -1;
  };
  // -- the accessible name, as close as a page script can get to it --------
  const nameOf = (el) => {
    const aria = el.getAttribute('aria-label');
    if (aria && aria.trim()) return aria;
    const labelledby = el.getAttribute('aria-labelledby');
    if (labelledby) {
      const parts = labelledby.split(/\\s+/)
        .map((id) => document.getElementById(id))
        .filter(Boolean)
        .map((n) => n.textContent || '');
      const joined = parts.join(' ').trim();
      if (joined) return joined;
    }
    return el.textContent || '';
  };

  if (args.mode === 'parity') {
    return { verdicts: args.corpus.map(matchIndex) };
  }

  const out = { groups: {}, overlaps: {} };
  for (const [name, selector] of args.groups) {
    const nodes = Array.from(document.querySelectorAll(selector));
    const verdicts = nodes.map((el) => matchIndex(nameOf(el)));
    // SHAPE FACTS for the unmatched, computed here so the string stays here.
    const shapes = [];
    nodes.forEach((el, i) => {
      if (verdicts[i] !== -1) return;
      const raw = String(nameOf(el)).slice(0, args.maxChars).trim();
      const toks = raw.split(/\\s+/).filter(Boolean);
      shapes.push({
        len: raw.length,
        tokens: toks.length,
        digits: /[0-9]/.test(raw),
        caps: toks.length > 0 && toks.every(
          (t) => !/^[A-Za-z]/.test(t) || t[0] === t[0].toUpperCase()),
      });
    });
    out.groups[name] = { count: nodes.length, verdicts: verdicts, shapes: shapes };
  }
  for (const [name, selA, selB] of args.overlaps) {
    const a = Array.from(document.querySelectorAll(selA));
    const b = new Set(Array.from(document.querySelectorAll(selB)));
    let shared = 0;
    for (const el of a) if (b.has(el)) shared += 1;
    out.overlaps[name] = { a: a.length, b: b.size, shared: shared };
  }
  return out;
}
"""

_SPENT: list[int] = []


def _verdict_to_classification(index: int, shape_queue: list) -> dict:
    """Turn an in-page index into the SAME shape ``menus.classify`` returns.

    ``-2`` is the page's spelling of ``no_label``; ``-1`` is ``unmatched`` and
    takes the next shape record. Anything else indexes the phrase list.
    """
    if index == -2:
        return {"matched": False, "refused": "no_label"}
    if index == -1:
        raw = shape_queue.pop(0) if shape_queue else {}
        return {
            "matched": False,
            "refused": "unmatched",
            "band": menus._band(int(raw.get("len") or 0)),
            "tokens": int(raw.get("tokens") or 0),
            "has_digits": bool(raw.get("digits")),
            "all_capitalised": bool(raw.get("caps")),
        }
    return {"matched": True, "term": _TERMS[index]}


async def _read_both_badges(page):
    """Both nav badges, REDUCED TO SCALARS AT THE BOUNDARY, plus furniture.

    **THE REDUCTION IS COPIED FROM THE PREDECESSOR AND SO IS THE REASON.** The
    shaped badge dicts carry ``why``, ``saw`` and ``shaped_label`` -- fields
    that can hold text LinkedIn wrote -- and a printer handed the whole dict
    can reach them. Handing back two pairs of scalars closes that in the
    SIGNATURE rather than in a habit, so adding a label later requires changing
    the return type, which is visible in a diff.

    **AND IT IS READ THROUGH ``shape`` RATHER THAN OFF THE DOM READER.** My
    first version called ``dom.read_messaging_badge`` and asked it for
    ``state`` and ``new_since_last_visit``. That reader returns ``links`` and
    ``label`` and has never had those two fields -- I took the names from an
    AUDIT DOCUMENT instead of from the code, and both came back ``None``, which
    the probe correctly refused on. The refusal was right for the wrong reason,
    which is the most expensive kind: a relayed field name is a reading with a
    timestamp, same as a relayed number.

    The third return value is the FURNITURE COUNT LIST, and it exists so the
    refusal can say what it saw. Signed-out and aimed-wrong both print
    ``state=None``; only the furniture separates them.
    """
    html = await page.content()
    messaging = shape.messaging_badge(html)
    invitation = shape.invitation_badge(await dom.read_invitation_badge(page))
    furniture = []
    for name, selector in (
        ("nav messaging anchors", 'a[href*="/messaging/"]'),
        ("nav feed anchors", 'a[href*="/feed/"]'),
        ("buttons on the page", "button"),
        ("sign-in forms", 'form[action*="login"]'),
    ):
        try:
            furniture.append((name, int(await page.locator(selector).count())))
        except Exception as exc:  # noqa: BLE001
            furniture.append((name, "reader failed: %s" % type(exc).__name__))
    return (
        (messaging.get("new_since_last_visit"), messaging.get("state")),
        (invitation.get("pending"), invitation.get("state")),
        furniture,
    )


def _python_index(text) -> int:
    """The phrase index PYTHON would pick. The parity control's other half.

    Deliberately a mirror of ``menus.classify``'s loop rather than a call to
    it: ``classify`` returns a TERM, and several phrases share a term, so a
    comparison through the term cannot tell a matcher that picked the right
    phrase from one that picked a different phrase with the same label. The
    index is the tighter comparison and it is the one the page returns.
    """
    if text is None or not str(text).strip():
        return -2
    raw = str(text)[:menus.MAX_LABEL_CHARS]
    normalised = menus._normalise(raw)
    if not normalised:
        return -2
    for position, (phrase, _term) in enumerate(menus._PHRASE_INDEX):
        if menus._contains_phrase(normalised, phrase):
            return position
    return -1


async def _parity(page) -> bool:
    """Run MY corpus through the page's matcher and compare with Python's."""
    print("\n2. PARITY CONTROL -- the two matchers, over MY OWN strings")
    result = await page.evaluate(
        _JS_MATCHER,
        {
            "mode": "parity",
            "corpus": _PARITY_CORPUS,
            "phrases": _PHRASES,
            "maxChars": menus.MAX_LABEL_CHARS,
            "groups": [],
            "overlaps": [],
        },
    )
    js = list(result.get("verdicts") or [])
    disagreements = []
    for position, text in enumerate(_PARITY_CORPUS):
        expected = _python_index(text)
        if position >= len(js) or js[position] != expected:
            disagreements.append(position)
    print("      corpus size            %d" % len(_PARITY_CORPUS))
    print("      disagreements          %d" % len(disagreements))
    if disagreements:
        # The INDEX, not the string -- the habit is the point even here.
        print("      disagreeing positions  %r" % disagreements)
        print("    REFUSED. Two implementations of one rule have diverged, so")
        print("    no classification below would mean anything. Nothing else")
        print("    is read.")
        return False
    print("      the two matchers agree on every case, including the two that")
    print("      convicted the first version of the Python one.")
    return True


async def _run(page) -> None:
    print("\n1. BEFORE THE SPEND")
    landed = await BROWSER.goto(page, FEED_URL)
    if "/login" in landed or "/checkpoint" in landed:
        print("    AUTH WALL. Nothing measured, nothing spent.")
        return
    msg_pair, inv_pair, furniture = await _read_both_badges(page)
    msg_count, msg_state = msg_pair
    inv_count, inv_state = inv_pair
    print("      messaging  new_since_last_visit=%r state=%r" % msg_pair)
    print("      invitation pending=%r state=%r" % inv_pair)

    if msg_state != "read" or inv_state != "read":
        # A REFUSAL THAT REPORTS ONLY WHAT IT DID NOT MATCH IS HALF A
        # MEASUREMENT. Three rounds were lost in this project to exactly that.
        # So the refusal prints the FURNITURE COUNTS it did see, which is what
        # separates "not signed in" from "signed in and the badge reader is
        # aimed wrong" -- two failures that print an identical None.
        print("    WHAT WAS THERE INSTEAD (counts only, no strings):")
        for name, value in furniture:
            print("      %-28s %r" % (name, value))
        print("    REFUSED. A badge that did not read is not a zero, and a")
        print("    load whose cost cannot be certified at BOTH ends does not")
        print("    get taken. Nothing was spent.")
        return
    if msg_count:
        print("    REFUSED. Something has arrived since his last visit, so the")
        print("    conversation LinkedIn redirects into may be UNREAD. Opening")
        print("    it marks a real person's message read. Nothing was spent.")
        return

    print("\n1a. THE SPEND -- one navigation to config.MESSAGING_URL")
    _SPENT.append(1)
    thread_landed = await BROWSER.goto(page, MESSAGING_URL)
    print("    redirected into a conversation: %r"
          % ("/messaging/thread/" in thread_landed))

    arrival = await dom.read_thread_reply_surface(page)
    print("    elements on the page: %r" % arrival.get("elements"))
    print("    settle verdict:       %r" % arrival.get("settle"))
    if arrival.get("settle") == "unrendered":
        print("    STOP. The page did not render; every count below is a fact")
        print("    about that and not about LinkedIn.")
        return

    if not await _parity(page):
        return

    # -----------------------------------------------------------------------
    # THE ENUMERATION IS TAKEN TWICE, WITH A SETTLE BETWEEN, AND BOTH ARE
    # PRINTED. This is THE RENDER GATE applied to a menu instead of a tab.
    #
    # This repository's standing finding is that a tabbed category's rows are
    # not in the document until its tab is pressed, so every "read zero" taken
    # from such a surface is a fact about the INSTRUMENT rather than the data.
    # A lazily-hydrated menu is the same shape one level down. A single pass
    # cannot tell "LinkedIn does not draw this" from "LinkedIn had not drawn it
    # YET", and those two answers retire opposite sets of rows.
    #
    # Two passes separated by a settle CAN tell them apart: a count that moves
    # is hydration, a count that does not is the surface. Neither pass is
    # privileged and both are reported -- an instrument that silently keeps the
    # second reading is one that has chosen its answer.
    # -----------------------------------------------------------------------
    print("\n3. THE ENUMERATION, PASS 1 (immediately on arrival)")
    first = await _enumerate(page)
    _report(first)

    await page.wait_for_timeout(3000)
    print("\n3a. THE ENUMERATION, PASS 2 (after a 3s settle)")
    second = await _enumerate(page)
    _report(second)

    print("\n3b. DID ANY COUNT MOVE BETWEEN THE PASSES?")
    moved = False
    for group_label, _selector in _GROUPS:
        before = ((first.get("tallies") or {}).get(group_label) or {}).get(
            "element_count"
        )
        after = ((second.get("tallies") or {}).get(group_label) or {}).get(
            "element_count"
        )
        if before != after:
            moved = True
        print("      %-24s %r -> %r%s"
              % (group_label, before, after, "   MOVED" if before != after else ""))
    print("      any movement: %r" % moved)
    print("      (no movement means these counts are about LinkedIn. Movement")
    print("       means the first pass was reading a page mid-hydration and")
    print("       every zero in it was void.)")

    await _report_overlaps(second)


async def _enumerate(page) -> dict:
    """One classification pass over every group, REDUCED TO PRIMITIVES AT THE
    BOUNDARY -- copied from ``_read_both_badges``'s own pattern in the
    predecessor probe, and the reason is the same one written there. NO LABEL
    CROSSES, and by the time this function returns, nothing downstream ever
    touches the page-evaluate result object either: every group's tally is
    already computed HERE, into plain integers and this module's own
    closed-vocabulary strings (a VOCABULARY term, a REFUSALS reason, or an
    ``_BANDS`` name), so a printer handed this return value cannot reach
    anything the page wrote even if a future edit hands it the whole thing.

    **WHY THIS CHANGED, AND IT IS NOT TO CLEAR A RED BY RENAMING.** The first
    version of this function returned the raw JS-evaluate object and let the
    printers tally it themselves. ``test_page_text_is_never_printed`` refused
    that file on 12 sites, and every one was the SAME mechanism ``196394d``
    and ``_read_both_badges`` already document in this package: **the taint
    engine tracks a name ACROSS THE WHOLE MODULE, not per scope.** ``result``
    was ``_parity``'s own local (bound from ``page.evaluate``) and,
    unrelatedly, was also the printer's parameter name; ``groups``,
    ``record``, ``name`` and ``control`` were locals and loop targets derived
    from it and reused the same way one function over. None of those sites
    ever actually held a raw label -- ``menus.tally`` and
    ``_verdict_to_classification`` already reduced everything to counts and
    vocabulary strings before this rewrite -- but a rename alone would have
    been the laundering this repository has a scar for: the fixed point
    follows the binding, not the meaning, so a name that merely LOOKS
    unrelated to a page read is not evidence that it is. The honest fix is to
    stop handing a printer a page-derived object at all, and only then rename
    what is left so nothing here can collide with ``_parity``'s locals again.

    THE CONTAINER-BUILDING SHAPE IS DELIBERATE TOO. Each group's reduced
    record is appended to a plain list of ``(label, record)`` pairs and the
    final mapping is built with ``dict(...)`` at the end, rather than
    assigned item-by-item into a dict that already exists
    (``tallies[group_label] = ...``). A subscript-assignment target is
    walked for tainted names on BOTH sides -- the container and the key --
    so writing into an existing dict by key would have tainted the group
    label itself and reopened exactly the collision this function exists to
    close. Appending to a list touches no name the label could collide with.
    """
    raw_pass = await page.evaluate(
        _JS_MATCHER,
        {
            "mode": "enumerate",
            "corpus": [],
            "phrases": _PHRASES,
            "maxChars": menus.MAX_LABEL_CHARS,
            "groups": [[group_label, selector] for group_label, selector in _GROUPS],
            "overlaps": [[n, a, b] for n, a, b in _OVERLAP_PAIRS],
        },
    )

    tally_pairs = []
    for group_label, _selector in _GROUPS:
        entry = (raw_pass.get("groups") or {}).get(group_label) or {}
        pending_shapes = list(entry.get("shapes") or [])
        tallied = menus.tally(
            _verdict_to_classification(int(v), pending_shapes)
            for v in (entry.get("verdicts") or [])
        )
        tally_pairs.append((group_label, {
            "element_count": entry.get("count"),
            "items": tallied["items"],
            "matched": tallied["matched"],
            "terms": tallied["terms"],
            "refused": tallied["refused"],
            "unmatched_shapes": tallied["unmatched_shapes"],
        }))

    overlap_pairs = []
    for overlap_label, _a, _b in _OVERLAP_PAIRS:
        entry = (raw_pass.get("overlaps") or {}).get(overlap_label) or {}
        overlap_pairs.append((overlap_label, {
            "set_a": entry.get("a"),
            "set_b": entry.get("b"),
            "shared": entry.get("shared"),
        }))

    return {"tallies": dict(tally_pairs), "overlaps": dict(overlap_pairs)}


def _report(passes: dict) -> bool:
    """Print one pass. Returns False when the firing control did not fire.

    Takes the ALREADY-REDUCED mapping ``_enumerate`` returns -- integers and
    this module's own vocabulary strings, never the page-evaluate result --
    and its own local names are chosen to share nothing with ``_parity``'s or
    ``_enumerate``'s. See ``_enumerate``'s docstring for why that emptiness is
    the property being protected here, not a style preference.
    """
    by_group = passes.get("tallies") or {}
    control_count = (by_group.get("CONTROL button") or {}).get("element_count")
    print("      CONTROL button count: %r" % control_count)
    if not control_count:
        print("    STOP. The role reader is dead; every zero below is void.")
        return False

    for group_label, _selector in _GROUPS:
        one = by_group.get(group_label) or {}
        print("\n    %s   count=%r" % (group_label, one.get("element_count")))
        print("      items %r   matched %r"
              % (one.get("items"), one.get("matched")))
        for vocabulary_term, term_count in (one.get("terms") or {}).items():
            print("        %-22s %d" % (vocabulary_term, term_count))
        if one.get("refused"):
            print("      refused: %r" % one.get("refused"))
        for shape_label, shape_count in (one.get("unmatched_shapes") or {}).items():
            print("        UNMATCHED %-38s %d" % (shape_label, shape_count))
    return True


async def _report_overlaps(passes: dict) -> None:
    """THE TWELVE-VERSUS-TWELVE QUESTION, ANSWERED BY ELEMENT IDENTITY."""
    print("\n4. THE TWELVE-VERSUS-TWELVE QUESTION, BY ELEMENT IDENTITY")
    for overlap_label, one in (passes.get("overlaps") or {}).items():
        print("      %s" % overlap_label)
        print("        set A (role=menuitem)        %r" % one.get("set_a"))
        print("        set B (label contains React) %r" % one.get("set_b"))
        print("        SHARED ELEMENTS              %r" % one.get("shared"))
    print("      (two sets of equal size sharing NOTHING are two different")
    print("       sets -- which is what an equal count cannot tell you, and")
    print("       is the whole reason this is an intersection and not a pair")
    print("       of tallies.)")


async def main() -> None:
    print("=" * 72)
    print("MESSAGING MENU ENUMERATION -- labels classified IN THE PAGE")
    print("=" * 72)

    # THE SESSION CONTEXT MANAGER YIELDS THE PAGE ITSELF, and it holds the
    # single-flight call lock for the whole run. Copied from the predecessor
    # probe rather than re-derived: several waves share this browser and two
    # navigations racing on one account is what the rate discipline exists to
    # prevent.
    async with BROWSER.session() as page:
        try:
            await _run(page)
        finally:
            # THE PAGE, NEVER THE CONTEXT. Closing the context would end his
            # signed-in session. Leaking the page is what degraded attach for
            # a whole fleet on 2026-09-05.
            try:
                await page.close()
                print("\n    page closed: %r" % page.is_closed())
            except Exception as exc:  # noqa: BLE001
                print("\n    page close failed: %s" % type(exc).__name__)
            print("    /messaging/ loads taken this run: %d" % len(_SPENT))
            print("    presses: 0   sends: 0   types: 0")


if __name__ == "__main__":
    asyncio.run(main())
