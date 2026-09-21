"""Read the CONNECTION COUNTS off an organisation Page root. Integers only.

Census rows ``N 33`` -- *see how many of your connections work at an
organisation* -- and ``N 54`` -- *view how many of your connections follow a
Page* -- are one page load apart and have been GAP since the census was
written. The blocker they were filed under EXPIRED on 2026-09-20 when
``/company/<slug>/`` and ``/company/<numeric id>/`` were both admitted, and
what remained is stated in ``company_page.py``'s own docstring:

    **It opens nothing.** There is no page function here. The address is on
    the allowlist and no tool in this package navigates to it.

This module is the page function. ``company_page.py`` stays exactly as it is --
a vocabulary and a predicate that touches no page, which its own tests assert
by refusing any coroutine in it -- and the reading lives here, one import away.

## WHAT IS BUILT, AND WHAT IS STILL A GUESS. BOTH, PLAINLY

BUILT AND REVIEWABLE: the address is assembled by
``company_page.company_page_url`` from a NUMERIC organisation id, so this
package never assembles a slug; the navigation goes through the shipped read
gate; the page is reduced to integers inside the document; the screen-reader
copy of every line is stepped over and counted; and a phrase that does not
render is reported as ``phrase_not_drawn`` and NEVER as a count of zero.

STILL A GUESS, AND IT IS ONE CONSTANT: :data:`COUNT_PHRASES`. **Nobody in this
repository has opened a company Page** -- ``company_page.py`` says so in its own
last line -- so the exact words LinkedIn draws beside these two numbers are
unmeasured. The first live fire of this reader is therefore two measurements at
once: whether the count is there, and whether these are its words. That is why
the payload reports ``chunks`` and ``elements`` beside every verdict: a reader
that matched nothing on a page it could see and a reader that saw nothing at
all are different answers, and this repository has met the uninterpretable zero
often enough to refuse a fifth.

**A WRONG PHRASE COSTS A MISSING READING.** It cannot produce a NAME, because
no string from the document crosses the boundary at all -- that half is
structural and holds whatever the phrases say.

**THE OTHER HALF WAS OVERCLAIMED AND A COLD REVIEW CONVICTED IT**, which is
recorded here rather than quietly rewritten. This paragraph used to end *"it
cannot produce a wrong number, because a number is only published when a phrase
this package shipped was found word-bounded in a short line"*. That was false:
the reader took the FIRST digit run in the candidate line, so a line reading
*"50 people viewed, 11 connections work here"* published FIFTY -- word-bounded,
short, shipped phrase, wrong answer. The search now starts AT the matched
phrase and walks outward within :data:`dom.COUNT_LINES_MAX_NUMERAL_GAP`.

What is true now, stated at the width the code actually holds: a number is
published only when a shipped phrase matched word-bounded in a short line AND a
digit run sits within that bound of it, on the side a count renders. That is a
much better rule than the one it replaces and it is still a rule about markup
nobody here has seen.

## THE ACCESSIBLE COPY IS THE DANGEROUS ONE, AND IT IS HANDLED IN THE PAGE

Measured on the search card and recorded in ``dom.py``: LinkedIn draws the same
line twice, an ``aria-hidden`` visible span that is name-free beside a
screen-reader span that carries a person's name. ``textContent`` is
unconditional and takes both. ``dom.CARD_HIDDEN_SELECTOR`` is what this package
already knows those spans by and **it had never been wired to a reader that
assembles text**; ``dom.COUNT_LINES_JS`` is the first one, it steps over those
subtrees rather than deleting them, and it returns HOW MANY it stepped over so
the exclusion is an integer a caller can see rather than an assurance.

On this surface that is not hygiene. The Page root draws *"a module naming
employees the operator knows"* -- the allowlist entry's own words -- so the
screen-reader copy of the very line this reader is aimed at is the most likely
place on the page for a third party's name to sit.

## AN EXCEPTION IS NOT A RETURN VALUE

``int()`` writes the value it refused verbatim into its ``ValueError``, that
escapes to ``server._error``, and ``config.scrub`` substitutes this server's own
paths and nothing else -- a name has no shape to scrub. **Nothing here calls
``int()`` on anything the page chose.** Every field arrives through
``coerce.as_int``, which never raises and never quotes its input.

## THE SUBSTITUTION DEFAULT DECIDES WHAT SITS AT INDEX 0

``coerce`` substitutes a refused value with ``0`` and COUNTS the substitution.
For a position in a closed alphabet that means **index 0 is where garbage
lands**, so index 0 must be a class that is harmless to land on:
:data:`NUMERAL_SHAPES` opens with ``no_digit_run``, which publishes no number
at all. An alphabet with ``plain_digits`` first would have turned a refused
value into "trust this number", which is the flattering direction and the one
nobody would have looked at.

**AND A REFUSED MATCH IS DROPPED HERE, WHICH IS THE OPPOSITE OF WHAT
``coerce.counts_only`` DOES.** That law exists because several callers align
lists POSITIONALLY against a closed alphabet, where dropping one entry renames
every entry behind it. A match in this reader is SELF-DESCRIBING -- it carries
its own phrase position -- so dropping one renames nothing, and the count of
drops is published as ``matches_refused``. The law is followed where its reason
applies and departed from where its reason does not, which is the only honest
way to hold a rule.

## NO NAME, SLUG, ADDRESS OR ID IS A PARAMETER OF ANYTHING HERE

:func:`read_company_root` takes a page and the documented ``html`` control
path. :func:`connection_counts` takes a reading of integers and cannot be
handed a needle even by mistake. The one function that takes an identifier is
``company_page.company_page_url``, which lives in the other module, refuses
anything but ten ASCII digits, and reports a SHAPE rather than the value.

## IT FIRES NOTHING

No function here presses, submits or takes a confirm token. ``J 86`` ("I'm
interested") and ``N 47`` (follow from the Page) are the two writes on this
root and neither is touched; each still needs its own url, its own sanction
entry and its own ruling.
"""

from __future__ import annotations

from typing import Any, Iterable, Optional

from linkedin_server import coerce, dom

#: The two capabilities this reader serves, as a closed alphabet. Order is the
#: contract: :func:`kind_for` maps a position back to a literal.
COUNT_KINDS: tuple[str, ...] = (
    "connections_at_organisation",
    "connections_following_page",
)

#: ``(kind, normalised phrase)``, and the phrase is what is shipped INTO the
#: page. The page answers with a POSITION in this tuple and never with a
#: string, so the output alphabet is closed by construction.
#:
#: THE PHRASES ARE NORMALISED ALREADY -- lowercase, alphanumerics only, single
#: spaced -- because that is the form ``dom.COUNT_LINES_JS`` compares against.
#: ``tests/test_company_root.py`` asserts that property rather than a second
#: normaliser applying it, so there is no transform here to drift from the one
#: in the page.
#:
#: **NO PHRASE MAY CONTAIN ANOTHER**, asserted by the same test. Two phrases
#: where one contains the other match the same line and produce two readings of
#: one number, which would read as corroboration and is one observation.
#:
#: SINGULAR AND PLURAL ARE BOTH HERE because LinkedIn draws "1 connection works
#: here" and "11 connections work here" with different verbs, and a reader that
#: knew only the plural would report ``phrase_not_drawn`` for exactly the
#: account with one connection at an employer -- the case a job hunt cares
#: about most.
#:
#: **UNMEASURED. See the module docstring.** These are the shapes LinkedIn's
#: own help pages use for these two modules; no capture in this repository
#: holds a company Page, so the first live fire is what settles them. A wrong
#: phrase costs a missing reading, never a wrong number and never a name.
COUNT_PHRASES: tuple[tuple[str, str], ...] = (
    ("connections_at_organisation", "connections work here"),
    ("connections_at_organisation", "connection works here"),
    ("connections_at_organisation", "connections work at this company"),
    ("connections_following_page", "connections follow this page"),
    ("connections_following_page", "connection follows this page"),
    ("connections_following_page", "connections follow this company"),
)

#: THE CLOSED SHAPE ALPHABET FOR THE NUMBER BESIDE A PHRASE. Position 0 is a
#: REFUSAL on purpose -- see the module docstring on the substitution default.
#: Only ``plain_digits`` and ``grouped_digits`` carry a value.
#: ``percent_refused`` IS APPENDED RATHER THAN INSERTED, 2026-09-21. Order is
#: the contract -- a reading is a POSITION in this tuple -- so a new class goes
#: on the END or every reading ever taken is silently renamed. It exists
#: because a cold review found that ``%`` fell through the suffix check while
#: ``k``/``m``/``b`` did not: an asymmetry against this module's own rule that
#: a decorated number is refused rather than misread.
NUMERAL_SHAPES: tuple[str, ...] = (
    "no_digit_run",
    "plain_digits",
    "grouped_digits",
    "abbreviated_refused",
    "decimal_refused",
    "digit_run_too_long",
    "percent_refused",
)

#: The shapes a caller may read a number from. Everything else is a refusal
#: that names what it saw.
_SHAPES_WITH_A_VALUE = frozenset({"plain_digits", "grouped_digits"})

#: THE CLOSED VERDICT ALPHABET, one verdict per kind.
#:
#: ``reader_blind`` IS FIRST for the reason ``no_digit_run`` is first above:
#: it is the verdict that asserts nothing about the organisation, and it is
#: where a reading taken through a page that did not render belongs.
#:
#: ``phrase_not_drawn`` IS NOT A COUNT OF ZERO and is never reported as one.
#: A page that draws no such line, a page whose wording moved, and an account
#: with no connections there are three different worlds, and this reader can
#: separate the first two from a rendered page but not the third from either.
READING_STATES: tuple[str, ...] = (
    "reader_blind",
    "phrase_not_drawn",
    "numeral_refused",
    "disagreement",
    "count_read",
)


def phrases_shipped() -> list[str]:
    """The phrase list handed to the page, in :data:`COUNT_PHRASES` order.

    A LIST OF STRINGS THIS PACKAGE AUTHORED. It is the only thing that crosses
    into the document, and what comes back is a position in it.
    """
    return [phrase for _kind, phrase in COUNT_PHRASES]


def kind_for(position: int) -> str:
    """One phrase position -> the kind it serves. Out of range REFUSES.

    A clamp would silently rename one capability to another -- position 0 is
    ``connections_at_organisation`` -- so an out-of-range position is reported
    rather than folded onto the first entry.
    """
    if 0 <= position < len(COUNT_PHRASES):
        return COUNT_PHRASES[position][0]
    return "position_out_of_range"


def term_for(position: int) -> str:
    """One shape position -> one literal. Out of range REFUSES, never clamps."""
    if 0 <= position < len(NUMERAL_SHAPES):
        return NUMERAL_SHAPES[position]
    return "position_out_of_range"


def emitted_alphabet() -> frozenset[str]:
    """Every token this module can publish in a ``state`` or ``numeral`` field."""
    return (
        frozenset(COUNT_KINDS)
        | frozenset(NUMERAL_SHAPES)
        | frozenset(READING_STATES)
        | {"position_out_of_range"}
    )


def normalised(text: Optional[str]) -> str:
    """The page's own normalisation, in Python, FOR CHECKING CONSTANTS ONLY.

    **THIS IS NOT A SECOND MATCHER AND NOTHING CALLS IT ON PAGE TEXT.** The
    comparison that matters happens inside ``dom.COUNT_LINES_JS``, where the
    strings are. This exists so ``tests/test_company_root.py`` can assert that
    every shipped phrase is ALREADY in the form the page compares against --
    a static property of a constant, checked once, rather than a transform
    that could drift from the one in the document.
    """
    out: list[str] = []
    gap = False
    for character in str(text or ""):
        lowered = character.lower()
        if ("a" <= lowered <= "z") or ("0" <= lowered <= "9"):
            if gap and out:
                out.append(" ")
            gap = False
            out.append(lowered)
        else:
            gap = True
    return "".join(out)


async def read_company_root(page: Any, html: str = "") -> dict[str, Any]:
    """Find the shipped count phrases on the page. Returns INTEGERS ONLY.

    THE ONLY FUNCTION HERE THAT TOUCHES A PAGE. What crosses the boundary back
    is a list of matches whose every field is a number, plus four counters.

    ``html`` IS THE CONTROL PATH: supplied, it runs the same walk against a
    document parsed from that string rather than against the live page. It is a
    parameter of the READER and never of :func:`connection_counts`.

    **NOTHING HAS EVER RUN THAT BRANCH, AND THIS SENTENCE USED TO IMPLY
    OTHERWISE.** A cold review measured it: ``DOMParser`` is undefined under
    plain node, so the offline driver in ``tests/test_company_root.py`` always
    passes ``html=""`` and supplies a synthetic tree instead; and production
    never passes ``html`` at all. The two tests that touch
    :func:`control_fixture` check the MARKUP STRING, not a reading of it.
    **THE SAME IS TRUE OF EVERY SIBLING CONTROL FIXTURE IN THIS PACKAGE** --
    ``anchors``, ``search_results`` and ``collections_page`` all declare one
    and none is driven through a browser by any test. Exercising it needs a
    real engine, which is a browser slot this wave did not have. Recorded in
    `_audit/2026-09-21-the-three-readers.md` rather than left as an implied
    proof.

    ``matches_refused`` counts matches DROPPED because a field the page filled
    was not a number. It is normally 0; a nonzero is a FINDING and is reported
    as a count precisely because the value that caused it may be a name. See
    the module docstring for why dropping is correct here and wrong elsewhere.
    """
    raw = await dom.read_count_lines(
        page,
        phrases=phrases_shipped(),
        hidden=dom.CARD_HIDDEN_SELECTOR,
        html=html or "",
    )
    source = raw if isinstance(raw, dict) else {}
    scalars, scalars_refused = coerce.scalars_only(
        source,
        (
            ("elements", "elements"),
            ("chunks", "chunks"),
            ("chunks_capped", "chunks_capped"),
            ("hidden_subtrees_skipped", "hidden_skipped"),
            ("non_content_skipped", "non_content_skipped"),
        ),
    )

    raw_matches = source.get("matches")
    if isinstance(raw_matches, (str, bytes)) or not isinstance(raw_matches, Iterable):
        raw_matches = []

    matches: list[dict[str, int]] = []
    refused = 0
    for entry in raw_matches:
        row = entry if isinstance(entry, dict) else None
        if row is None:
            refused += 1
            continue
        position = coerce.as_int(row.get("phrase"))
        shape = coerce.as_int(row.get("shape"))
        value = coerce.as_int(row.get("value"))
        chars = coerce.as_int(row.get("chars"))
        if position is None or shape is None or value is None or chars is None:
            refused += 1
            continue
        matches.append(
            {"phrase": position, "shape": shape, "value": value, "chars": chars}
        )

    return {
        "elements": scalars["elements"],
        "chunks": scalars["chunks"],
        "chunks_capped": scalars["chunks_capped"],
        "hidden_subtrees_skipped": scalars["hidden_subtrees_skipped"],
        # SCRIPT, STYLE, TEMPLATE, NOSCRIPT, SVG, IFRAME, OBJECT and anything
        # wearing [hidden]. Counted apart from the screen-reader copy because
        # the two numbers answer different questions: one is the accessible
        # duplicate, the other is markup a browser never draws as text.
        "non_content_skipped": scalars["non_content_skipped"],
        "matches": matches,
        "matches_refused": refused,
        "values_refused": scalars_refused,
    }


def connection_counts(reading: Optional[dict[str, Any]]) -> dict[str, Any]:
    """One verdict per kind, from a reading of integers.

    **A NEEDLE HANDED HERE DOES NOTHING AND LEAVES NOTHING**, which is the
    accurate width of the property ``search_results.tally`` states about
    itself. A caller CAN pass a string -- Python has no way to stop it -- and
    what happens then is that the argument fails an ``isinstance`` check and
    every field inside it goes through ``coerce.as_int``, so it can neither be
    read nor echoed nor raised. That is a claim about behaviour rather than
    about the signature, and it is written this way because the previous
    wording ("cannot reach it even by mistake") was true of the signature and
    false of the mechanism: the argument RAISED on a bare string until a cold
    review drove one through it.

    Each entry in ``by_kind`` carries:

    ``state``    a literal from :data:`READING_STATES`
    ``value``    the integer, or ``None`` when no state publishes one
    ``numeral``  a literal from :data:`NUMERAL_SHAPES`, or ``None``
    ``why``      prose this module authored, with integers interpolated

    **``disagreement`` IS REPORTED AND NEVER RECONCILED.** Two phrases of one
    kind matching two different numbers means the page drew two count-shaped
    lines, and picking one would be this reader deciding which of LinkedIn's
    own lines it prefers. A caller gets the finding and both are withheld.
    """
    # ``isinstance`` BEFORE ``dict()``, AND A COLD REVIEW IS WHY. This read
    # ``dict(reading or {})``, which RAISES on a bare int, bool or string --
    # in a function whose own docstring says a needle cannot reach it. Every
    # FIELD was coerced and the ARGUMENT itself was not, which is the
    # coercion-leak class one layer shallower. No caller in this package can
    # reach it today; that is a fact about today's callers, not about the
    # function.
    seen = reading if isinstance(reading, dict) else {}
    elements = coerce.as_count(seen.get("elements"))
    chunks = coerce.as_count(seen.get("chunks"))
    capped = coerce.as_count(seen.get("chunks_capped"))
    skipped = coerce.as_count(seen.get("hidden_subtrees_skipped"))
    refused = coerce.as_count(seen.get("matches_refused"))

    raw_matches = seen.get("matches")
    rows = raw_matches if isinstance(raw_matches, list) else []

    per_kind: dict[str, list[dict[str, int]]] = {kind: [] for kind in COUNT_KINDS}
    for entry in rows:
        if not isinstance(entry, dict):
            continue
        position = coerce.as_int(entry.get("phrase"))
        shape = coerce.as_int(entry.get("shape"))
        value = coerce.as_int(entry.get("value"))
        if position is None or shape is None or value is None:
            continue
        kind = kind_for(position)
        if kind not in per_kind:
            continue
        per_kind[kind].append({"shape": shape, "value": value})

    by_kind: dict[str, dict[str, Any]] = {}
    for kind in COUNT_KINDS:
        by_kind[kind] = _verdict_for(
            per_kind[kind], elements=elements, chunks=chunks
        )

    return {
        "by_kind": by_kind,
        "elements_walked": elements,
        "chunks_considered": chunks,
        "chunks_capped": capped,
        # THE EXCLUSION AS AN INTEGER. A screen-reader copy of one of these
        # lines is the most likely place on this page for a third party's
        # name, and this number is how a caller sees that the walk stepped
        # over one rather than being told that it would.
        "hidden_subtrees_skipped": skipped,
        "non_content_skipped": coerce.as_count(seen.get("non_content_skipped")),
        "matches_refused": refused,
        "phrases_shipped": len(COUNT_PHRASES),
    }


def _verdict_for(
    entries: list[dict[str, int]], *, elements: int, chunks: int
) -> dict[str, Any]:
    """The verdict for one kind. Integers in, a literal and a why out."""
    if not entries:
        if elements <= 0:
            return {
                "state": "reader_blind",
                "value": None,
                "numeral": None,
                "why": (
                    "the walk visited no element at all, so this reading is a "
                    "fact about the READER and not about the organisation. A "
                    "page that had not hydrated, a session that is not signed "
                    "in and a restyle all land here."
                ),
            }
        return {
            "state": "phrase_not_drawn",
            "value": None,
            "numeral": None,
            "why": (
                "the walk considered %d line(s) across %d element(s) and none "
                "carried a phrase this package ships for this count. THIS IS "
                "NOT A COUNT OF ZERO. It means the line was not drawn, or "
                "LinkedIn words it differently from the unmeasured phrases in "
                "COUNT_PHRASES -- and no capture in this repository holds a "
                "company Page to settle which." % (chunks, elements)
            ),
        }

    usable = [
        entry
        for entry in entries
        if term_for(entry["shape"]) in _SHAPES_WITH_A_VALUE
    ]
    if not usable:
        shape = term_for(entries[0]["shape"])
        return {
            "state": "numeral_refused",
            "value": None,
            "numeral": shape,
            "why": (
                "the line rendered and the number beside it was refused as "
                "%s. An abbreviation is not rounded and a decimal is not read "
                "as a grouped run: a wrong number that looks right is worse "
                "than no number." % shape
            ),
        }

    values = {entry["value"] for entry in usable}
    if len(values) > 1:
        return {
            "state": "disagreement",
            "value": None,
            "numeral": None,
            "why": (
                "%d phrase(s) for this count matched lines carrying %d "
                "DIFFERENT numbers. Both are withheld: choosing one would be "
                "this reader deciding which of LinkedIn's own lines it "
                "prefers." % (len(usable), len(values))
            ),
        }

    chosen = usable[0]
    return {
        "state": "count_read",
        "value": chosen["value"],
        "numeral": term_for(chosen["shape"]),
        "why": (
            "one line carrying a shipped phrase rendered with a %s number "
            "beside it. The number is a COUNT and never a list -- nothing "
            "here reads who is counted, and the roster tab that would is "
            "refused by the read boundary." % term_for(chosen["shape"])
        ),
    }


#: THE CONTROL TREE, DEFINED ONCE AND RENDERED TWICE. ``(class, children)``,
#: where a child is a ``str`` (a text node) or another node.
#:
#: WHY IT IS A STRUCTURE RATHER THAN A STRING OF MARKUP. It is rendered to HTML
#: for :func:`control_fixture` -- the ``html`` control path, which needs a real
#: browser to parse -- AND to a node list for the offline driver in
#: ``tests/test_company_root.py``, which runs the SHIPPED script under V8 with
#: a synthetic tree because node has no DOM. Two hand-written copies of one
#: fixture is the drift this repository has paid for; one source rendered twice
#: cannot disagree with itself.
#:
#: **THE FIRST GROUP IS THE WHOLE POINT AND ITS SHAPE IS DELIBERATE.** The
#: screen-reader copy is SHORTER than the visible line and carries a DIFFERENT
#: number. Because the tightest phrase-bearing container wins, a walk that does
#: not step over that copy reads FORTY-ONE where the page says ELEVEN -- so the
#: exclusion changes the ANSWER here and not merely a counter. A fixture where
#: the hidden copy is longer would leave the skip looking decorative.
#:
#: Every name in it is synthetic and person-SHAPED on purpose: a fixture whose
#: hazard is spelled ``xxx`` does not exercise the hazard. The same reasoning
#: ``anchors.control_fixture`` gives for its slugs.
_CONTROL_TREE: tuple[Any, ...] = (
    "",
    [
        (
            "org-top-card",
            [
                (
                    "visually-hidden",
                    ["41 other connections work here"],
                ),
                "11 connections work here",
            ],
        ),
        (
            "org-follow",
            [
                ("", ["1,204 connections follow this page"]),
                (
                    "a11y-text",
                    ["Exampleone Markersurname and 9,999 others follow this page"],
                ),
            ],
        ),
        ("org-about", [("", ["2K connections follow this company"])]),
        ("org-rating", [("", ["1.5 connections work at this company"])]),
    ],
)


def _render_html(node: Any) -> str:
    klass, children = node
    inner = "".join(
        child if isinstance(child, str) else _render_html(child)
        for child in children
    )
    attribute = f" class='{klass}'" if klass else ""
    return f"<div{attribute}>{inner}</div>"


def control_fixture() -> str:
    """Markup that MUST match, and the screen-reader copy that must NOT win.

    Rendered from :data:`_CONTROL_TREE`; see that constant for why the tree is
    the source and this is one of its two renderings.
    """
    return "<html><body>" + _render_html(_CONTROL_TREE) + "</body></html>"


def control_tree() -> Any:
    """The same fixture as a nested ``(class, children)`` structure.

    For a driver that has no DOM to parse markup with. Returned rather than
    re-declared so the offline control and the in-page control are the same
    fixture -- see :data:`_CONTROL_TREE`.
    """
    return _CONTROL_TREE


def adversarial_trees() -> tuple[tuple[str, Any, int, str], ...]:
    """``(label, tree, expected value, expected shape)`` -- the shapes a cold
    review convicted, kept as a corpus so each is DRIVEN rather than described.

    **EVERY ROW HERE WAS A RED ONCE.** Four of them were defects in the first
    version of ``dom.COUNT_LINES_JS`` and two are the boundary either side of
    one of those defects, which is the half a red usually forgets: a rule that
    convicts everything is not discriminating, it is failing.

    The expected value is ``-1`` where no number may be published, so a row
    cannot accidentally assert "some number came back".

    Each tree is its own document, so one row cannot mask another -- the reader
    keeps ONE best match per phrase, and a corpus in a single tree would have
    let the easiest shape win every comparison.
    """
    return (
        (
            # THE WRONG NUMBER. Both numbers in one undivided text run, so the
            # tightest-container rule cannot separate them and the numeral has
            # to be found by its distance from the PHRASE.
            "two numbers, one text run",
            ("", [("card", ["50 people viewed, 11 connections work here"])]),
            11,
            "plain_digits",
        ),
        (
            # THE MISSING READING. The phrase alone in a child, the number
            # outside it: the shorter match carries no number, so preferring
            # it on length alone published numeral_refused for a page a human
            # reads at a glance.
            "phrase in a child, number in the parent",
            ("", [("card", ["11 ", ("txt", ["connections work here"])])]),
            11,
            "plain_digits",
        ),
        (
            "number and phrase in sibling elements",
            ("", [("card", [("num", ["11 "]), ("txt", ["connections work here"])])]),
            11,
            "plain_digits",
        ),
        (
            # A PERCENTAGE IS NOT A COUNT.
            "a percentage",
            ("", [("card", ["11% connections work here"])]),
            -1,
            "percent_refused",
        ),
        (
            # THE FIRST BOUNDARY EITHER SIDE OF THE DISTANCE RULE. A number
            # far enough away belongs to another clause and must NOT be
            # adopted -- if it were, the fix would be the old defect with a
            # longer reach.
            "a number beyond the gap is not adopted",
            (
                "",
                [
                    (
                        "card",
                        [
                            "50 people viewed this page last week and also "
                            "liked it, connections work here"
                        ],
                    )
                ],
            ),
            -1,
            "no_digit_run",
        ),
        (
            # THE SECOND BOUNDARY. A number AFTER the phrase is still its
            # number, because a count does not always render in front.
            "a number after the phrase",
            ("", [("card", ["connections work here: 11"])]),
            11,
            "plain_digits",
        ),
        (
            # NON-CONTENT IS STEPPED OVER. A browser draws none of this as
            # text, and a walk that reads it is reading markup as a line.
            "a script-shaped node is not read",
            ("", [("card", [("SCRIPT", ["11 connections work here"])])]),
            -1,
            "phrase_not_drawn",
        ),
    )


def control_expectations() -> dict[str, Any]:
    """What the shipped reader MUST say about :func:`control_fixture`.

    Written down beside the fixture so the offline driver and any future live
    control assert the same thing rather than each deciding what "correct"
    means. ``connections_at_organisation`` is ELEVEN and not forty-one -- that
    single number is the whole accessible-copy property.
    """
    return {
        "connections_at_organisation": {
            "state": "count_read",
            "value": 11,
            "numeral": "plain_digits",
        },
        "connections_following_page": {
            "state": "count_read",
            "value": 1204,
            "numeral": "grouped_digits",
        },
        "hidden_subtrees_skipped": 2,
    }
