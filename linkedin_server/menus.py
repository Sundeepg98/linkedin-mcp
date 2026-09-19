"""A menu enumerator that publishes TERMS FROM A CLOSED VOCABULARY AND NO LABELS.

THIS IS A RULING BEING IMPLEMENTED. The ruling it implements is the one the
``messaging-rows`` wave asked for and could not make for itself
(``_audit/2026-09-05-messaging-rows.md`` section 7):

    "The cheapest single open item is now the 12-versus-12 question -- whether
    the 12 ``role=menuitem`` elements and the 12 ``React``-labelled controls
    are the same twelve. It needs the menu items' labels on a live
    conversation, so it needs a ``/messaging/`` load AND A RULING ABOUT
    READING LABELS ON THAT SURFACE."

That wave's standing rule was **no page string enters the process** -- not
redacted, not shaped -- and it was right to hold it. A conversation page is a
third party's correspondence in full. ``shape._CONVERSATION_ROW`` records what
a row's accessible name actually is: ``Select conversation with <a person>``.
So on this surface a LABEL IS A NAME, routinely, by LinkedIn's own design.

**THIS MODULE DOES NOT RELAX THAT RULE. IT KEEPS IT AND ENUMERATES ANYWAY.**

The move is to classify IN THE PAGE and return only the verdict. A label is
compared against a vocabulary of UI verbs written in this file, and what comes
back is the TERM THAT MATCHED -- one of this module's own literals -- never the
string it matched against. The page's text is never marshalled across the CDP
boundary, so it is not redacted, not shaped, and not present.

**THE OUTPUT ALPHABET IS CLOSED AND THAT IS THE SAFETY PROPERTY.** Every string
this module can emit is a literal defined below. That is structural in the same
sense ``groups.py`` is structural: a reader that is never handed a name cannot
leak one, and here a reader that can only emit its own constants cannot emit a
page's. A filter has to keep up with what LinkedIn serves tomorrow; a closed
output alphabet does not. ``test_menus.py`` asserts the alphabet over
adversarial input rather than trusting this paragraph.

## NO LABEL IS A PARAMETER OF ANY PUBLISHING FUNCTION IN THIS MODULE

Copied deliberately from ``groups.py``, including the reason. ``classify`` is
the one function that sees a label at all, it is pure, and it returns a term or
a refusal. Everything a caller actually publishes goes through ``tally``, whose
parameter is a list of CLASSIFICATIONS -- never a list of labels. The signature
is asserted in the tests, because a property stated only in prose is the defect
this repository has recorded more than once.

## WHY WORD-BOUNDED, AND WHY SOME TERMS ARE MULTI-WORD ONLY

**A BARE SUBSTRING MATCH IS THE SCAR THIS PACKAGE ALREADY WEARS.**
``writes._recipient_gate`` once used a bare ``indexOf`` and could have committed
a STRANGER to an irreversible message. Matching here is word-bounded for the
same reason, one level down.

The specific hazard on this surface is that a UI verb can also be a person's
name. ``Mark`` is the worked example: a single-word ``mark`` term would match a
conversation with a person called Mark. So the vocabulary carries
``mark as read`` / ``mark as unread`` and **never a bare ``mark``**. The same
reasoning keeps ``reply``, ``forward`` and ``copy`` -- all plausible surnames --
out of the single-word set unless they are paired with an object.

**NOTE WHAT A FALSE MATCH WOULD AND WOULD NOT COST, because the two are
different and only one of them matters here.** A label wrongly classified as
``delete_conversation`` publishes the string ``delete_conversation``, which is
mine and says nothing whatever about the person. **A misclassification is a
CORRECTNESS defect and cannot be a DISCLOSURE defect**, because disclosure is
closed off by construction rather than by the accuracy of this table. That is
the whole reason to put the closed alphabet underneath the vocabulary instead
of relying on the vocabulary being right.

## AN UNMATCHED LABEL IS REPORTED AS WHAT IT WAS, NOT ONLY AS A MISS

**A REFUSAL THAT REPORTS ONLY WHAT IT DID NOT MATCH IS HALF A MEASUREMENT.**
Three rounds were lost in this project to exactly that, and the rule is written
into ``groups.group_identifier`` beside this one. So an unmatched label comes
back with SHAPE FACTS -- a coarse length band, a token count, whether it carries
digits, whether every token is capitalised -- which is what distinguishes
"LinkedIn draws a verb this table has not learned" from "these are conversation
rows wearing people's names".

**THE SHAPE FACTS ARE DELIBERATELY LOSSY AND THERE IS NO DIGEST.** A hash of a
label would be a lookup table over a small domain wearing a redaction's
clothes -- ``groups.py`` rejected exactly that for group identifiers and the
reasoning transfers without change. Length is BANDED, never exact, because an
exact length over a known vocabulary is itself an identifier.

## IF YOU COPY THIS PATTERN, COPY ITS BOUNDARY OBLIGATIONS TOO

**ADDED 2026-09-19, BECAUSE THE PATTERN SPREAD AND THESE DID NOT TRAVEL WITH
IT.** Ship-the-vocabulary-in-and-get-integers-back is a good shape and it has
already been copied into another package module. Within hours that module put
the package's central guarantee into a red state, in two ways that have nothing
to do with whether the idea is sound:

1. **`page.evaluate` IS A SCANNED MUTATING CALL.** It is in
   ``readonly._MUTATION_CALL_PATTERNS`` deliberately -- injected code *could*
   mutate, so the scanner refuses to take anyone's word for it. A read-only
   harvester inside ``linkedin_server/`` must either carry a trailing
   ``# readonly-ok`` ON THE LINE WITH THE CALL, or earn an entry in
   ``readonly.SANCTIONED_MUTATIONS``. Note the placement: the scanner works
   line by line, so on a multi-line call the waiver belongs on the line
   carrying the call itself and nowhere else.

   **AND WRITING THIS PARAGRAPH TRIPPED THE SCANNER, WHICH IS THE POINT
   TWICE OVER.** The first draft spelled that call out with its leading dot
   and open bracket, and the scanner flagged THIS MODULE -- prose is matched
   line by line like anything else, and the skip rules cover comments,
   ``re.compile(`` lines and bare string literals but NOT docstring text.
   Caught by measuring the package straight after the edit rather than by a
   later gate. So: name these calls in prose without writing them in the form
   the scanner hunts for, and re-scan after documenting them.

2. **THE INJECTED JAVASCRIPT IS SCANNED SEPARATELY, BY A DIFFERENT TABLE.**
   ``readonly.JS_MUTATION_TOKENS`` refuses 24 tokens including ``innerHTML =``,
   ``setAttribute``, ``appendChild``, ``.value =``, ``fetch(`` and ``eval(``.
   **Parsing markup by assigning it into an element trips this**, even on a
   detached node that nobody can see -- and the guard is right to refuse it,
   because the argument that a node is detached is exactly the kind of thing
   that is true until somebody edits two lines above it. Read the DOM you were
   given; do not build one.

**THIS MODULE ITSELF TOUCHES NEITHER.** It is pure functions over strings
somebody else read, which is why it needs no waiver and appears in no sanction
-- and that is the property worth copying, not just the vocabulary trick. The
module that does the evaluating is the one that owes the boundary work, so
keeping the classifier free of the browser is what makes the obligation small
and obvious rather than diffuse.

## RULED 2026-09-19: DELIBERATELY UNWIRED. This is an INSTRUMENT, not a tool.

Nothing in the package imports this module, and that is the intended state
rather than an oversight. An import-graph audit found five reader modules with
no caller, and an orphan nobody has ruled on is how an unbanked backlog grows
by one -- so this paragraph is the ruling, attached to the module, where the
next audit will find it instead of a question.

**There is no operator-facing question it answers.** He wants rows, jobs and
capabilities. *"Classify the labels on this menu into UI verbs"* is something a
PROBE asks on the way to a measurement, never something he calls. Wiring it
would widen the tool surface permanently with a classifier nobody would invoke,
and **wiring something that should not be a tool is worse than leaving it
orphaned**, because the tool surface does not shrink again.

**And it is load-bearing for the press boundary specifically by staying
uncallable.** ``linkedin_server/press.py`` implements the disclosing-press
ruling, whose condition 2 is that a control is matched by ATTRIBUTE and never
by label text. This module is exactly what a caller must NOT reach for when
deciding what to press. Keeping it out of the tool surface keeps that boundary
obvious rather than a matter of discipline.

Its callers are ``scripts/_probe_messaging_menu_enumeration.py`` and
``tests/test_menus.py``, and nothing else. That is the shape it is meant to
have.

## WHAT THIS MODULE IS NOT

* It **does not open a page**, press a control, or touch a browser. It is handed
  classifications somebody else took.
* It **does not decide** whether an item may be clicked. Enumerating a menu is a
  read; clicking an item in it is not, and that boundary lives in
  ``readonly.SANCTIONED_MUTATIONS``, not here.
* It makes **no claim that the vocabulary is complete.** It cannot: the
  unmatched count exists precisely so that incompleteness is visible in the
  output rather than hidden by it.
"""
from __future__ import annotations

from typing import Any, Iterable, Mapping, Optional

#: THE VOCABULARY. Every string a caller can ever see as a ``term`` is a key
#: here, and these are the module's own literals rather than anything a page
#: supplied.
#:
#: Each entry maps a TERM to the phrases that select it. A phrase is matched
#: word-bounded and case-insensitively against the whole label. The matcher
#: sorts by length so that the MOST SPECIFIC phrase wins, which is what keeps
#: ``mark as unread`` from being decided by a shorter neighbour and what makes
#: the order of this table irrelevant to the result.
VOCABULARY: dict[str, tuple[str, ...]] = {
    # -- conversation-level, the CONVERSATION-OVERFLOW-MENU family -----------
    "delete_conversation": ("delete conversation", "delete this conversation"),
    "archive": ("archive", "unarchive", "move to archive"),
    "mark_read_state": ("mark as read", "mark as unread"),
    "mute": ("mute", "unmute", "mute conversation"),
    "report_conversation": ("report conversation", "report this conversation"),
    "star": ("star", "unstar", "remove star", "add star"),
    "move_folder": ("move to other", "move to focused", "move to inbox"),
    "leave_conversation": ("leave conversation", "leave this conversation"),
    "block_or_remove": ("block", "remove connection", "block and report"),
    "pin": ("pin", "unpin", "pin conversation"),
    # -- message-level, the PER-MESSAGE-OVERFLOW-MENU family ----------------
    "delete_message": ("delete message", "delete this message"),
    "edit_message": ("edit message", "edit this message"),
    "report_message": ("report message", "report this message"),
    "forward_message": ("forward message", "forward this message"),
    "copy_message": ("copy message", "copy text", "copy link to message"),
    "reply_to_message": ("reply privately", "reply to message", "quote reply"),
    "translate": ("translate", "see translation", "show original"),
    # -- MESSAGE-REACTION ---------------------------------------------------
    "react": ("react", "react to message", "add reaction", "remove reaction"),
    "reaction_emoji": (
        "like", "celebrate", "support", "love", "insightful", "funny",
        "curious", "thumbs up", "clap", "heart",
    ),
    # -- the filter rail, which is the one SANCTIONED click on this surface --
    "filter": (
        "focused", "other", "unread", "jobs", "connections", "inmail",
        "starred", "my connections", "drafts", "spam",
    ),
    # -- MESSAGE-REQUESTS-SURFACE, the thing row 50 is looking for ----------
    "message_requests": (
        "message requests", "message request", "requests",
        "invitations to connect",
    ),
    # -- composer furniture, present so it is NOT counted as an overflow item
    "compose": (
        "compose", "write a message", "new message", "start a conversation",
    ),
    "send": ("send", "send message"),
    "attach": (
        "attach", "attach a file", "add a photo", "add an attachment", "gif",
    ),
    "emoji_picker": ("emoji", "open emoji keyboard", "emoji keyboard"),
    # -- generic openers. These are TRIGGERS, not items, and are kept
    #    separate so a trigger is never tallied as a menu's contents.
    "overflow_trigger": ("more", "more options", "options", "open options"),
}

#: REFUSAL REASONS. The second half of the closed alphabet.
REFUSALS: tuple[str, ...] = (
    "no_label",
    "unmatched",
)

#: Length bands for an unmatched label. BANDED, NEVER EXACT -- an exact length
#: over a small known domain is itself an identifier.
_BANDS: tuple[tuple[int, str], ...] = (
    (0, "empty"),
    (1, "1-8"),
    (9, "9-20"),
    (21, "21-40"),
    (41, "41-plus"),
)

#: A label longer than this is not read further. An unbounded scan over
#: attacker-shaped input is a cost nobody chose, and every real UI verb on this
#: surface is far shorter.
MAX_LABEL_CHARS = 400

_WORD_CHARS = frozenset("abcdefghijklmnopqrstuvwxyz0123456789")


def _band(length: int) -> str:
    """The coarse length band for an unmatched label. One of ``_BANDS``."""
    chosen = _BANDS[0][1]
    for floor, name in _BANDS:
        if length >= floor:
            chosen = name
    return chosen


def _normalise(label: str) -> str:
    """Lowercase, and collapse every non-word character to a single space.

    Punctuation is collapsed rather than stripped so that ``Delete/Archive``
    cannot become the single token ``deletearchive`` and match neither.
    """
    out: list[str] = []
    previous_space = True
    for character in label.lower():
        if character in _WORD_CHARS:
            out.append(character)
            previous_space = False
        elif not previous_space:
            out.append(" ")
            previous_space = True
    return "".join(out).strip()


def _contains_phrase(haystack: str, phrase: str) -> bool:
    """Word-bounded match. NOT ``in``, and NOT the same rule at both lengths.

    ``haystack`` and ``phrase`` are both already normalised to space-separated
    word tokens, so a bounded match is an exact run of tokens. This is written
    as a token-window comparison rather than a regex because the scar it exists
    to avoid -- ``writes._recipient_gate``'s bare ``indexOf`` -- was a
    substring test, and a token window cannot silently decay into one.

    **A SINGLE-WORD PHRASE MUST BE THE WHOLE LABEL. A MULTI-WORD PHRASE MAY BE
    CONTAINED.** That asymmetry is not tidiness; it was forced by a measured
    defect and it is the difference between a table that works and one that
    quietly counts people as menu items.

    The first version applied containment at both lengths, and the smoke test
    that found it is now a test:

        classify("Star Anise")  -> term ``star``  (WRONG, and it shipped)

    **THE EXAMPLE IS A SPICE ON PURPOSE.** The defect was found with a
    plausible human full name, and the write-up originally carried it. It is a
    spice here because a tracked file may not carry a third party's name even
    as an illustration, and because the substitute has to demonstrate the same
    thing: two tokens, the first of which is a vocabulary term. A reader who
    needs the human case can supply it mentally; the file does not need to.

    The vocabulary had already been written to keep a bare ``mark`` out for
    exactly this reason -- a given name can be a UI verb -- and ``star`` walked
    in through the same door, because the hazard had been treated as a property
    of one WORD instead of a property of every single-word term. **A NAME ADDS
    TOKENS.** A real single-word menu item IS its label: a reaction picker's
    ``Like`` is the whole accessible name. So requiring equality costs nothing
    real and closes the class rather than the instance.

    Note what this does and does not fix, because the two get conflated. It
    fixes a COUNTING error. It was never a disclosure risk: the wrong branch
    emitted ``star``, this module's own literal, and a person's name cannot
    leave here under any branch. See the module docstring.
    """
    words = haystack.split()
    needle = phrase.split()
    if not needle or len(needle) > len(words):
        return False
    if len(needle) == 1:
        return words == needle
    for start in range(len(words) - len(needle) + 1):
        if words[start:start + len(needle)] == needle:
            return True
    return False


#: Phrases sorted longest-first, computed once. See ``VOCABULARY``.
_PHRASE_INDEX: tuple[tuple[str, str], ...] = tuple(
    sorted(
        (
            (phrase, term)
            for term, phrases in VOCABULARY.items()
            for phrase in phrases
        ),
        key=lambda pair: (-len(pair[0].split()), -len(pair[0]), pair[0]),
    )
)


def classify(label: Optional[str]) -> dict[str, Any]:
    """A label's TERM, or a refusal carrying what it saw. THE ONLY IMPURE EDGE.

    This is the single function in the module that is handed a label, it is
    pure, and **it returns no part of its input under any branch.** Callers that
    publish take ``tally``, whose parameter is a list of these verdicts.

    Returns one of::

        {"matched": True,  "term": <a VOCABULARY key>}
        {"matched": False, "refused": "no_label"}
        {"matched": False, "refused": "unmatched", "band": ..., "tokens": ...,
         "has_digits": ..., "all_capitalised": ...}

    The unmatched branch reports SHAPE and never content -- see the module
    docstring for why a digest was rejected and why the length is banded.
    """
    if label is None or not str(label).strip():
        return {"matched": False, "refused": "no_label"}

    raw = str(label)[:MAX_LABEL_CHARS]
    normalised = _normalise(raw)
    if not normalised:
        return {"matched": False, "refused": "no_label"}

    for phrase, term in _PHRASE_INDEX:
        if _contains_phrase(normalised, phrase):
            return {"matched": True, "term": term}

    tokens = raw.split()
    return {
        "matched": False,
        "refused": "unmatched",
        "band": _band(len(raw.strip())),
        "tokens": len(tokens),
        "has_digits": any(character.isdigit() for character in raw),
        # The tell that separates a UI verb from a person's name, and the
        # reason this branch exists at all rather than reporting a bare miss.
        "all_capitalised": bool(tokens) and all(
            token[:1].isupper() for token in tokens if token[:1].isalpha()
        ),
    }


def tally(classifications: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Count classified items. NO LABEL IS A PARAMETER OF THIS FUNCTION.

    THE SIGNATURE IS THE SAFETY PROPERTY, and ``test_menus.py`` asserts it on
    ``inspect.signature`` rather than trusting this sentence. A publishing
    function that is never handed a label cannot publish one, whatever LinkedIn
    draws tomorrow and whatever a later edit does to the vocabulary.

    ``items`` and ``matched`` are both reported and the difference is the
    point: a caller shown ``matched: 5`` out of twelve can see that seven were
    not understood, where a bare list of five terms reads identically whether
    seven were refused or none were offered.
    """
    terms: dict[str, int] = {}
    refused: dict[str, int] = {}
    shapes: dict[str, int] = {}
    items = 0
    for verdict in classifications:
        items += 1
        if verdict.get("matched"):
            term = str(verdict.get("term"))
            terms[term] = terms.get(term, 0) + 1
            continue
        reason = str(verdict.get("refused") or "unmatched")
        refused[reason] = refused.get(reason, 0) + 1
        if reason == "unmatched":
            # The shape summary, keyed by a string built ONLY from this
            # module's own band names and booleans.
            key = "{band}|tokens={tokens}|digits={digits}|caps={caps}".format(
                band=verdict.get("band"),
                tokens=verdict.get("tokens"),
                digits=bool(verdict.get("has_digits")),
                caps=bool(verdict.get("all_capitalised")),
            )
            shapes[key] = shapes.get(key, 0) + 1

    return {
        "items": items,
        "matched": sum(terms.values()),
        "terms": dict(sorted(terms.items())),
        "refused": dict(sorted(refused.items())),
        "unmatched_shapes": dict(sorted(shapes.items())),
    }


def emitted_alphabet() -> frozenset[str]:
    """Every string this module can ever emit as a term or a refusal.

    Exists so the closed-alphabet claim is CHECKABLE rather than argued. The
    test asserts that a tally over adversarial input -- including real-looking
    names -- emits nothing outside this set.
    """
    return frozenset(VOCABULARY) | frozenset(REFUSALS)
