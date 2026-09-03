"""GIVEN A CONTROL, WHAT DOES THIS PAGE SAY PRESSING IT DOES.

That question is the one every click ruling in this package has turned on, and
it has never had an instrument that could answer it. ``set_open_to_work`` is
this resolver's FIRST CALLER, not its purpose: the surface registry below is
one entry long today and the mechanism knows nothing about open-to-work.

---

## The four readers that came before, and why each could not answer

Naming them is not throat-clearing. Each failed for a DIFFERENT structural
reason, and a fifth instrument that does not say which of those four reasons it
escapes is just the fifth guess.

    dom.read_sdui_actions      A FIXED WINDOW either side of a needle, counted
                               in the page. It over-counts on purpose and says
                               so -- an over-wide window attributes a
                               neighbour's ServerRequest and refuses a click
                               that was safe, which is the direction to be
                               wrong in. It cannot attribute; it bounds.

    the TALLY                  ``_probe_open_to_work_payload._count_vocabulary``
                               counts the whole payload. There is no control in
                               a whole-payload count, so there is no
                               attribution in one either.

    the ENCLOSURE reader       The smallest balanced ``{...}`` around the label.
                               LIVE: 297 characters, balanced, ZERO action
                               kinds. Not a bug -- SDUI defines actions in their
                               own chunks and REFERENCES them, so the object
                               enclosing a label does not contain its actions.
                               Enclosure is the wrong RELATION on this page and
                               widening the window only swallows neighbours.

    the COMPONENTKEY follower  label -> the key of the component carrying it ->
                               every other place that key appears. LIVE: no
                               ``componentkey`` in any of the four objects
                               enclosing the label, in any of four spellings.
                               Its own refusal text names the answer: *the
                               flight row's ``$L<n>`` pointers are a DIFFERENT
                               relation, not a bigger number here.*

**THIS IS THAT DIFFERENT RELATION**, and the live refusal above corroborates it
rather than contradicting it: finding no key within four enclosing levels is
exactly what a page wiring its components by ``$L`` would produce.

## The relation, as the census recorded it

React Server Components serialise as a FLIGHT STREAM: a sequence of rows, each
``<hexid>:<json>``. A parent does not embed a child, it NAMES one -- the string
``$L<hexid>`` stands where the child goes, and the child is the row with that
id. ``_audit/_slice-otw-census.md`` line 243 records the shape verbatim on this
very page::

    component : div role="menu" ..., children [$L153, $L154, $L155]

and its table at lines 301-303 resolves all three to their own rows, each
carrying a ``legacyControlName``, a label and an action list. **The census
followed this relation by hand, off files that had to be destroyed.** So the
mechanism is not a hypothesis: it is a measurement with no instrument behind
it, which is the same debt ``_probe_open_to_work_payload.py`` was built to pay
one relation over.

## THE REFERENCE POINTS BOTH WAYS, AND THE FIRST CUT OF THIS FILE WALKED IT
## THE WRONG WAY

Worth recording, because the mistake is the design.

The obvious reading of "follow the reference from the label" is: the control
names a row, that row holds its actions. Call it SHAPE A. **The census
recorded SHAPE B instead** -- the label and its actions are in the SAME row,
and the reference points AT that row from its parent's ``children`` array. In
shape B, walking OUT from a label finds no ``$L`` at all, so a resolver built
only for shape A would refuse on the exact case the census resolved by hand.

So this reads BOTH directions and says which one answered::

    OUTGOING   a `$L` in the objects enclosing the label. Resolve it to its
               row; the kinds are there.                          (shape A)

    INCOMING   the label's HOME ROW is itself named by a `$L` somewhere else.
               That is the LICENCE to read the home row as one component: a
               lazily referenced row is addressed as a unit, where a main-tree
               row is a page section whose kinds belong to the section.
                                                                  (shape B)

**AND IT ATTRIBUTES ONLY WHEN EXACTLY ONE OF THE TWO IS AVAILABLE.** They are
naturally exclusive -- a main-tree slab has no incoming reference, a lazy chunk
has no outgoing one -- so both firing means the page is doing something neither
model covers, and two mechanisms each claiming to be the attribution is
precisely where a script must not choose.

**WITHOUT THE INCOMING LICENCE THE HOME ROW'S KINDS ARE NOT COUNTED AT ALL**,
only its size. A wider relation printed beside a refusal gets read as the
answer, which is the cap-raised-until-it-agrees failure wearing a different
hat.

## EVERY OCCURRENCE IS READ, AND THEY MUST AGREE

The predecessor's locator refuses on anything but exactly one occurrence,
because picking one of several would be attribution by document order. **On
this page that rule cannot answer for ``Edit``**: it is escaped TWICE, measured
live, and the census says why -- a control's definition appears "once per
rendering variant", and ``Edit``'s own action was resolved at two offsets,
681922 and 682537.

So each occurrence is resolved INDEPENDENTLY and the readings must AGREE.
On one occurrence that is the old rule exactly. On two it either agrees --
and the agreement is its own evidence, two independent readings of one control
-- or it REFUSES naming the disagreement. **Nothing is ever attributed by
document order**, which is the property the old refusal was protecting, so
this is a stricter instrument rather than a relaxed one.

``_locate_label`` keeps the old behaviour unchanged so the differential below
still holds; the multi-site path is a separate ``_locate_all``.

## What this emits

ACTION KINDS FROM A FIXED SET, THEIR COUNTS, AND THE ORDER THEY OCCUR IN.
Plus counts OF STRUCTURE: how many rows each anchor found, how many ``$L``
references sit at each enclosing level, how many rows a reference resolved to,
and how many characters each region ran to.

**NO ID EVER LEAVES THIS FILE.** Not a componentkey, not a row id, not the
``$L`` token that names one. A row id is an index into a stream and is almost
certainly harmless -- but "almost certainly" is a judgement about a string read
OUT of his payload, and the moment one is emitted the safety story stops being
*this instrument holds nothing* and becomes *this instrument holds something
and guards it*. Those are different claims and only the first survives an edit.
The rule is asserted over the RENDERED LINES rather than over the dicts,
because a transcript is a publication channel and the dicts are intermediates.

## Deliberately NOT shared with the probe it is a variant of

``scripts/_probe_open_to_work_payload.py`` holds a locator and an enclosure
walk this file re-implements. Sharing them would be the better structure in the
abstract and is refused here for two reasons that both point the same way: a
GENERAL resolver must not depend on a SPECIFIC probe, and that probe is
committed and being gated -- extracting primitives out of it is an edit to
somebody else's freeze.

**SO THE DUPLICATION IS PAID FOR WITH A DIFFERENTIAL RATHER THAN AN
INSPECTION.** ``tests/test_sdui_action_resolver.py`` asserts that this file's
``_occurrences``, ``_enclosing_object`` and ``_locate_label`` return answers
IDENTICAL to the probe's on one corpus. "Identical walk-out, identical
refusals" is then a claim that fails and names its divergence, instead of a
sentence somebody read once. That is this repository's own finding about prose
claiming a relationship in the code (section 90) applied before the prose was
written.

## The bounds, unchanged from the instrument this varies

**PASSIVE OBSERVATION ONLY.** ``page.on("response")``. No ``page.route``: it
cannot read a body without ``fetch``-and-``fulfil``, which is the REWRITE the
bound forbids, and the count of that call is asserted at zero. ``.on`` has no
channel through which it could modify anything, so the bound is met by not
holding the capability rather than by guarding it.

**ONE URL, BY EQUALITY, ESTABLISHED BEFORE THE LISTENER EXISTS.** Two passes:
the first resolves ``/in/me/`` and reads nothing, the second compares against
that exact string. The read allowlist matches ANY member's profile, which is
correct for its job and useless as a self-ownership test.

**NO OUTPUT PATH.** None, and no constant that could become one. A probe that
cannot write cannot leak.

**REFUSE RATHER THAN GUESS**, on zero matches and on many. Every failure below
is a NAMED refusal, and the names are the diagnostic: this reader cannot print
the payload, so which refusal comes back is the only way a human learns what
shape LinkedIn's markup actually has.

**FOUR ENCLOSING LEVELS, AND THE CAP IS NOT RAISED.** The widening was
considered and declined on 2026-09-03 with its reasoning recorded in
``aff8368``: past level four the enclosing object IS the carousel, so a
reference found there belongs to the container. A cap raised until it returns
something is not a measurement.

## And it is expected to fail

Three instruments have already said "the next one might answer this." If ``$L``
also cannot attribute, THAT IS THE ANSWER -- and it is a better one than a
fourth maybe, because it is the fourth independent mechanism to come back
empty on the same question. **Nothing here is tuned to produce agreement.**

Run:  python scripts/_probe_sdui_action_resolver.py [surface ...]
Writes NOTHING. Prints counts and action kinds, and never a url, a label
slice, an id, or a byte of payload.
"""
from __future__ import annotations

import asyncio
import bisect
import re
import sys
from pathlib import Path
from typing import Any, NamedTuple, Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import BASE_URL  # noqa: E402

#: The only address this asks for. ``/in/me/`` is on the read allowlist and
#: redirects to whoever is signed in, which is the property that makes it the
#: only profile spelling that cannot reach a third party.
SELF_PROFILE_URL = f"{BASE_URL}/in/me/"

#: NO OUTPUT DIRECTORY, and no path constant to become one later.


class Surface(NamedTuple):
    """One sanctioned reading: which controls, and which extra kind to count.

    ``extra_kinds`` exists so the RESOLVER stays general. The action kinds
    below are SDUI's own protocol vocabulary and mean the same thing on every
    page; ``saveAndFetchNextStepRequest`` is an open-to-work RPC and belongs to
    its caller. A resolver that knew that string would be a fourth open-to-work
    probe wearing a general name.
    """

    labels: tuple[str, ...]
    extra_kinds: tuple[str, ...]


#: THE SANCTIONED SURFACES, and the registry is the point rather than the
#: entries.
#:
#: A LABEL IS A LOCATOR AND A LOCATOR IS A SEARCH THROUGH HIS PROFILE. Taking
#: one from the command line would let a member's name be searched for in his
#: payload and echoed back in a heading, so labels are not accepted from argv:
#: argv selects a SURFACE KEY and the labels are written here.
#:
#: EVERY LABEL IS UI FURNITURE. ``Show details`` and ``Edit`` are LinkedIn's
#: own words on his own profile; neither can be a person, a company or an id,
#: which is what makes locating by them different in kind from locating by
#: anything else on this page. A test pins the set so a third locator has to be
#: argued for rather than added.
_SANCTIONED_SURFACES: dict[str, Surface] = {
    "open_to_work": Surface(
        labels=("Show details", "Edit"),
        # The RPC whose presence beside `Edit` is the whole of the August
        # finding about which of the two controls is dangerous.
        extra_kinds=("saveAndFetchNextStepRequest",),
    ),
}

#: SDUI's own action type names, and the closed set this may REPORT. Nothing is
#: read out of the payload: the region is asked how many times it contains each
#: of these fixed strings.
_SDUI_ACTION_KINDS: tuple[str, ...] = (
    "Navigate",
    "NavigateToScreen",
    "NavigateToUrl",
    "ServerRequest",
    "SetState",
    "ShowMenu",
    "CloseMenu",
)

#: How far out a balanced region may grow before the walk refuses.
_REGION_CAP = 20_000

#: How many enclosing objects out from the label an outgoing reference is
#: looked for.
#:
#: FOUR, AND DELIBERATELY NOT FIVE. Raising it was considered on 2026-09-03 for
#: the componentkey reader and declined, and the reasoning transfers unchanged:
#: past level four the enclosing object is the carousel, so a reference found
#: there is the container's and attributing the container's children to a
#: button inside it is the fixed-window failure reached by a longer route.
_REFERENCE_LEVELS = 4

#: A row larger than this is reported and REFUSED rather than counted.
#:
#: THIS NUMBER IS A BOUND, NOT A MEASUREMENT, and saying so is the point. A
#: flight row is the protocol's own unit and is legitimately larger than one
#: object -- but a row holding a tenth of a megabyte is a page section, and
#: kinds counted across a page section attribute the section rather than the
#: control. The reading always REPORTS the row's size, so a refusal here is
#: legible and a future ruling can re-argue the cap against a number instead of
#: re-guessing it.
_ROW_CAP = 100_000

#: How many occurrences of a label this will read independently before
#: refusing without reading any.
#:
#: TWO IS THE MEASURED SHAPE and this allows four. The census recorded a
#: control's definition appearing "once per rendering variant" -- ``Edit`` at
#: two payload offsets, the open-to menu items at three ids each -- so a
#: handful is measured behaviour on this page. Past that a label is furniture
#: repeated across the document rather than one control, and reading twenty
#: sites to compare them is a search for agreement.
_MAX_SITES = 4


# ---------------------------------------------------------------------------
# PRIMITIVES -- re-implemented rather than imported, and held to the probe's
# answers by a differential test. See the module docstring.
# ---------------------------------------------------------------------------


def _occurrences(payload: str, token: str) -> int:
    """How many times ``token`` appears AS A TOKEN, not as a substring.

    ``str.count`` matches substrings, so ``edit`` counts inside ``isEditFlow``,
    ``edited``, ``editor``, ``credit`` and ``editorial`` -- measured at SIX for
    a string containing one standalone ``edit``. Identifier boundaries on both
    sides, and integers out: a string in, a count back, and no path by which a
    character of his profile reaches a caller.
    """
    pattern = r"(?<![A-Za-z0-9_])" + re.escape(token) + r"(?![A-Za-z0-9_])"
    return len(re.findall(pattern, payload))


def _enclosing_object(payload: str, at: int) -> Optional[tuple[int, int]]:
    """The SMALLEST balanced ``{...}`` containing ``at``, or None.

    Structure rather than a byte window: a fixed window either clips a
    control's own region or swallows its neighbour's, and neither failure is
    visible in the output. It REFUSES rather than guessing, twice -- an
    unbalanced walk returns None, and so does a region grown past
    :data:`_REGION_CAP`.

    NAIVE ABOUT STRINGS, AND THAT IS DECLARED. A brace inside a quoted string
    counts. Its effect is to make the walk fail or the region grow, both of
    which refuse, so the error mode is a refusal rather than a wrong
    attribution.
    """
    depth = 0
    start = None
    for index in range(at, max(-1, at - _REGION_CAP), -1):
        char = payload[index]
        if char == "}":
            depth += 1
        elif char == "{":
            if depth == 0:
                start = index
                break
            depth -= 1
    if start is None:
        return None

    depth = 0
    for index in range(start, min(len(payload), start + _REGION_CAP)):
        char = payload[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return (start, index + 1)
    return None


def _label_spellings(payload: str, label: str) -> tuple[dict[str, int], str]:
    """The three spellings' counts, and which one this reader will locate by.

    ESCAPED FIRST, WITH THE QUOTED FALLBACK KEPT. The document is not a payload
    -- it is an HTML page WITH a payload inside it, and the two write a label
    differently::

        "Edit"        an HTML attribute, aria-label="Edit"   -> the DOM
        \\"Edit\\"      JSON inside a JS string literal        -> the payload

    So on a document carrying both, the QUOTED form is the DOM. A page serving
    plain unescaped JSON carries its payload quoted instead, so escaped-with-
    a-quoted-fallback is correct on both documents where quoted-first is
    correct on one.

    BARE IS NEVER USED TO LOCATE. In a payload this size a bare label matches
    prose -- ``Edit`` measured 27 bare on the live page, every ``Edit
    profile`` and ``Edit about`` on it -- and attributing actions to a prose
    match is the fixed-window failure wearing a different hat.
    """
    spellings = {
        "quoted": '"' + label + '"',
        "escaped": '\\"' + label + '\\"',
        "bare": label,
    }
    seen = {
        name: len(re.findall(re.escape(form), payload))
        for name, form in spellings.items()
    }
    chosen = "escaped" if seen["escaped"] else ("quoted" if seen["quoted"] else "")
    return seen, chosen


def _hits_for(payload: str, label: str, chosen: str) -> list[int]:
    """Offsets of every occurrence in the chosen spelling."""
    if not chosen:
        return []
    form = {"quoted": '"' + label + '"', "escaped": '\\"' + label + '\\"'}[chosen]
    return [m.start() for m in re.finditer(re.escape(form), payload)]


def _locate_label(payload: str, label: str) -> tuple[dict[str, Any], list[int]]:
    """Find ONE labelled control, or refuse. The predecessor's rule, unchanged.

    KEPT AS IT IS SO THE DIFFERENTIAL CAN HOLD. ``resolve`` uses
    :func:`_locate_all` instead, which reads every occurrence and requires the
    readings to agree -- see the module docstring for why that is a stricter
    rule rather than a relaxed one. This function exists so
    ``tests/test_sdui_action_resolver.py`` can assert, on one corpus, that this
    file's walk and the probe's walk return the same answers. Two locators that
    silently disagree about which bytes they describe is the failure that
    duplication is otherwise paid for with.

    A ZERO FROM A LOCATOR IS NOT EVIDENCE THE LABEL IS GONE. It is equally
    consistent with the locator being unable to see it, which is why all three
    counts are reported and a bare-only match refuses with that sentence.
    """
    seen, chosen = _label_spellings(payload, label)
    hits = _hits_for(payload, label, chosen)
    out: dict[str, Any] = {
        "label": label,
        "occurrences": len(hits),
        "spellings": seen,
        "located_by": chosen or None,
        "refused": None,
    }
    if not chosen and seen["bare"]:
        out["refused"] = (
            "the label appears %d time(s) BARE and never as a quoted or "
            "escaped JSON string, so this reader can see the text but not the "
            "action definition it belongs to. THAT IS A FACT ABOUT THIS "
            "READER, not about the page -- do not read it as the control "
            "having gone." % seen["bare"]
        )
        return out, []
    if len(hits) != 1:
        out["refused"] = (
            "zero occurrences -- the label is not on this page at all, which "
            "is the finding rather than a failure of this reader"
            if not hits
            else (
                "%d occurrences, so this cannot say WHICH control it would be "
                "describing. Picking the first would be attribution by "
                "document order." % len(hits)
            )
        )
        return out, []
    return out, hits


def _locate_all(payload: str, label: str) -> tuple[dict[str, Any], list[int]]:
    """Find EVERY occurrence of a labelled control, or refuse.

    THE SAME SPELLING RULE, A DIFFERENT ARITY RULE. Zero occurrences and a
    bare-only match refuse exactly as they do above. What changes is that two
    or three occurrences are handed back to be read INDEPENDENTLY and compared,
    rather than refused unread -- because on this page they are the measured
    shape, not an ambiguity.
    """
    seen, chosen = _label_spellings(payload, label)
    hits = _hits_for(payload, label, chosen)
    out: dict[str, Any] = {
        "label": label,
        "occurrences": len(hits),
        "spellings": seen,
        "located_by": chosen or None,
        "refused": None,
    }
    if not chosen and seen["bare"]:
        out["refused"] = (
            "the label appears %d time(s) BARE and never as a quoted or "
            "escaped JSON string, so this reader can see the text but not the "
            "action definition it belongs to. THAT IS A FACT ABOUT THIS "
            "READER, not about the page -- do not read it as the control "
            "having gone." % seen["bare"]
        )
        return out, []
    if not hits:
        out["refused"] = (
            "zero occurrences -- the label is not on this page at all, which "
            "is the finding rather than a failure of this reader"
        )
        return out, []
    if len(hits) > _MAX_SITES:
        out["refused"] = (
            "%d occurrences, past the %d-site ceiling, so none was read. The "
            "census measured a control's definition repeating once per "
            "rendering variant, which is a handful; a label appearing this "
            "often is page furniture repeated across the document rather than "
            "one control, and reading twenty sites to compare them is a "
            "search for agreement." % (len(hits), _MAX_SITES)
        )
        return out, []
    return out, hits


# ---------------------------------------------------------------------------
# THE FLIGHT STREAM: rows, and the references between them
# ---------------------------------------------------------------------------

#: What a row id may be made of. React serialises row ids with ``toString(16)``,
#: so lowercase hex, and the census's own recorded ids -- ``17a``, ``153``,
#: ``166`` -- are exactly that shape. Bounded at six characters because an
#: unbounded class on a megabyte of payload is how a "row id" becomes a
#: sentence.
_ROW_ID_CLASS = r"[0-9a-f]{1,6}"


def _row_header_patterns() -> dict[str, "re.Pattern[str]"]:
    """THREE ANCHORS FOR A ROW HEADER, and the third is the one nearly missed.

    Rows are newline-separated, so an anchor on the delimiter finds them --
    EXCEPT the first row of each chunk. The stream is served in pieces, one
    ``self.__next_f.push([1,"..."])`` per script tag, and a row beginning at a
    chunk boundary has an HTML tag before it rather than a newline. Anchoring
    only on the delimiter would make those rows INVISIBLE, and a reference
    resolving to one of them would come back "no such row" -- a fact about the
    reader reported in the grammar of a fact about the page, which is this
    family's oldest failure.

    THE ESCAPED ANCHOR REFUSES A DOUBLED BACKSLASH. Inside a JS string literal
    a stream newline is written ``\\n``; a literal backslash-n in the DATA is
    written ``\\\\n``. Without the lookbehind the second matches the first,
    which is *a discriminator must be a string that cannot appear inside
    another string you did not mean* -- the defect ``edit`` cost this family
    once already.
    """
    return {
        # Inside a JS string literal: backslash, 'n', then the header.
        "escaped newline": re.compile(r"(?<!\\)\\n(" + _ROW_ID_CLASS + r"):"),
        # A plain flight response, served as its own document.
        "literal newline": re.compile("\n(" + _ROW_ID_CLASS + "):"),
        # The first row of a chunk, which has no delimiter before it.
        "chunk start": re.compile(
            r"__next_f\.push\(\[\d+,\s*\\?\"(" + _ROW_ID_CLASS + r"):"
        ),
    }


_ROW_PATTERNS = _row_header_patterns()


def _reference_patterns() -> dict[str, "re.Pattern[str]"]:
    """The ``$L<hexid>`` patterns, quoted and escaped.

    Two spellings for the same two-axis reason the label has them: whatever
    spelling the label wears, its neighbours wear. A reader that knew only
    ``"$L153"`` would report "no references" on a document whose every
    reference is written ``\\"$L153\\"``, and those two answers look identical.
    """
    return {
        "quoted": re.compile(r"\"\$L(" + _ROW_ID_CLASS + r")\""),
        "escaped": re.compile(r"\\\"\$L(" + _ROW_ID_CLASS + r")\\\""),
    }


_REFERENCE_PATTERNS = _reference_patterns()


def _row_index(payload: str) -> dict[str, Any]:
    """Every row header in the document, by id, with the counts per anchor.

    ONE PASS, REUSED FOR EVERY LABEL. Building this per control would scan a
    megabyte once per label for no gain, and -- worse -- would let two readings
    in one run disagree about how many rows the document has.

    A ROW'S EXTENT IS UP TO THE NEXT HEADER, whichever anchor found that one.
    Mixing the anchors when sorting is deliberate: they are three ways of
    spotting the same thing, and a row cut short by a header its own anchor
    could not see would be a silent under-read.

    THE MEASURED EXTENT CAN BE TOO WIDE, AND THAT IS THE SAFE DIRECTION. A row
    spanning a chunk boundary swallows the ``"])</script><script>...`` markup
    between two pushes, so its character count is inflated and tokens from that
    markup could be counted. An over-wide region can only ADD kinds -- and this
    family has already ruled which way that error should lean: an over-wide
    read attributes a neighbour's ``ServerRequest`` and REFUSES a click that
    was safe, where a too-narrow one misses this control's own and PERMITS a
    click that sends. Those are not symmetric.

    RETURNS COUNTS AND OFFSETS. ``by_id`` is keyed by id for lookup inside this
    module; every consumer emits its VALUES' shapes and never its keys.
    """
    by_id: dict[str, list[int]] = {}
    anchors: dict[str, int] = {}
    starts: list[tuple[int, int, str]] = []  # (header start, content start, id)
    for anchor, pattern in _ROW_PATTERNS.items():
        found = list(pattern.finditer(payload))
        anchors[anchor] = len(found)
        for match in found:
            starts.append((match.start(), match.end(), match.group(1)))
    starts.sort()

    # A header found by two anchors at the same place is ONE row, not two.
    deduped: list[tuple[int, int, str]] = []
    for entry in starts:
        if deduped and deduped[-1][0] == entry[0]:
            continue
        deduped.append(entry)

    bounds: dict[int, tuple[int, int]] = {}
    id_at: dict[int, str] = {}
    for position, (_, content_start, row_id) in enumerate(deduped):
        end = (
            deduped[position + 1][0]
            if position + 1 < len(deduped)
            else len(payload)
        )
        bounds[content_start] = (content_start, end)
        id_at[content_start] = row_id
        by_id.setdefault(row_id, []).append(content_start)

    # EVERY REFERENCE IN THE DOCUMENT, ONCE. The incoming licence asks "does
    # anything else name this row", and answering it by scanning the whole
    # payload per site is a whole-document regex pass per control for an
    # answer that does not change between them.
    references: dict[str, list[int]] = {}
    reference_anchors: dict[str, int] = {}
    for spelling, pattern in _REFERENCE_PATTERNS.items():
        found = list(pattern.finditer(payload))
        reference_anchors[spelling] = len(found)
        for match in found:
            references.setdefault(match.group(1), []).append(match.start())

    return {
        "anchors": anchors,
        "rows": len(deduped),
        "distinct_ids": len(by_id),
        "by_id": by_id,
        "bounds": bounds,
        "id_at": id_at,
        "references": references,
        "reference_anchors": reference_anchors,
        # Sorted content starts, so the row containing an offset is a bisection
        # rather than a walk. It was a walk once, and the walk resolved each
        # row's id by scanning every id it knew -- quadratic in the row count,
        # invisible on a 300-character corpus and minutes on his profile. Found
        # by reading rather than by running, which is luck; the scale check
        # beside this file is the method.
        "order": [content_start for _, content_start, _ in deduped],
    }


def _row_holding(index: dict[str, Any], at: int) -> Optional[tuple[str, tuple[int, int]]]:
    """The id and bounds of the row an offset falls inside, or None.

    NONE IS A REAL ANSWER HERE. An offset before the first header is in the
    document's HTML rather than in the stream, and reporting that honestly is
    how a run distinguishes *the label is in the payload* from *the label is in
    the markup* -- the same distinction the locator's three spellings exist
    for, one layer down.
    """
    position = bisect.bisect_right(index["order"], at) - 1
    if position < 0:
        return None
    content_start = index["order"][position]
    best = (index["id_at"][content_start], index["bounds"][content_start])
    if not (best[1][0] <= at < best[1][1]):
        return None
    return best


def _references_in(region: str) -> tuple[set[str], dict[str, int]]:
    """Distinct ``$L`` ids in one region, and the per-spelling match counts.

    THE SET IS THE POINT. One id written through two spellings is one
    reference; two ids through one spelling are two references and this reader
    must not choose between them. So the ambiguity test is on the distinct
    VALUES, never on the number of matches.
    """
    values: set[str] = set()
    counts: dict[str, int] = {}
    for spelling, pattern in _REFERENCE_PATTERNS.items():
        found = pattern.findall(region)
        counts[spelling] = len(found)
        values.update(found)
    return values, counts


def _incoming_references(
    index: dict[str, Any], row_id: str, row: tuple[int, int]
) -> int:
    """How many times something OUTSIDE this row names it with a ``$L``.

    THE LICENCE TEST, AND THE WHOLE OF SHAPE B TURNS ON IT. A row that another
    row names is a lazily rendered COMPONENT -- addressed as a unit, delivered
    as a unit, and therefore attributable as a unit. A row nobody names is a
    slab of the main tree, and its action kinds belong to the page section it
    holds rather than to any control inside it.

    THE ROW'S OWN EXTENT IS EXCLUDED. A row that mentioned its own id would
    otherwise licence itself, which is a reader agreeing with itself.

    READS THE INDEX RATHER THAN THE PAYLOAD. Every reference in the document is
    found once when the index is built; asking the payload again per site is a
    whole-document regex pass for an answer that cannot have changed.
    """
    total = 0
    for position in index["references"].get(row_id, ()):
        if row[0] <= position < row[1]:
            continue
        total += 1
    return total


def _outgoing_reference(payload: str, at: int) -> dict[str, Any]:
    """Walk outward from a located label to the nearest object naming a row.

    STOPS AT THE FIRST LEVEL THAT NAMES ONE, which is the only defensible
    stopping rule and is the componentkey reader's, unchanged: an outer object
    that also names a reference names the child of something LARGER, and
    preferring the outer one attributes a carousel's children to a button
    inside it.

    MORE THAN ONE DISTINCT ID AT THE STOPPING LEVEL IS A REFUSAL, and the
    refusal names the reason rather than the count. Several ``$L`` ids in one
    object is the ``children`` array -- exactly the shape the census recorded
    at line 243 -- and a container's children are not one control's action.

    THE COMPONENTKEY READER'S MINIMUM-LENGTH FLOOR DOES NOT TRANSFER, and the
    difference is worth stating because dropping a guard usually is not. That
    floor existed because a short key is not addressing one control among
    thousands and following it through a megabyte matches prose. A ROW ID IS
    NOT AN IDENTIFIER AMONG THOUSANDS -- it is an index into a stream, so ``5``
    is a legitimate row and a length test would refuse a valid reading. The
    ambiguity it was protecting against moves instead to the caller, where an
    id matching several row headers refuses on the count of headers.

    PER-LEVEL COUNTS ARE RECORDED BEFORE EACH CHECK, so a refusal still
    reports the structure that produced it. "How many references, at which
    level" is the question this was built to answer, and a refusal that
    withholds its own evidence answers nothing.
    """
    out: dict[str, Any] = {
        "levels_walked": 0,
        "references_per_level": [],
        "reference_spellings": {spelling: 0 for spelling in _REFERENCE_PATTERNS},
        "reference_found": False,
        "reference_spelling": None,
        # WHY IT FAILED, AS A CODE RATHER THAN AS A SENTENCE. The caller has to
        # tell "several references, so refuse outright" from "no reference, so
        # try the other direction", and matching a substring of the refusal
        # PROSE to decide that would make an edit to the wording a change of
        # behaviour. That is the collapsed-state defect one layer along: the
        # reason has to be a value, or a test cannot name it.
        "reason": None,
        "refused": None,
        # The id travels as ``_id`` and is read explicitly by the one consumer
        # that needs it. Deliberately not under a name a renderer might loop
        # over.
        "_id": None,
    }
    region = _enclosing_object(payload, at)
    while region is not None and out["levels_walked"] < _REFERENCE_LEVELS:
        out["levels_walked"] += 1
        start, end = region
        values, counts = _references_in(payload[start:end])
        out["references_per_level"].append(len(values))
        for spelling, count in counts.items():
            out["reference_spellings"][spelling] += count
        if len(values) > 1:
            out["reason"] = "ambiguous"
            out["refused"] = (
                "%d DISTINCT row references inside the object at level %d, so "
                "this cannot say which one is this control's. That is the "
                "shape of a `children` array -- the census recorded one on "
                "this page -- and a container's children are not one "
                "control's action. Choosing would be attribution by document "
                "order." % (len(values), out["levels_walked"])
            )
            return out
        if values:
            out["reference_found"] = True
            out["_id"] = next(iter(values))
            out["reference_spelling"] = next(
                spelling for spelling, count in counts.items() if count
            )
            return out
        if start == 0:
            break
        region = _enclosing_object(payload, start - 1)
    if out["refused"] is None:
        out["reason"] = "none_found"
        out["refused"] = (
            "no outgoing row reference in any of the %d objects enclosing this "
            "label (walked %d, %s distinct per level)"
            % (
                _REFERENCE_LEVELS,
                out["levels_walked"],
                out["references_per_level"] or "none",
            )
        )
    return out


def _kinds_in(region: str, kinds: tuple[str, ...]) -> dict[str, Any]:
    """The closed vocabulary counted in one region, plus the ORDER it occurs in.

    THE ORDER IS PART OF THE BASELINE AND COSTS NOTHING TO REPORT. The census
    did not record "Edit fires SetState and ServerRequest", it recorded
    **SetState x2, THEN ServerRequest** -- a save preceded by two optimistic
    state writes. An unordered set drops the half of the finding that says
    which happens first.

    AND IT EMITS NO PAYLOAD. The sequence is this file's OWN fixed strings
    sorted by where each first occurs; the offsets are used and discarded and
    the strings were never read out of the region.
    """
    counts = {kind: _occurrences(region, kind) for kind in kinds}
    firsts: list[tuple[int, str]] = []
    for kind, count in counts.items():
        if not count:
            continue
        match = re.search(
            r"(?<![A-Za-z0-9_])" + re.escape(kind) + r"(?![A-Za-z0-9_])", region
        )
        if match:
            firsts.append((match.start(), kind))
    return {
        "kinds": counts,
        "sequence": [kind for _, kind in sorted(firsts)],
    }


def _resolve_one(
    payload: str,
    at: int,
    index: dict[str, Any],
    vocabulary: tuple[str, ...],
) -> dict[str, Any]:
    """One occurrence of a label, read through both directions of the relation.

    THE PRECEDENCE RULE IS THAT THERE IS NONE. Both mechanisms are computed,
    both are reported, and an attribution is made only when EXACTLY ONE of them
    is available. They are naturally exclusive -- a main-tree slab has no
    incoming reference and a lazy chunk has no outgoing one -- so both firing
    means the page is doing something neither model covers, and two mechanisms
    each claiming to be the attribution is precisely where a script must not
    choose.

    THE FLOOR, AND IT IS THE MOST IMPORTANT REFUSAL IN THIS FILE. ZERO OF
    EVERYTHING IS THE EXACT SHAPE OF PERMISSION: the operator ruled that a
    click measured to issue no ``ServerRequest`` is by effect a READ, so an
    all-zero reading is the thing that would authorise pressing a button on his
    live profile. An all-zero reading has two causes that look identical -- the
    control really has no actions, or THIS READER RESOLVED A REGION THAT DOES
    NOT CARRY ACTIONS. So it refuses, and the refusal is what makes every
    non-zero reading trustworthy: a run that reports kinds has demonstrated, on
    this payload, that it can see kinds through this relation.
    """
    out: dict[str, Any] = {
        "home_row_found": False,
        "home_row_chars": None,
        "incoming": None,
        "levels_walked": 0,
        "references_per_level": [],
        "reference_spellings": {},
        "outgoing_found": False,
        "outgoing_spelling": None,
        "outgoing_rows_named": None,
        "mechanism": None,
        "region_chars": None,
        "kinds": None,
        "sequence": None,
        "refused": None,
    }
    home = _row_holding(index, at)
    if home is None:
        out["refused"] = (
            "this occurrence sits OUTSIDE every flight row this reader can see "
            "-- before the first header, or in a stretch no anchor covers. It "
            "is in the document's markup rather than in the stream, so "
            "following a row reference from it would be following a reference "
            "the payload never made."
        )
        return out
    home_id, home_bounds = home
    out["home_row_found"] = True
    out["home_row_chars"] = home_bounds[1] - home_bounds[0]
    out["incoming"] = _incoming_references(index, home_id, home_bounds)

    walk = _outgoing_reference(payload, at)
    out["levels_walked"] = walk["levels_walked"]
    out["references_per_level"] = walk["references_per_level"]
    out["reference_spellings"] = walk["reference_spellings"]
    out["outgoing_found"] = walk["reference_found"]
    out["outgoing_spelling"] = walk["reference_spelling"]

    # --- which regions each mechanism offers, computed before either is used
    outgoing_region: Optional[tuple[int, int]] = None
    if walk["reference_found"]:
        named = [index["bounds"][s] for s in index["by_id"].get(walk["_id"], [])]
        out["outgoing_rows_named"] = len(named)
        if len(named) == 1:
            outgoing_region = named[0]
    elif walk["reason"] == "ambiguous":
        # SEVERAL REFERENCES IS A REFUSAL OUTRIGHT, not a reason to try the
        # other direction. The object enclosing this label names a handful of
        # rows, which is a container; falling through to the incoming licence
        # would answer a question about the container with a reading of the
        # label's row and call the pair a measurement.
        out["refused"] = walk["refused"]
        return out

    # THE INCOMING LICENCE. Exactly one other row naming this one: a component
    # delivered as a unit. Zero means a main-tree slab, whose kinds are the
    # section's. More than one means several parents share this row, and a row
    # shared between parents is not one control's.
    home_region = home_bounds if out["incoming"] == 1 else None

    if outgoing_region is not None and home_region is not None:
        out["refused"] = (
            "BOTH mechanisms are available on this occurrence -- the label's "
            "row is named by exactly one other row AND the objects enclosing "
            "the label name a row of their own. The two are meant to be "
            "exclusive, so this page is doing something neither model covers "
            "and choosing between them would be a guess wearing a reading's "
            "clothes. Both are reported above; neither is attributed."
        )
        return out

    if outgoing_region is not None:
        out["mechanism"] = "outgoing"
        region = outgoing_region
    elif home_region is not None:
        out["mechanism"] = "incoming"
        region = home_region
    else:
        out["refused"] = _no_mechanism_refusal(out, walk)
        return out

    out["region_chars"] = region[1] - region[0]
    if out["region_chars"] > _ROW_CAP:
        out["refused"] = (
            "the %s row runs to %d characters, past the %d-character cap. A "
            "row that large is a page section rather than one control, and "
            "kinds counted across it would attribute the section. The size is "
            "reported so this bound can be re-argued against a measurement "
            "rather than re-guessed."
            % (out["mechanism"], out["region_chars"], _ROW_CAP)
        )
        return out

    reading = _kinds_in(payload[region[0]:region[1]], vocabulary)
    if not any(reading["kinds"].values()):
        out["refused"] = (
            "the %s mechanism resolved to exactly one row and that row "
            "contains NOT ONE action kind from the closed set. This is NOT "
            "'the control has no actions' -- it is equally consistent with "
            "the row carrying markup rather than behaviour, which this reader "
            "could not tell apart. A zero from a reader that has not been "
            "shown returning non-zero on this same payload is not a "
            "measurement, and an all-zero reading is what would authorise a "
            "click." % out["mechanism"]
        )
        return out

    out["kinds"] = reading["kinds"]
    out["sequence"] = reading["sequence"]
    return out


def _no_mechanism_refusal(out: dict[str, Any], walk: dict[str, Any]) -> str:
    """Why NEITHER direction of the relation could attribute this occurrence.

    THE REFUSAL IS THE DELIVERABLE WHEN IT FIRES, so it names both halves
    separately. "No reference anywhere" and "a reference that resolves to no
    row" are different facts about LinkedIn's markup, and a refusal that
    collapsed them would remove the vocabulary this reading exists to produce.
    """
    if walk["reference_found"]:
        outgoing = (
            "the outgoing reference is MADE and names %d rows in this "
            "document. Zero means a stream can name a row that arrives later "
            "or never -- this document was read once, at one moment -- so it "
            "is not evidence the row does not exist, only that THIS reading "
            "cannot reach it. More than one means the id is ambiguous here."
            % out["outgoing_rows_named"]
        )
    else:
        outgoing = (
            "there is no outgoing reference in any of the %d objects "
            "enclosing the label (walked %d, %s distinct per level)"
            % (
                _REFERENCE_LEVELS,
                out["levels_walked"],
                out["references_per_level"] or "none",
            )
        )
    # REACHED ONLY WHEN THE INCOMING LICENCE FAILED, and that is structural
    # rather than incidental: a held licence produces a region, and a region
    # is attributed or refused on its own terms before this is called.
    incoming = (
        "and the label's own row is named by %d other row(s) rather than by "
        "exactly one, so it is a slab of the main tree rather than a component "
        "delivered as a unit -- its kinds would be the page section's"
        % out["incoming"]
    )
    return (
        "NEITHER DIRECTION OF THE RELATION ATTRIBUTES THIS OCCURRENCE: %s; %s. "
        "That is a fact about the page's shape, not about the control. It is "
        "the FOURTH independent mechanism to come back empty on this question, "
        "and four empty mechanisms is an answer rather than a prompt for a "
        "fifth." % (outgoing, incoming)
    )


def resolve(
    payload: str,
    label: str,
    index: dict[str, Any],
    *,
    extra_kinds: tuple[str, ...] = (),
) -> dict[str, Any]:
    """What this page says pressing ONE labelled control does.

    EVERY OCCURRENCE IS READ AND THEY MUST AGREE. See the module docstring:
    ``Edit`` is escaped twice on the live page and the census says why, so the
    predecessor's exactly-one rule cannot answer for it. Reading each site
    independently and requiring agreement keeps the property that rule was
    protecting -- nothing is attributed by document order -- while letting a
    control that the page renders twice be answered at all.

    SITES ARE DEDUPLICATED BY THEIR HOME ROW. Two occurrences inside one row
    are one place, not two, and counting them twice would turn a single
    reading into a self-agreeing pair.

    A DISAGREEMENT IS THE FINDING AND IS NOT TO BE SMOOTHED OVER. If ``Show
    details`` now carries a ``ServerRequest`` where the census counted none,
    this prints that and says nothing about what it means. Deciding is a ruling
    and rulings are not taken by scripts.
    """
    vocabulary = _SDUI_ACTION_KINDS + tuple(extra_kinds)
    out, hits = _locate_all(payload, label)
    out.update({"sites": [], "agreed": None, "kinds": None, "sequence": None})
    if out["refused"] or not hits:
        return out

    if not index["rows"]:
        out["refused"] = (
            "this document carries no flight row header that any of the %d "
            "anchors can see, so there is no row graph to walk. THAT IS A "
            "FACT ABOUT THIS READER AND THIS DOCUMENT TOGETHER: either the "
            "page is not server-rendered as a flight stream, or it writes its "
            "rows in a fourth way. It is not a statement that any control has "
            "no actions." % len(_ROW_PATTERNS)
        )
        return out

    seen_rows: set[tuple[int, int]] = set()
    for at in hits:
        home = _row_holding(index, at)
        if home is not None:
            if home[1] in seen_rows:
                continue
            seen_rows.add(home[1])
        out["sites"].append(_resolve_one(payload, at, index, vocabulary))

    readable = [site for site in out["sites"] if site["kinds"] is not None]
    if not readable:
        out["refused"] = (
            "no occurrence of this label could be attributed. Each site's own "
            "refusal is printed above and they are not necessarily the same "
            "refusal -- read them rather than this line."
        )
        return out
    if len(readable) != len(out["sites"]):
        out["refused"] = (
            "%d of %d sites were attributed and %d refused, so this reading is "
            "PARTIAL. It is refused rather than reported, because a site this "
            "reader could not read is exactly where the ServerRequest that "
            "would refuse a click might be, and a partial reading that comes "
            "back missing a kind is indistinguishable from a control that does "
            "not have it."
            % (
                len(readable),
                len(out["sites"]),
                len(out["sites"]) - len(readable),
            )
        )
        return out

    first = readable[0]
    out["agreed"] = all(
        site["kinds"] == first["kinds"]
        and site["sequence"] == first["sequence"]
        and site["mechanism"] == first["mechanism"]
        for site in readable
    )
    if not out["agreed"]:
        out["refused"] = (
            "%d sites resolved and they DISAGREE about what this control "
            "does. Each site's reading is printed above. That is the finding: "
            "either the page renders two different controls under one label, "
            "or this reader is describing two different things. Reporting "
            "either one would be attribution by document order." % len(readable)
        )
        return out

    out["kinds"] = first["kinds"]
    out["sequence"] = first["sequence"]
    return out


def render(found: dict[str, Any]) -> list[str]:
    """The lines a run prints for ONE control. Pure, so a test can read them.

    THE LEAK CHECK LIVES HERE RATHER THAN ON THE DICT. The dict is an
    intermediate; the LINES are what reaches a transcript, and a transcript is
    a publication channel. So the rendering has no side effects and
    ``tests/test_sdui_action_resolver.py`` asserts that no row id, no ``$L``
    token and no payload text ever appears in what it returns.
    """
    lines = [
        "    %r: %d occurrence(s)  spellings=%s  located_by=%r"
        % (
            found["label"],
            found["occurrences"],
            found["spellings"],
            found["located_by"],
        )
    ]
    for position, site in enumerate(found.get("sites") or []):
        lines.append("      site %d:" % position)
        if site["home_row_found"]:
            lines.append(
                "        home row: %d chars, named by %d other row(s)"
                % (site["home_row_chars"], site["incoming"])
            )
            lines.append(
                "          (its kinds are counted ONLY when exactly one other "
                "row names it -- a row nobody names is a slab of the main "
                "tree and its kinds are the page section's)"
            )
        if site["levels_walked"]:
            lines.append(
                "        walked %d level(s); distinct outgoing references per "
                "level: %s"
                % (site["levels_walked"], site["references_per_level"])
            )
            lines.append(
                "        reference spellings matched while walking: %s"
                % (site["reference_spellings"],)
            )
        if site["outgoing_found"]:
            lines.append(
                "        outgoing reference: level %d, spelling %r, naming %s "
                "row(s) (id withheld -- nothing read out of the payload is "
                "emitted)"
                % (
                    site["levels_walked"],
                    site["outgoing_spelling"],
                    site["outgoing_rows_named"],
                )
            )
        if site["mechanism"]:
            lines.append(
                "        mechanism: %s, region %s chars"
                % (site["mechanism"], site["region_chars"])
            )
        if site["refused"]:
            lines.append("        REFUSED: %s" % site["refused"])
            continue
        lines.append(
            "        kinds: %s"
            % ({k: v for k, v in site["kinds"].items() if v} or "none")
        )
        if site["sequence"]:
            lines.append("        order: %s" % " -> ".join(site["sequence"]))
    if found["refused"]:
        lines.append("      REFUSED: %s" % found["refused"])
        return lines
    lines.append(
        "      ATTRIBUTED, %d site(s) read independently and AGREEING:"
        % len(found["sites"])
    )
    lines.append(
        "        %s" % ({k: v for k, v in found["kinds"].items() if v} or "none")
    )
    if found["sequence"]:
        lines.append("        order: %s" % " -> ".join(found["sequence"]))
    return lines


def _surfaces_from(argv: list[str]) -> tuple[list[str], list[str]]:
    """Which sanctioned surfaces a run was asked for, and which names were not.

    AN UNKNOWN NAME IS REPORTED, NOT IGNORED. A typo that silently reads
    nothing looks exactly like a surface with nothing to say, and this family
    has already paid for one instrument that answered confidently about
    something it could not see.
    """
    if not argv:
        return sorted(_SANCTIONED_SURFACES), []
    wanted = [name for name in argv if name in _SANCTIONED_SURFACES]
    unknown = [name for name in argv if name not in _SANCTIONED_SURFACES]
    return wanted, unknown


async def main() -> None:
    wanted, unknown = _surfaces_from(sys.argv[1:])
    print("=== SDUI ACTION RESOLVER, LIVE")
    print("    given a control, what does this page say pressing it does")
    print("    writes nothing, prints no url, no id and no payload text\n")
    for name in unknown:
        print(
            "    NOT A SANCTIONED SURFACE: %r. Labels are not accepted from "
            "the command line -- a locator is a search through his profile, "
            "so they are written in the file and argued for there." % name
        )
    if not wanted:
        print(
            "    nothing to read. Sanctioned surfaces: %s"
            % ", ".join(sorted(_SANCTIONED_SURFACES))
        )
        return

    await BROWSER.start()
    async with BROWSER.session() as page:
        # --- PASS 1: establish the one url. Reads nothing. -------------------
        landed = await BROWSER.goto(page, SELF_PROFILE_URL)
        if "/login" in landed or "/checkpoint" in landed:
            print("    AUTH WALL. Not signed in, so nothing was measured.")
            await BROWSER.stop()
            return
        print("    pass 1: self-profile resolved (url withheld deliberately)")

        # --- PASS 2: the passive listener, bound to that one string ----------
        seen: list = []

        def _remember(response) -> None:
            """Collect the ONE document response for the resolved url.

            Synchronous and does no IO, so it cannot raise into Playwright's
            event loop. The body is read later, once, by the caller.
            """
            try:
                if response.url != landed:
                    return
                if response.request.resource_type != "document":
                    return
            except Exception:
                return
            seen.append(response)

        page.on("response", _remember)
        try:
            await BROWSER.goto(page, landed)
        finally:
            page.remove_listener("response", _remember)

        print(f"    pass 2: document responses matching that exact url: {len(seen)}")
        if len(seen) != 1:
            print("    REFUSED: expected exactly one. Zero means the response was")
            print("    served from cache or the url moved; more than one means this")
            print("    cannot say which document it would be reading. Nothing read.")
            await BROWSER.stop()
            return

        response = seen[0]
        print(f"    status: {response.status}")
        if response.status != 200:
            print("    REFUSED: a body read off a non-200 is not a measurement of")
            print("    the profile. Nothing read.")
            await BROWSER.stop()
            return

        try:
            payload = await response.text()
        except Exception as exc:
            print(f"    REFUSED: the body could not be read ({type(exc).__name__}).")
            print("    That is not an empty payload -- it is no reading at all.")
            await BROWSER.stop()
            return

        # ---- everything below counts and nothing below prints a slice -------
        print(f"\n    document characters: {len(payload)}")
        index = _row_index(payload)
        print("\n=== THE FLIGHT STREAM, AS THIS READER SEES IT")
        print("    Three anchors, counted apart. A row beginning at a chunk")
        print("    boundary has no newline before it, so an anchor on the")
        print("    delimiter alone would make those rows invisible and a")
        print("    reference into one would come back as 'no such row'.")
        for anchor, count in index["anchors"].items():
            print(f"      {count:6d}  headers found by the {anchor} anchor")
        print(f"      {index['rows']:6d}  rows after de-duplicating the anchors")
        print(f"      {index['distinct_ids']:6d}  distinct row ids")
        if not index["rows"]:
            print("      NO ROWS. Every reading below will refuse, and the")
            print("      refusal is about this reader and this document")
            print("      together -- not about any control.")

        for name in wanted:
            surface = _SANCTIONED_SURFACES[name]
            print(f"\n=== SURFACE {name!r}")
            for label in surface.labels:
                for line in render(
                    resolve(payload, label, index, extra_kinds=surface.extra_kinds)
                ):
                    print(line)
                print()

        # THE BODY IS DROPPED HERE. Not because a name going out of scope is a
        # security control -- it is not -- but because nothing above copied it
        # anywhere, nothing below reads it, and this script has no path to
        # write a file with. That is the actual property.
        del payload

        print("\n=== WHAT THIS DOES AND DOES NOT SETTLE")
        print("    It answers ONE question -- which action kinds this page")
        print("    attaches to a named control through the flight row graph --")
        print("    and it refuses rather than guessing at every step where it")
        print("    cannot. A refusal here is a fact about the page's shape or")
        print("    about this reader, and the refusal text says which.")
        print("    It does NOT make any action performable. It makes the")
        print("    measurement takeable before anybody presses anything.")

    await BROWSER.stop()


# GUARDED, for the reason ``_probe_messaging.py`` states at length: importing a
# script must not DO anything, and ``tests/test_scripts_are_import_safe.py``
# accepts an attribute call at module scope -- which ``asyncio.run(...)`` is. A
# probe ending in a bare one would launch a browser and drive his signed-in
# session on import. This one runs only when run.
if __name__ == "__main__":
    asyncio.run(main())
