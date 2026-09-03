"""Re-measure the Open To Work SDUI payload LIVE, and keep none of it.

WHAT THIS REPLACES AND WHY IT HAD TO BE REPLACED. The August analysis behind
``_audit/_slice-otw-census.md`` was taken by SAVING HIS PROFILE TO DISK and
reading the files: 1,177,077 characters, of which 1,091,238 -- 92.7% -- were
SDUI flight payload rather than DOM. That analysis is the whole basis for
``set_open_to_work``'s ``url_template=None``, and its verdict is stronger than
a capture accident: the open-to-work editor is not addressed by a url AT ALL.
It is fetched by an RPC named
``com.linkedin.sdui.requests.preferenceCollection.saveAndFetchNextStepRequest``
fired from a ``button[aria-label="Edit"]`` with no href.

THE PROBLEM WAS NEVER THE ANALYSIS. IT WAS THAT IT COULD NOT BE RE-TAKEN.
Those five files are his profile -- his name, his employer, his connections,
a third party's photo id -- so they could not be committed, and they were
destroyed. The measurement therefore has no instrument behind it: it is a
number in a document, and every month that passes it is a number about a page
LinkedIn has since changed.

THIS IS THAT INSTRUMENT, and the design constraint is the one that killed the
files: IT MUST BE ABLE TO ANSWER WITHOUT KEEPING ANYTHING.

---

## What it does NOT do, because the narrowest bound turned out to be narrower
## than the one asked for

THE BRIEF SAID REQUEST INTERCEPTION -- ``page.route`` scoped to one url,
``continue`` only, never abort, fulfil or rewrite. **This uses no interception
at all, and that is strictly narrower rather than a substitution.**

The reason is mechanical. With ``page.route`` the handler receives a ``Route``
and the body does not come with it; reading the body means
calling ``route.fetch`` and then ``route.fulfill`` with the result, which is
the REWRITE the brief forbids -- the response the browser renders would be one
this process handed it rather than one LinkedIn sent. There is no form of
``page.route`` that both reads a body and leaves the response untouched.
(Written without the call parentheses on purpose: ``readonly``'s mutation
scanner matches the CALL SYNTAX, and a docstring cannot carry the trailing
``# readonly-ok`` a code line would use. Prose about a call this file does not
make should not read as the call.)

``page.on("response")`` is PASSIVE. It observes what the browser already
received and has no channel through which to modify a request, a response, or
anything else -- so "never abort, fulfil or rewrite" is true BY CONSTRUCTION
here rather than by a check somebody has to keep running. The bound the brief
was reaching for is achieved by removing the mechanism that could violate it.

``.route`` is also on ``readonly._MUTATION_CALL_PATTERNS`` as a mutation kind
in its own right. ``.on`` is not, and correctly so.

## The four bounds, each argued

**ONE URL, COMPARED BY EQUALITY, KNOWN BEFORE THE LISTENER EXISTS.** This runs
TWO navigations rather than one. The first goes to ``/in/me/`` with no
listener attached and reads nothing at all; its only product is the LANDED
url, since ``/in/me/`` redirects to whoever is signed in. The second attaches a
listener that will read a body only for a response whose url is EXACTLY that
string, and navigates there again.

Why not one pass: a listener attached before the navigation cannot know which
url is his, and the allowlist cannot tell it -- ``^https://www\\.linkedin\\.com
/in/[A-Za-z0-9\\-_%]+/?$`` matches ANY member's profile, which is correct for
its own job and useless as a self-ownership test. A gate that would read a
stranger's profile document if the page ever landed on one is not a bound. So
the url is established first, by a pass that keeps nothing, and the second
pass compares against that one string. The cost is one extra load of his own
page, which is his and records nothing anywhere -- ``linkedin_who_viewed_me``
establishes that the durable-record cost belongs to loading OTHER people's
profiles.

**A CLOSED VOCABULARY, COUNTED. NO CAPTURED GROUP EVER LEAVES THE PAYLOAD.**
Every token below is a name LinkedIn's own protocol chose -- an action type, an
RPC id, a screen id, a tracking verb. None of them can be a member's name, a
company, a url or a message, because none of them is read OUT of the payload:
they are fixed strings written in this file and the payload is asked HOW MANY
TIMES it contains each. A regex with a capture group would be a different
instrument with a different safety story, and this one deliberately has none.

That is the same discipline ``dom.read_compose_modes`` uses on the message
composer, where the labels ARE his name: shape it where it lives and let a
count cross the boundary, rather than pulling the string across and guarding it
afterwards. A guard is one edit from being an absent guard; a design that never
holds the string is not.

**EXTRACT THEN DISCARD, AND THERE IS NOWHERE TO PUT IT ANYWAY.** The body is a
local inside one function, it is counted, and it is dropped. This script holds
NO output path -- following ``_probe_messaging.py``, whose docstring records
why: the version that had an ``OUT`` used it, and the captures had to be
destroyed by hand afterwards. A probe that cannot write cannot leak.

**NOTHING ABOUT HEADERS OR COOKIES ENTERS THIS PROCESS.** ``response.headers``,
``request.headers`` and ``context.cookies()`` are never referenced. Two
non-header fields are: ``request.resource_type``, to tell the main document
from the hundred subresources a LinkedIn page draws, and ``response.status``,
because a body read off a 302 or a 999 is not a measurement of anything and
reporting it as one would be worse than reporting nothing.

---

## What it can settle, stated narrowly, because it is narrower than the
## analysis it guards

THE TALLY IS A REGRESSION DETECTOR, NOT A RE-DERIVATION. The August analysis
attributed individual actions to individual controls by reading the payload's
structure around each ``componentkey``. A count cannot do that: it can say the
payload contains eleven ``Navigate`` tokens, and it cannot say which control
owns them.

THERE ARE NOW THREE READERS HERE, AND THE THIRD IS THE ONLY ONE THAT
ATTRIBUTES. They are kept together deliberately: one live read of his profile
answers all three, and the printout shows what each can and cannot say about
the same bytes.

    1  the TALLY          counts the closed vocabulary across the whole
                          payload. No control, so no attribution.
    2  the ENCLOSURE      smallest balanced object around a label. Live it
       reader             found a 297-character region holding ZERO action
                          kinds -- because SDUI defines actions in their own
                          chunks and REFERENCES them by ``componentkey``.
                          Enclosure is the wrong relation on this page.
    3  the REFERENCE      label -> that component's key -> every other place
       follower           the key appears -> the kinds in those objects. The
                          relation the payload actually uses.

Reader 3 is the first code in this file that reads a STRING out of the
payload, because a reference cannot be followed without holding the thing
referred to. The bound moves accordingly and is stated where it lives: one
capture group, its value never emitted, asserted over the RENDERED LINES. The
census measured one componentkey on this page as ``<vanity>_openToButton``, so
that rule is protecting a measured identifier and not a protocol string.

WHAT IT CAN SAY IS WHETHER THE VOCABULARY AND THE COUNTS STILL HOLD. If
``saveAndFetchNextStepRequest`` has vanished, or ``ServerRequest`` has appeared
where the census counted zero, or a screen id has been renamed, then the August
analysis is describing a page that no longer exists and the full reading has to
be re-taken by a human. That is the question this answers, and it is the
question that actually matters for a spec resting on a four-week-old capture.

**A DISAGREEMENT IS THE FINDING AND IS NOT TO BE SMOOTHED OVER.** August
recorded ``Show details`` as one ``Navigate`` with NO ``ServerRequest``, and
``Edit`` as the step that fires the save RPC. If the live counts do not fit
that picture, this prints the numbers and says so; it does not decide what they
mean. Deciding is a ruling, and rulings are not taken by scripts.

**AND IT DOES NOT MAKE ``set_open_to_work`` PERFORMABLE.** It restores the
ability to measure what a control does before anybody presses it. The press is
a separate ruling against a fresh reading.

Run:  python scripts/_probe_open_to_work_payload.py
Writes NOTHING. Prints counts, and never a url, a label or a slice of payload.
"""
from __future__ import annotations

import asyncio
import re
import sys
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import BASE_URL  # noqa: E402

#: The only address this script asks for. ``/in/me/`` is on the read allowlist
#: and redirects to whoever is signed in, which is the property that makes it
#: the ONLY profile spelling that cannot reach a third party.
SELF_PROFILE_URL = f"{BASE_URL}/in/me/"

#: NO OUTPUT DIRECTORY, and no path constant to become one later. See the
#: docstring: the instrument this replaces was a pile of files on disk.

#: THE CLOSED VOCABULARY. Fixed strings, written here, counted in the payload.
#:
#: EVERY ONE IS LINKEDIN'S OWN PROTOCOL NAME and none is read out of the page,
#: which is the whole safety argument: this script cannot emit a member's name
#: because it never extracts a string at all, it only counts strings it already
#: had. Grouped by what a change in each would mean.
_VOCABULARY: dict[str, tuple[str, ...]] = {
    # THE ACTION KINDS. The census read these off the payload's own
    # ``proto.sdui.actions.core.*`` type names.
    "action kinds": (
        "proto.sdui.actions.core.Navigate",
        "NavigateToScreen",
        "NavigateToUrl",
        "ServerRequest",
        "SetState",
        "ShowMenu",
        "CloseMenu",
    ),
    # THE RPC THAT IS THE WHOLE FINDING. The open-to-work editor is fetched by
    # this and by no url, which is why ``url_template`` is None. Its
    # disappearance or its appearance somewhere new is the single most
    # important thing this probe can report.
    "the editor RPC": (
        "com.linkedin.sdui.requests.preferenceCollection"
        ".saveAndFetchNextStepRequest",
        "saveAndFetchNextStepRequest",
        "isEditFlow",
        "SeekerPrefCollectionStepType_ENTRY_POINT",
    ),
    # THE SCREENS. Addressed by screenId rather than by url, which is the
    # architectural fact the verdict rests on.
    "screen ids": (
        "com.linkedin.sdui.flagshipnav.jobs.PrefCollectionDetailView",
        "PrefCollectionDetailView",
        "ProfileServicesEducation",
        "ProfileOpenToVolunteerEducation",
    ),
    # THE CARD'S OWN CONTROLS, by the ids the payload gives them.
    "open-to controls": (
        "opento_button_hiring",
        "opento_button_smp",
        "opento_button_otv",
    ),
    # THE TRACKING VERBS, which is how the census told a read-shaped control
    # from a state-changing one.
    "tracking verbs": (
        "clickThrough",
        "dismissMenu",
        "spcPrefDetailsDismissIcon",
        "edit",
    ),
    # THE WIZARD'S OWN SHAPE. These are why the census said "budget for N
    # screens, not 1", and a change here changes that estimate.
    "wizard shape": (
        "skipNextStepNavigation",
        "skipBackNavigation",
        "skipComplexBackNavigation",
        "fromDeleteConfirmationPrivateSetting",
    ),
}

#: WHAT THE CENSUS COUNTED, for the columns this probe can compare against.
#: Absent from this table means August did not count it in a form a live run
#: can be compared with, and the probe says "no baseline" rather than
#: inventing one.
_AUGUST: dict[str, int] = {
    # ``_slice-otw-census.md`` section 7: zero SDUI Navigate actions in the
    # pre-hydration payload carried a non-empty url for an OTW surface, and
    # section 3's table counted ServerRequest actions per file at 0/0/0/24/0.
    # Neither is a single number this probe reproduces, so neither is here.
    # These two ARE single numbers and they are the load-bearing ones.
    "occurrences of `opentowork` or `open-to-work`": 0,
    "occurrences of `psettings`": 2,
}

#: The two strings the census counted at zero across all five files. Kept
#: separate because a NON-zero reading here is the single cheapest signal that
#: LinkedIn has given the feature a url since August -- which would change the
#: verdict outright.
_ABSENT_IN_AUGUST: tuple[str, ...] = ("opentowork", "open-to-work")


def _occurrences(payload: str, token: str) -> int:
    """How many times ``token`` appears AS A TOKEN, not as a substring.

    THE DEFECT THIS EXISTS FOR, found on the FIRST LIVE RUN, 2026-09-02. The
    count was ``payload.count(token)``, and ``str.count`` matches substrings.
    The vocabulary contains ``edit``, so that count matched inside
    ``isEditFlow``, ``edited``, ``editor``, ``credit`` and ``editorial``, and
    reported 117 for a token that identifies nothing. MEASURED: a string
    containing ONE standalone ``edit`` counts SIX.

    IT IS THE THIRD INSTANCE OF ONE SHAPE IN A SINGLE DAY. The receipt work
    hit it as ``"saved"`` versus ``"saved list"`` -- ``apply_job``'s text
    contains ``the SAVED tab``, so ``saved`` fires on a CORRECT row -- and the
    general form is: **A DISCRIMINATOR MUST BE A STRING THAT CANNOT APPEAR
    INSIDE ANOTHER STRING YOU DID NOT MEAN.** Nothing in the act of writing a
    token tells you which kind you have written.

    SO THE FIX IS THE MECHANISM, NOT THE TOKEN. Dropping ``edit`` would have
    repaired one instance and left the next author to rediscover the class.
    Every token is now matched with identifier boundaries on both sides, so a
    short lowercase token counts only where it stands alone -- and
    :func:`_undiscriminating_tokens` reports which tokens the two methods
    disagree about, so the vocabulary can say whether it has any more.

    STILL INTEGERS OUT. The signature is the safety property: a string in, a
    count back, and no path by which a character of his profile reaches a
    caller.
    """
    pattern = r"(?<![A-Za-z0-9_])" + re.escape(token) + r"(?![A-Za-z0-9_])"
    return len(re.findall(pattern, payload))


def _count_vocabulary(payload: str) -> dict[str, dict[str, int]]:
    """Count each known token, by boundary rather than by substring."""
    return {
        group: {token: _occurrences(payload, token) for token in tokens}
        for group, tokens in _VOCABULARY.items()
    }


def _undiscriminating_tokens(payload: str) -> dict[str, tuple[int, int]]:
    """Tokens whose SUBSTRING count exceeds their TOKEN count, and by how much.

    THE VOCABULARY'S OWN CAN-IT-DISCRIMINATE CHECK, and it reports rather than
    refuses. A token the two methods disagree about is one that occurs inside
    larger words on this page -- which does not make it useless (the boundary
    count is still correct) but does mean the naive reading of it was noise,
    and whoever reads this run should know which numbers those were.

    IT IS A MEASUREMENT OF THE PAGE, not of the token in the abstract:
    ``edit`` is undiscriminating on a page full of ``editor`` and harmless on
    one without. So it is computed live rather than asserted at design time.
    """
    out: dict[str, tuple[int, int]] = {}
    for tokens in _VOCABULARY.values():
        for token in tokens:
            naive = payload.count(token)
            bounded = _occurrences(payload, token)
            if naive != bounded:
                out[token] = (naive, bounded)
    return out


def _unknown_action_kinds(payload: str) -> int:
    """HOW MANY distinct SDUI action type names are NOT in the vocabulary.

    A COUNT AND NOT THE NAMES, and the restraint is deliberate rather than
    timid. An action type name is LinkedIn's protocol vocabulary and would
    almost certainly be safe to print -- but "almost certainly" is a judgement
    about a string this process has not seen, and the whole design of this
    probe is that it never makes one. Printing them needs its own ruling; the
    count is enough to say "the protocol grew, go and look properly".
    """
    marker = "proto.sdui.actions.core."
    known = {
        token.rsplit(".", 1)[-1]
        for token in _VOCABULARY["action kinds"]
        if token.startswith(marker)
    }
    seen: set[str] = set()
    start = 0
    while True:
        found = payload.find(marker, start)
        if found < 0:
            break
        start = found + len(marker)
        tail = payload[start : start + 64]
        name = ""
        for char in tail:
            if char.isalnum() or char == "_":
                name += char
            else:
                break
        if name:
            seen.add(name)
    return len(seen - known)


#: THE TWO CONTROLS THE CLICK RULING TURNS ON, by the exact label each wears.
#:
#: THESE ARE UI FURNITURE, NOT NAMES. ``Show details`` and ``Edit`` are
#: LinkedIn's own words on his own profile; neither can be a person, a company
#: or an identifier, which is what makes locating by them different in kind
#: from locating by anything else on this page.
_CONTROL_LABELS: tuple[str, ...] = ("Show details", "Edit")

#: The action kinds that may be REPORTED for a located control. A closed set,
#: same rule as the tally: nothing is read OUT of the payload, the region is
#: asked how many times it contains each of these fixed strings.
_REPORTABLE_KINDS: tuple[str, ...] = (
    "Navigate",
    "NavigateToScreen",
    "NavigateToUrl",
    "ServerRequest",
    "SetState",
    "ShowMenu",
    "CloseMenu",
)

#: How far out a balanced region may grow before this refuses. A control's own
#: object is small; a region this large means the braces did not balance where
#: expected and the reader is about to attribute half the page to one control.
_REGION_CAP = 20_000


def _enclosing_object(payload: str, at: int) -> Optional[tuple[int, int]]:
    """The SMALLEST balanced ``{...}`` containing ``at``, or None.

    STRUCTURE RATHER THAN A BYTE WINDOW, and the difference is the whole
    reason this can attribute anything. A fixed window either clips a
    control's own actions or swallows its neighbour's, and neither failure is
    visible in the output -- it would report a number that looks exactly like
    a measurement. Walking out to a balanced pair follows the payload's own
    nesting, so the region either IS the control's object or the walk fails.

    IT REFUSES RATHER THAN GUESSING, twice: an unbalanced walk returns None,
    and so does a region that grows past :data:`_REGION_CAP`, because a region
    that large is not one control's object whatever the braces say.

    NAIVE ABOUT STRINGS, AND THAT IS DECLARED. A brace inside a quoted string
    counts here. In an SDUI payload that is rare and its effect is to make the
    walk fail or the region grow, both of which REFUSE -- so the error mode is
    a refusal rather than a wrong attribution, which is the direction to be
    wrong in. A quote-aware scanner would be a second parser to get subtly
    wrong for a page nobody has structurally re-read.
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


def _locate_label(payload: str, label: str) -> tuple[dict[str, Any], list[int]]:
    """Find ONE labelled control, or refuse. Shared by BOTH readers.

    EXTRACTED SO THE TWO READERS CANNOT DISAGREE ABOUT WHICH OCCURRENCE THEY
    ARE DESCRIBING. :func:`_actions_for` walks out to an enclosure and
    :func:`_actions_by_reference` follows a key, and if each had its own
    locator they could silently answer about different bytes -- which is the
    failure that would be hardest to see in a printout that shows both.

    Returns the shared skeleton and the hit positions. A refusal is already
    written into the skeleton when the hits are not exactly one.
    """
    # THREE SPELLINGS, COUNTED SEPARATELY, AND THE COUNTS ARE THE DIAGNOSTIC.
    #
    # THE FIRST RUN OF THIS READER REPORTED ``Show details``: 0 OCCURRENCES,
    # and a zero from a locator is NOT evidence the label is gone -- it is
    # equally consistent with the locator being unable to see it. Those are the
    # two answers that must never be conflated, and a single quoted-form search
    # cannot tell them apart.
    #
    # A Next.js flight payload carries JSON inside JS string literals, so a
    # label may appear as ``"Show details"``, as ``\\"Show details\\"``, or bare
    # in rendered DOM. Counting all three says WHICH, and a bare-only match
    # means the reader found the DOM text rather than the action definition --
    # which is a different thing and must not be attributed to.
    spellings = {
        "quoted": '"' + label + '"',
        "escaped": '\\"' + label + '\\"',
        "bare": label,
    }
    seen = {
        name: len(re.findall(re.escape(form), payload))
        for name, form in spellings.items()
    }
    # THE ESCAPED FORM FIRST, AND THE LIVE RUN OF 2026-09-03 IS WHY.
    #
    # THIS WAS QUOTED-FIRST, AND QUOTED-FIRST AIMS AT THE DOM. The document
    # this reads is not a payload -- it is an HTML page WITH a payload inside
    # it, and the two write a label differently:
    #
    #     "Edit"       an HTML attribute, aria-label="Edit"   -> the DOM
    #     \\"Edit\\"     JSON inside a JS string literal        -> the payload
    #
    # So on a document carrying both, THE QUOTED FORM IS THE DOM. Measured
    # live, and the census corroborates both halves exactly:
    #
    #     Edit           quoted 1, escaped 2, bare 27
    #                    quoted 1  == census: button[aria-label="Edit"],
    #                                 count 1, UNIQUE -- the DOM attribute
    #                    escaped 2 == census: Edit's action resolved at TWO
    #                                 payload offsets, 681922 and 682537
    #     Show details   quoted 0, escaped 1, bare 2
    #
    # Quoted-first therefore sent the reader at the HTML attribute, where
    # there is no JSON object at all -- and BOTH readers duly refused, one
    # with "no balanced object within 20000 characters" and the other with
    # "walked 0". Neither refusal was about the page. **A reader aimed at the
    # wrong half of a document reports a fact about itself in the grammar of a
    # fact about its subject**, which is this file's oldest lesson arriving
    # one layer along.
    #
    # WHAT THE FIX BUYS IS AN HONEST REFUSAL, NOT AN ANSWER, and that is worth
    # saying plainly rather than discovering as a disappointment: aimed at the
    # payload, ``Edit`` now finds its escaped form TWICE and refuses as
    # AMBIGUOUS. That is the correct outcome. Two payload occurrences and no
    # way to say which is the control means picking one would be attribution
    # by document order.
    #
    # THE FALLBACK IS KEPT, and it is not decoration: a page that served plain
    # unescaped JSON would carry its payload in the QUOTED form, and escaped
    # would be zero. Preferring escaped with a quoted fallback is correct on
    # both documents; preferring quoted is correct only on the second.
    #
    # Bare is never used to locate: in a payload this size a bare label matches
    # prose, and attributing actions to a prose match is the fixed-window
    # failure wearing a different hat. Live, ``Edit`` bare was 27 -- every
    # ``Edit profile``, ``Edit about`` and ``Edit default activity`` on the
    # page -- which is exactly the noise that rule exists for.
    chosen = "escaped" if seen["escaped"] else ("quoted" if seen["quoted"] else "")
    hits = (
        [m.start() for m in re.finditer(re.escape(spellings[chosen]), payload)]
        if chosen
        else []
    )
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


def _actions_for(payload: str, label: str) -> dict[str, Any]:
    """Which action kinds sit in the region ENCLOSING one labelled control.

    RETURNS COUNTS AND A REFUSAL REASON, never a slice of the payload. The
    region is located, the closed vocabulary is counted inside it, and the
    region itself is discarded -- exactly the tally's discipline applied to a
    smaller piece of the same document, which is why this needed no wider
    permission than the read that already holds the whole body in memory.

    REFUSES ON ANYTHING BUT EXACTLY ONE OCCURRENCE. Zero means the label is
    gone, which is itself the finding. More than one means this cannot say
    which control it would be describing, and picking the first would be
    attribution by document order -- the thing this package refuses everywhere
    else.

    AND ON THE LIVE PAGE IT ANSWERS NEITHER QUESTION, which is recorded here
    rather than only in the commit that found it: SDUI defines actions in
    their own chunks and references them by ``componentkey``, so the object
    enclosing a label does not contain that label's actions. Enclosure is the
    wrong relation on this page. :func:`_actions_by_reference` is the right
    one, and this stays because a reader that refuses is still evidence --
    it is what proves the actions are not where a structural reading would
    naturally look.
    """
    out, hits = _locate_label(payload, label)
    out["kinds"] = None
    out["region_chars"] = None
    if out["refused"] or not hits:
        return out

    region = _enclosing_object(payload, hits[0])
    if region is None:
        out["refused"] = (
            "no balanced object encloses this label within %d characters, so "
            "there is no region to attribute actions to. Refused rather than "
            "falling back to a fixed window, which would report a number that "
            "looks like a measurement." % _REGION_CAP
        )
        return out

    start, end = region
    out["region_chars"] = end - start
    out["kinds"] = {
        kind: _occurrences(payload[start:end], kind)
        for kind in _REPORTABLE_KINDS
    }
    # AND THE ONE RPC BY NAME, because its presence beside `Edit` is the whole
    # of the August finding about which control is dangerous.
    out["kinds"]["saveAndFetchNextStepRequest"] = _occurrences(
        payload[start:end], "saveAndFetchNextStepRequest"
    )
    return out


# ---------------------------------------------------------------------------
# THE REFERENCE-FOLLOWING READER
#
# THE THIRD INSTRUMENT AIMED AT ONE QUESTION, AND THE FIRST THAT CAN ANSWER
# IT. Two have already failed, and neither failed by being buggy:
#
#   the TALLY (:func:`_count_vocabulary`) counts the whole payload. It can say
#   the page holds eleven Navigate tokens and cannot say which control owns
#   one. A count is not an attribution and never was.
#
#   the ENCLOSURE reader (:func:`_actions_for`) takes the smallest balanced
#   object around the label. Live, that object was 297 characters, balanced,
#   and held ZERO action kinds -- because SDUI DEFINES ACTIONS IN THEIR OWN
#   CHUNKS AND REFERENCES THEM BY ``componentkey``. The object enclosing a
#   label does not contain its actions. Enclosure is the wrong RELATION on
#   this page, so no amount of widening the window fixes it: widening only
#   swallows neighbours.
#
# So the relation has to be followed rather than assumed: label -> the key of
# the component that carries it -> every other place that key appears -> the
# action kinds in those objects. That is what this does.
#
# WHAT IT COSTS, STATED FIRST BECAUSE IT IS THE REAL CHANGE. This is the ONLY
# code in this file that reads a string OUT of the payload. Everything else
# asks "how many times do you contain this fixed string I already had"; a
# reference cannot be followed without holding the thing referred to. So the
# key crosses into a local variable, and the bound moves from "no capture
# group exists" to "one capture group exists, its value is never emitted, and
# a test asserts that over the RENDERED LINES rather than over the dict".
#
# AND THE KEY IS NOT ASSUMED HARMLESS. The census measured the topcard
# button's key as ``<vanity>_openToButton`` -- a componentkey that carries his
# profile slug. Others are opaque uuids. So "never emit the key" is not
# fastidiousness about a protocol string: on this page one of the four known
# keys IS an identifier, and the rule exists because of that measurement.
# ---------------------------------------------------------------------------

#: The field that names a component's key, in every spelling this payload can
#: write it in.
#:
#: FOUR SPELLINGS, COUNTED SEPARATELY, AND THE RUN SAYS WHICH MATCHED. That is
#: the locator's own lesson applied one level down, and it was earned: the
#: first version of :func:`_locate_label` searched ONE spelling, got zero, and
#: would have reported "the label is gone" when the truth was "this reader
#: cannot see it". A key reader that searched only ``"componentkey":"..."``
#: could report "no key" on a payload whose every key is written
#: ``\"componentKey\":\"...\"``, and the two answers look identical.
#:
#: The escaped pair is not hypothetical. A Next.js flight payload carries JSON
#: inside JS string literals, which is exactly why the label had to be looked
#: for in an escaped form too -- and the label WAS found escaped on the live
#: page. Whatever spelling the label wears, its neighbours wear.
_KEY_FIELD_NAMES: tuple[str, ...] = ("componentkey", "componentKey")

#: What a key may be made of. Deliberately permissive about CONTENT (uuids,
#: slugs and ``auto-component-`` prefixes are all real shapes here) and strict
#: about LENGTH, because an unbounded value class on a megabyte of payload is
#: how a "key" becomes half a document.
_KEY_VALUE_CLASS = r"[A-Za-z0-9_.:%\-]{1,200}"


def _key_field_patterns() -> dict[str, "re.Pattern[str]"]:
    """The key-field patterns, BUILT rather than typed out.

    Two axes -- the field's spelling and whether the JSON is escaped -- so a
    third field name is one entry and not two more copies to keep in step.
    The same rule the vocabulary corpus follows in the tests.
    """
    out: dict[str, re.Pattern[str]] = {}
    for name in _KEY_FIELD_NAMES:
        out[name + " quoted"] = re.compile(
            '"' + name + r'"\s*:\s*"(' + _KEY_VALUE_CLASS + ')"'
        )
        out[name + " escaped"] = re.compile(
            r'\\"' + name + r'\\"\s*:\s*\\"(' + _KEY_VALUE_CLASS + r')\\"'
        )
    return out


_KEY_PATTERNS = _key_field_patterns()

#: How many enclosing objects out from the label this will look for a key.
#:
#: THE LABEL IS NOT ITSELF KEYED. It sits in a text node inside a component,
#: so the key is at least one object out -- but "at least one" is not "exactly
#: one", and a fixed depth of 1 would refuse a page that nests its text one
#: level deeper for reasons that have nothing to do with actions. Four is the
#: number at which a parent stops plausibly being THIS control's component and
#: starts being the carousel that holds it; past that, a key found is somebody
#: else's.
#:
#: RAISING THIS WAS CONSIDERED ON 2026-09-03 AND DECLINED, and the decision is
#: recorded here because a declined widening that nobody wrote down is
#: indistinguishable from one nobody thought of.
#:
#: The live run walked all four levels for ``Show details`` and found ZERO
#: component keys in all four spellings. Six or eight levels might have found
#: one. **That is exactly why it was not tried: a cap raised until it returns
#: something is not a measurement, it is a search for agreement.** And the
#: thing a wider walk would find is knowable in advance without running it --
#: past level four the enclosing object is the carousel, so its key belongs to
#: the container and attributing the container's actions to a button inside it
#: is the fixed-window failure this whole reader exists to avoid.
#:
#: The honest reading of that zero is the one the refusal already prints: on
#: this page the componentkey is not reachable from the label by enclosure.
#: The answer to that is a DIFFERENT relation -- the flight row's ``$L<n>``
#: pointers -- not a bigger number here.
_REFERENCE_LEVELS = 4

#: A key shorter than this is refused rather than followed. Eight characters
#: is not an identifier addressing one control among thousands, and following
#: a short string through a megabyte matches prose -- the substring defect
#: this file already paid for once, wearing a different hat.
_MIN_KEY_CHARS = 8

#: More reference sites than this and the key is not a key.
#:
#: MEASURED, NOT GUESSED, AND MEASURED ON THE RIGHT CONTROL. The obvious
#: citation here is the census's responsive duplicate pair -- two nodes,
#: identical componentkey -- and it is the WRONG one: that was measured on
#: ``button[aria-label="Open to"]``, which this reader does not read. ``Edit``
#: is DOM count 1 and unique.
#:
#: The on-point measurement is in the PAYLOAD, which is where this reader
#: looks: the census resolved ``Edit``'s own click action at TWO offsets
#: (681922 and 682537), and the Open-to menu items appear 3x each, "once per
#: rendering variant". So a payload carrying two or three copies of one
#: control's action definition is measured behaviour ON A CONTROL THIS READER
#: READS. Twelve leaves room for that plus slack, and refuses the reading
#: where a "key" turns out to be a common token.
_MAX_REFERENCE_SITES = 12

#: How many times a key may OCCUR before this refuses without walking.
#:
#: A SEPARATE BOUND FROM THE SITE CAP, and both are needed. The site cap is
#: about attribution -- twelve distinct objects is not one control. This one is
#: about COST: every occurrence costs a region walk of up to
#: :data:`_REGION_CAP` in each direction, and a key matching thousands of times
#: would drag this reader through hundreds of millions of characters of his
#: profile before refusing on the other cap. Checked first, so the expensive
#: pass never starts.
_MAX_KEY_OCCURRENCES = 200


def _keys_in(region: str) -> tuple[set[str], dict[str, int]]:
    """Distinct key VALUES in one region, and the per-spelling match counts.

    THE SET IS THE POINT. One value found through two spellings is still one
    key; two values found through one spelling are two keys and this reader
    must not choose between them. So the ambiguity test is on the distinct
    VALUES, never on the number of matches.

    The values are returned to the caller inside this module and go no
    further. Nothing that leaves this file carries one.
    """
    values: set[str] = set()
    counts: dict[str, int] = {}
    for spelling, pattern in _KEY_PATTERNS.items():
        found = pattern.findall(region)
        counts[spelling] = len(found)
        values.update(found)
    return values, counts


def _key_for_label(payload: str, at: int) -> dict[str, Any]:
    """Walk outward from a located label to the nearest object naming a key.

    STOPS AT THE FIRST LEVEL THAT NAMES ONE, which is the only defensible
    stopping rule: an outer object that also names a key names the key of
    something LARGER, and preferring the outer one would attribute a
    carousel's actions to a button inside it.

    EVERY FAILURE IS A NAMED REFUSAL, and the names are the diagnostic. This
    reader cannot print the payload, so the only way a human learns what shape
    the page actually has is by which of these refusals comes back. "No key
    within four levels" and "three distinct keys at level two" are different
    facts about LinkedIn's markup, learned without a byte of it crossing out.
    """
    out: dict[str, Any] = {
        "levels_walked": 0,
        "key_spellings": {spelling: 0 for spelling in _KEY_PATTERNS},
        "key_found": False,
        "key_spelling": None,
        "region": None,
        "refused": None,
        # The value itself is deliberately NOT in this dict under a name a
        # renderer might loop over. It travels as ``_key`` and every consumer
        # in this file reads it explicitly.
        "_key": None,
    }
    region = _enclosing_object(payload, at)
    while region is not None and out["levels_walked"] < _REFERENCE_LEVELS:
        out["levels_walked"] += 1
        start, end = region
        values, counts = _keys_in(payload[start:end])
        for spelling, count in counts.items():
            out["key_spellings"][spelling] += count
        if len(values) > 1:
            out["refused"] = (
                "%d DISTINCT component keys inside the object at level %d, so "
                "this cannot say which one belongs to the label. Choosing "
                "would be attribution by document order." % (
                    len(values), out["levels_walked"],
                )
            )
            return out
        if values:
            key = next(iter(values))
            if len(key) < _MIN_KEY_CHARS:
                out["refused"] = (
                    "the key at level %d is %d characters, under the %d-"
                    "character floor. A string that short is not addressing "
                    "one control among thousands, and following it through a "
                    "megabyte matches prose rather than references."
                    % (out["levels_walked"], len(key), _MIN_KEY_CHARS)
                )
                return out
            out["key_found"] = True
            out["_key"] = key
            out["region"] = region
            out["key_spelling"] = next(
                spelling for spelling, count in counts.items() if count
            )
            return out
        if start == 0:
            break
        region = _enclosing_object(payload, start - 1)
    if out["refused"] is None:
        out["refused"] = (
            "no component key in any of the %d objects enclosing this label "
            "(walked %d). THAT IS A FACT ABOUT THE PAGE'S SHAPE, not about "
            "the control: it means the label is not carried inside a keyed "
            "component, so there is no reference for this instrument to "
            "follow and no attribution it can honestly make."
            % (_REFERENCE_LEVELS, out["levels_walked"])
        )
    return out


def _kinds_in(region: str) -> dict[str, Any]:
    """The closed vocabulary counted in one region, plus the ORDER it occurs in.

    THE ORDER IS PART OF THE BASELINE AND COSTS NOTHING TO REPORT. August did
    not record "Edit fires SetState and ServerRequest", it recorded **SetState
    x2, THEN ServerRequest** -- a save preceded by two optimistic state
    writes. Comparing an unordered set against that would drop the half of the
    finding that says which happens first.

    AND IT EMITS NO PAYLOAD. The sequence is this file's OWN fixed strings
    sorted by where each first occurs; the offsets are used and discarded and
    the strings were never read out of the region.
    """
    counts = {kind: _occurrences(region, kind) for kind in _REPORTABLE_KINDS}
    counts["saveAndFetchNextStepRequest"] = _occurrences(
        region, "saveAndFetchNextStepRequest"
    )
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


def _actions_by_reference(payload: str, label: str) -> dict[str, Any]:
    """Which action kinds are attached to ONE labelled control, BY REFERENCE.

    THE ONE QUESTION THIS EXISTS FOR, and nothing wider::

        Show details   August census: one Navigate, ZERO ServerRequest
        Edit           August census: SetState x2, then ServerRequest
                       saveAndFetchNextStep

    WHAT IT EMITS: action KINDS from a closed set, counts, the order they
    occur in, and how many sites carried them. NOT the key, NOT the chunk, NOT
    the arguments of any request. The Edit RPC's payload carries
    ``currentStep``, ``origin`` and ``isEditFlow`` values -- none of it is
    read, because "which kinds" is the question and the rest is a different
    permission nobody has asked for.

    PER SITE, NOT SUMMED, and that choice is load-bearing. The census resolved
    ``Edit``'s click action at TWO payload offsets, and the Open-to menu items
    appear three times each, once per rendering variant -- so one control's
    action definition arriving two or three times is measured behaviour here.
    Summing would report ``SetState 4`` for a control August recorded at
    ``SetState x2`` and manufacture a disagreement out of an aggregation
    choice -- the exact way an instrument invents a finding. Each site is
    reported separately and a human compares one against August.

    A DISAGREEMENT IS THE FINDING. If ``Show details`` now carries a
    ``ServerRequest``, this prints that and says nothing about what it means.
    Deciding is a ruling and rulings are not taken by scripts.

    THE ONE REFERENCE IT FOLLOWS, AND THE ONE IT DOES NOT. This follows
    ``componentkey``. The payload has a SECOND reference mechanism -- the
    flight row's own ``$L<n>`` lazy chunk pointers, which is how the census
    resolved the ``Open to`` menu's three items -- and this does not follow
    those. That is scope, not oversight: two instruments have already answered
    the wrong question by being widened past what was asked, and a ``$L``
    follower reads a chunk chosen by an integer rather than by a name.

    THE COST OF THAT BOUND IS PAID IN A REFUSAL, NOT IN A WRONG ANSWER. If
    this page attaches the two controls' actions by ``$L`` rather than by key,
    this returns "the key is defined and never referenced" -- which names the
    mechanism as the thing that failed and is exactly the input a ruling on a
    fourth instrument would need.
    """
    out, hits = _locate_label(payload, label)
    out.update(
        {
            "key_found": False,
            "key_spelling": None,
            "key_spellings": {},
            "levels_walked": 0,
            "sites": [],
            "reference_sites": 0,
            "definition_sites": 0,
            "ancestor_sites": 0,
            "unresolved_sites": 0,
            "key_occurrences": 0,
            "kinds": None,
            "sequence": None,
        }
    )
    if out["refused"] or not hits:
        return out

    found = _key_for_label(payload, hits[0])
    out["key_found"] = found["key_found"]
    out["key_spelling"] = found["key_spelling"]
    out["key_spellings"] = found["key_spellings"]
    out["levels_walked"] = found["levels_walked"]
    if not found["key_found"]:
        out["refused"] = found["refused"]
        return out

    key = found["_key"]
    home_start, home_end = found["region"]
    pattern = r"(?<![A-Za-z0-9_])" + re.escape(key) + r"(?![A-Za-z0-9_])"
    positions = [match.start() for match in re.finditer(pattern, payload)]

    # THE OCCURRENCE CEILING, CHECKED BEFORE ANY REGION IS WALKED. Each walk
    # scans up to :data:`_REGION_CAP` in each direction, so a key found a few
    # thousand times would send this reader through hundreds of millions of
    # characters of his profile to produce a number it would refuse anyway on
    # the site cap below. Refusing FIRST is both the cheap answer and the
    # honest one: a string occurring this often is not addressing one control,
    # and the count is reported so the refusal is legible.
    out["key_occurrences"] = len(positions)
    if len(positions) > _MAX_KEY_OCCURRENCES:
        out["refused"] = (
            "the key occurs %d times, past the %d-occurrence ceiling, so no "
            "region was walked at all. A string appearing that often is not "
            "an identifier for one control -- following it would attribute "
            "the page." % (len(positions), _MAX_KEY_OCCURRENCES)
        )
        return out

    # ONE REGION PER SITE. A key written twice inside the same object -- as a
    # field and again inside a tracking blob -- is one place, not two, and
    # counting it twice would double every kind in it.
    seen_regions: dict[tuple[int, int], str] = {}
    for position in positions:
        region = _enclosing_object(payload, position)
        if region is None:
            out["unresolved_sites"] += 1
            continue
        start, end = region
        if start >= home_start and end <= home_end:
            # Inside the object the key was found in: this is the definition,
            # whatever its own braces say.
            role = "definition"
        elif start <= home_start and end >= home_end:
            # AN ANCESTOR, AND IT IS NOT AN ACTION CHUNK. An object that
            # CONTAINS the component also contains its neighbours, so its
            # kinds are the carousel's, not this control's. Counting it would
            # be the fixed-window failure reached by a different route -- the
            # window arrived at by walking rather than by a constant.
            role = "ancestor"
        else:
            role = "reference"
        seen_regions.setdefault(region, role)

    for region, role in sorted(seen_regions.items()):
        start, end = region
        reading = _kinds_in(payload[start:end])
        out["sites"].append(
            {
                "role": role,
                "region_chars": end - start,
                "kinds": reading["kinds"],
                "sequence": reading["sequence"],
            }
        )
        if role == "reference":
            out["reference_sites"] += 1
        elif role == "ancestor":
            out["ancestor_sites"] += 1
        else:
            out["definition_sites"] += 1

    if out["unresolved_sites"]:
        out["refused"] = (
            "%d occurrence(s) of the key sit in no object this reader can "
            "walk -- unbalanced, or larger than the %d-character cap. The "
            "reading is refused rather than reported without them, because "
            "the site it could not read is exactly where the ServerRequest "
            "that would REFUSE a click might be. A partial reading that comes "
            "back missing a kind is indistinguishable from a control that "
            "does not have it." % (out["unresolved_sites"], _REGION_CAP)
        )
        out["sites"] = []
        return out

    if out["reference_sites"] > _MAX_REFERENCE_SITES:
        out["refused"] = (
            "the key is referenced at %d distinct sites, past the %d-site "
            "cap. A key that appears that often is not addressing one "
            "control, and attributing every one of those objects to this "
            "label would be the fixed-window failure with more steps."
            % (out["reference_sites"], _MAX_REFERENCE_SITES)
        )
        out["sites"] = []
        return out

    if out["reference_sites"] == 0:
        out["refused"] = (
            "the key is DEFINED and never referenced anywhere else in the "
            "payload, so there is no reference to follow. That is a fact "
            "about the mechanism, not about the control: this page does not "
            "attach this control's actions by componentkey, and a third "
            "instrument has now failed to attribute it. Do not read it as "
            "'the control has no actions'."
        )
        return out

    union = {kind: 0 for kind in _REPORTABLE_KINDS}
    union["saveAndFetchNextStepRequest"] = 0
    order: list[str] = []
    for site in out["sites"]:
        if site["role"] != "reference":
            continue
        for kind, count in site["kinds"].items():
            union[kind] = max(union[kind], count)
        for kind in site["sequence"]:
            if kind not in order:
                order.append(kind)
    # THE FLOOR, AND IT IS THE MOST IMPORTANT LINE IN THIS FUNCTION.
    #
    # ZERO OF EVERYTHING IS THE EXACT SHAPE OF PERMISSION. The operator ruled
    # on 2026-09-01 that a click measured to issue no ``ServerRequest`` is by
    # effect a READ -- so an all-zero reading from this instrument is the
    # thing that would authorise pressing a button on his live profile. And an
    # all-zero reading has two causes that look identical: the control really
    # has no actions, or THIS READER FOUND THE KEY IN OBJECTS THAT DO NOT
    # CARRY ACTIONS. The second is entirely plausible here -- a payload that
    # writes ``{"componentkey":"X"},{"actions":[...]}`` as SIBLINGS rather
    # than as parent and child would produce exactly this, and nothing in the
    # output would say so.
    #
    # SO IT REFUSES, and the refusal is what makes every NON-zero reading
    # trustworthy: a run that reports kinds has demonstrated, ON THIS PAYLOAD,
    # that it can see kinds through a reference. A zero for one particular
    # kind is then a reading rather than a silence, which is the negative
    # control ``dom.read_sdui_actions`` had to be given for the same reason.
    if not any(union.values()):
        out["refused"] = (
            "every reference site resolved and NOT ONE contains an action "
            "kind from the closed set. This is NOT 'the control has no "
            "actions' -- it is equally consistent with the key being defined "
            "beside its actions rather than around them, which this reader "
            "would not be able to tell apart. A zero from a reader that has "
            "not been shown returning non-zero on this same payload is not a "
            "measurement, and an all-zero reading is what would authorise a "
            "click."
        )
        return out

    # MAX ACROSS SITES, NOT SUM, for the responsive-duplicate reason above.
    # Stated in the output too, because a number whose aggregation rule is
    # only in the source is a number the next reader will misread.
    out["kinds"] = union
    out["sequence"] = order
    return out


def _render_reference(found: dict[str, Any]) -> list[str]:
    """The lines a run prints for ONE control. Pure, so a test can read them.

    THE LEAK CHECK LIVES HERE RATHER THAN ON THE DICT. The dict is an
    intermediate; the LINES are what reaches a transcript, and a transcript is
    a publication channel -- that is this repo's own finding about failure
    messages, applied to a printout. So the rendering is a function with no
    side effects and ``tests/test_otw_payload_probe.py`` asserts a
    vanity-shaped key never appears in what it returns.
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
    # THE FOUR KEY SPELLINGS PRINT WHETHER OR NOT ONE MATCHED, and the case
    # where NONE did is the one they exist for. "No key here" and "a key
    # written in a spelling this reader does not know" produce the same
    # refusal text, and only these four counts tell them apart -- which is
    # the locator's own lesson, and it was earned by a reader that reported
    # `Show details`: 0 OCCURRENCES when the label was sitting there escaped.
    if found["levels_walked"]:
        lines.append(
            "      key fields seen while walking %d level(s): %s"
            % (found["levels_walked"], found["key_spellings"])
        )
    if found["key_found"]:
        lines.append(
            "      key: found at level %d, spelling %r (value withheld -- one "
            "known key on this page carries his profile slug)"
            % (found["levels_walked"], found["key_spelling"])
        )
    if found["key_occurrences"]:
        lines.append(
            "      key occurrences in the whole payload: %d"
            % found["key_occurrences"]
        )
    # THE SITE SUMMARY PRINTS BEFORE ANY REFUSAL THAT HAS ONE. A refusal
    # whose evidence is withheld is a reader saying "no" and keeping the
    # reason: the all-zero refusal below is only readable if you can see that
    # it DID resolve sites and they DID hold nothing.
    if found["key_found"]:
        lines.append(
            "      sites: %d definition, %d reference, %d ancestor, %d "
            "unresolved"
            % (
                found["definition_sites"],
                found["reference_sites"],
                found["ancestor_sites"],
                found["unresolved_sites"],
            )
        )
    for index, site in enumerate(found["sites"]):
        present = {k: v for k, v in site["kinds"].items() if v}
        lines.append(
            "        site %d  %-10s %6d chars  %s"
            % (index, site["role"], site["region_chars"], present or "no kinds")
        )
        if site["sequence"]:
            lines.append("                  order: %s" % " -> ".join(site["sequence"]))
    if found["refused"]:
        lines.append("      REFUSED: %s" % found["refused"])
        return lines
    lines.append(
        "      ATTRIBUTED (reference sites only, MAX across sites not sum -- "
        "the payload carries one action list once per rendering variant; "
        "August resolved Edit's at two offsets):"
    )
    lines.append(
        "        %s" % ({k: v for k, v in found["kinds"].items() if v} or "none")
    )
    if found["sequence"]:
        lines.append("        order: %s" % " -> ".join(found["sequence"]))
    return lines


async def main() -> None:
    await BROWSER.start()
    print("=== OPEN TO WORK PAYLOAD, LIVE")
    print("    writes nothing, prints no url, no label and no payload text\n")

    async with BROWSER.session() as page:
        # --- PASS 1: establish the one url. Reads nothing. -------------------
        #
        # NO LISTENER IS ATTACHED HERE. This pass exists only to resolve the
        # ``/in/me/`` redirect into the concrete address pass 2 will compare
        # against, so that the comparison in pass 2 is against a string this
        # script already holds rather than against a pattern that would also
        # match a stranger.
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
            event loop and cannot be a place where a body is read at an
            unbounded moment. The body is read later, once, by the caller.
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
        status = response.status
        print(f"    status: {status}")
        if status != 200:
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
        print(f"\n    payload characters: {len(payload)}")
        print("    (August measured 1,177,077 across the whole saved file, of")
        print("     which 1,091,238 was flight payload rather than DOM)\n")

        counts = _count_vocabulary(payload)
        for group, tokens in counts.items():
            print(f"    {group}:")
            for token, count in tokens.items():
                shown = token if len(token) <= 56 else token[:53] + "..."
                print(f"      {count:6d}  {shown}")
            print()

        print("    tokens the census counted, compared:")
        for label, token in (
            ("occurrences of `opentowork` or `open-to-work`", None),
            ("occurrences of `psettings`", "psettings"),
        ):
            if token is None:
                live = sum(payload.count(t) for t in _ABSENT_IN_AUGUST)
            else:
                live = payload.count(token)
            august = _AUGUST[label]
            verdict = "SAME" if live == august else "*** CHANGED ***"
            print(f"      {label}: august {august}, live {live}  {verdict}")

        noisy = _undiscriminating_tokens(payload)
        print("    vocabulary self-check -- tokens that also occur INSIDE")
        print("    larger words on this page (substring count vs token count):")
        if not noisy:
            print("      none: every token above stands alone wherever it occurs")
        for token, (naive, bounded) in sorted(noisy.items()):
            print(f"      {token!r}: substring {naive}, as a token {bounded}")
            print("        the reported count is the TOKEN one; the substring")
            print("        reading of this token was noise")

        print("\n=== THE TWO CONTROLS THE CLICK RULING TURNS ON")
        print("    August recorded:")
        print("      Show details  one Navigate, ZERO ServerRequest")
        print("      Edit          SetState x2, then ServerRequest")
        print("                    saveAndFetchNextStepRequest")
        print()
        for label in _CONTROL_LABELS:
            found = _actions_for(payload, label)
            print(
                f"    {label!r}: {found['occurrences']} occurrence(s)"
                f"  spellings={found['spellings']}"
                f"  located_by={found['located_by']!r}"
            )
            if found["refused"]:
                print(f"      REFUSED: {found['refused']}")
                continue
            print(f"      region: {found['region_chars']} chars, balanced")
            for kind, count in found["kinds"].items():
                if count:
                    print(f"        {count:4d}  {kind}")
            if not any(found["kinds"].values()):
                print("        NO action kind from the closed set is in this")
                print("        region. That is a fact about SDUI's shape, not")
                print("        about the control: actions are defined in their")
                print("        own chunks and REFERENCED by componentkey, so")
                print("        the object enclosing a label does not contain")
                print("        them. Enclosure cannot attribute here -- only")
                print("        following the reference can, which is a")
                print("        different instrument and a wider one.")

        print("\n=== READER 3: FOLLOWING THE COMPONENTKEY REFERENCE")
        print("    The two readers above cannot attribute an action to a")
        print("    control -- a tally has no control, and an enclosure holds")
        print("    no actions on this page. This one follows the reference")
        print("    SDUI actually uses. It emits action KINDS and nothing")
        print("    else: no key, no chunk, no request arguments.")
        print()
        for label in _CONTROL_LABELS:
            for line in _render_reference(_actions_by_reference(payload, label)):
                print(line)
            print()

        unknown = _unknown_action_kinds(payload)
        print(f"\n    SDUI action type names NOT in this vocabulary: {unknown}")
        if unknown:
            print("      The protocol has names this probe does not know. They are")
            print("      NOT printed -- naming a string read out of his payload is")
            print("      a separate decision from counting one. Re-read properly.")

        # THE BODY IS DROPPED HERE. Not because the name going out of scope is
        # a security control -- it is not, and pretending otherwise would be
        # the kind of confident claim this package refuses -- but because
        # nothing above copied it anywhere, nothing below reads it, and this
        # script has no path to write a file with. That is the actual property.
        del payload

        print("\n=== WHAT THIS DOES AND DOES NOT SETTLE")
        print("    It is a REGRESSION DETECTOR for the August analysis, not a")
        print("    re-derivation of it: counts cannot attribute an action to a")
        print("    control. If anything above reads CHANGED, the analysis in")
        print("    _audit/_slice-otw-census.md is describing a page that has")
        print("    moved and a human has to re-take it.")
        print("    It does NOT make set_open_to_work performable. It makes the")
        print("    measurement re-takeable, which it has not been since August.")

    await BROWSER.stop()


# GUARDED, for the reason ``_probe_messaging.py`` states at length: importing
# a script must not DO anything, and ``tests/test_scripts_are_import_safe.py``
# accepts an attribute call at module scope -- which ``asyncio.run(...)`` is.
# A probe ending in a bare one would launch a browser and drive his signed-in
# session on import. This one runs only when run.
if __name__ == "__main__":
    asyncio.run(main())
