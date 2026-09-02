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

IT IS A REGRESSION DETECTOR, NOT A RE-DERIVATION. The August analysis
attributed individual actions to individual controls by reading the payload's
structure around each ``componentkey``. A count cannot do that: it can say the
payload contains eleven ``Navigate`` tokens, and it cannot say which control
owns them.

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


def _actions_for(payload: str, label: str) -> dict[str, Any]:
    """Which action kinds sit in the region around ONE labelled control.

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
    # THE QUOTED FORM FIRST, THEN THE ESCAPED ONE. Bare is never used to
    # locate: in a payload this size a bare label matches prose, and
    # attributing actions to a prose match is the fixed-window failure wearing
    # a different hat.
    chosen = "quoted" if seen["quoted"] else ("escaped" if seen["escaped"] else "")
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
        "kinds": None,
        "region_chars": None,
    }
    if not chosen and seen["bare"]:
        out["refused"] = (
            "the label appears %d time(s) BARE and never as a quoted or "
            "escaped JSON string, so this reader can see the text but not the "
            "action definition it belongs to. THAT IS A FACT ABOUT THIS "
            "READER, not about the page -- do not read it as the control "
            "having gone." % seen["bare"]
        )
        return out
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
