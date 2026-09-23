"""THE DISCLOSING PRESS, bounded mechanically rather than by judgement.

Implements `_audit/2026-09-19-the-disclosing-press-ruling.md`. Read that first:
the four conditions are CONJUNCTIVE, and the reasoning is what makes the list
narrow. This module is the guard that bounds the ruling, and the ruling's last
line is that nobody presses anything until this exists -- *a ruling is not a
permission to act ahead of the guard that bounds it.*

## WHICH RULE GOVERNS A CALL SITE, because the confusion cost a fortnight

**THIS MODULE GOVERNS THE PACKAGE.** Any press from `linkedin_server/*.py` goes
through :func:`disclose` and is bound by all four conditions below.

**PROBES UNDER ``scripts/`` ARE GOVERNED BY A DIFFERENT RULE** --
``tests/test_probe_interaction_budget.py``, which splits verbs into OPEN and
GATED and lets a probe click freely while requiring a declaration for anything
that persists or sends.

The two are not in competition and they are not the same bar. A probe
legitimately opens a menu to find out what is in it; the package may only do so
under conditions 1-4. **The reason this distinction is stated at the top of the
file rather than inferred is that nobody stated it before**: the package rule
never covered ``scripts/`` at all, so the fleet's restraint was tacit, and for a
fortnight "we do not press" was simultaneously true of the package and false of
the probes, with no test anywhere able to tell the difference.

**TYPING IS REFUSED BY BOTH.** ``page.fill`` is not a press. The one ``fill``
measured in ``scripts/`` is refused by this ruling's own terms whatever the
probe rule concludes about it.

## THE FOUR CONDITIONS, and each is mechanically checkable

1. **THE PAGE IS ALREADY ADMITTED**, by :func:`readonly.is_read_url`, checked
   BEFORE any press. **A press NEVER extends reach.** If the address is refused,
   every control on it is refused. This closes the laundering path -- load an
   admitted page, press into a refused one.
2. **THE CONTROL MATCHES AN ENUMERATED SHAPE, BY ATTRIBUTE** --
   :data:`SANCTIONED_SHAPES`, exact membership, never a label. A label is page
   text and this server does not read page text into decisions.
3. **THE PRESS IS SHOWN NOT TO MOVE AN OUTWARD COUNTER**, read before and after.
   **Where no counter can price the press, UNMEASURABLE RESOLVES AGAINST IT.**
4. **IT IS CLOSED AND THE CLOSURE VERIFIED** -- the toggle restored and the page
   confirmed as found.

## THE WITNESS RIDES ALONGSIDE THE VERDICT AND NEVER DECIDES IT

**THIS IS THE DESIGN POINT MOST LIKELY TO ERODE, so it is here rather than only
in a wave's report.** :func:`disclose` returns a ``witness`` saying whether
anything actually opened. It is **not a fifth condition**. Permission stays
decided on safety alone, and folding disclosure in would turn a READING into a
GATE -- refusing a perfectly safe press for the sin of being uninformative.

**AND THE WITNESS IS ATTACHED TO REFUSALS TOO**, which is the half that looks
like an oversight and is not. *"Refused on counters AND nothing opened"* is a
different fact from *"refused"*, and a reader who has to infer which one they
have will infer wrong. A refusal that drops the witness is a refusal that
cannot be told from a press that was never informative in the first place.

**WHY IT EXISTS AT ALL:** condition 4 compares the control's state before the
press with its state after the DISMISSAL, and a successful Escape makes those
equal whether or not anything ever opened. **Two readings cannot describe three
states.** The gate was SAFE and BLIND, and those are different properties -- no
row may be banked on a press verdict that carries no witness.

## HOW CONDITION 3 IS SATISFIED, AND WHY THERE ARE TWO WAYS

``priced_by`` once named every counter READ at both ends, so condition 3 could
be shown PASSING and never shown capable of FAILING. Requiring SENSITIVITY
instead would have been unsatisfiable almost everywhere -- a counter is shown
sensitive only by a press of that class moving it, which for an outward counter
is the write this gate prevents -- and **a condition nothing can satisfy is a
disabled gate, not a stricter one**.

So ``condition_3_route`` names which of two ways it was satisfied:
``sensitive_counter`` (established, though DERIVED from what a label MEANS) or
``structural_argument`` (an explicit case that no OUTWARD effect is possible,
carrying its BOUND and its REFUTERS). ``sensitivity_established`` separates
them, and **a merely readable counter is neither and prices nothing.**

## EVERY REFUSAL A URL CAN PREDICT IS TAKEN BEFORE THE PAGE IS TOUCHED

**RULED AND REPAIRED 2026-09-21.** `_audit/2026-09-21-the-all-filters-press.md`
section 3 measured this gate taking a real click and a real `Escape` on a
surface it then refused for `no_sensitivity_basis` -- a refusal that is a PURE
FUNCTION OF THE URL and was therefore knowable before any contact. The surface
where it was found lists OTHER PEOPLE. *A gate that clicks and then says no has
already done the thing it refused.*

The pre-press branch of :func:`evaluate` now runs :func:`check_basis`, which is
condition 3's url-derivable half: `no_sensitivity_basis` and
`structural_argument_incomplete` are both decided from :data:`SENSITIVITY_BASES`
alone, and both are now returned with the page untouched.

**WHAT THIS DOES NOT DO, so nobody reads it as more than it is.** It only ever
makes the gate refuse EARLIER. No press that was permitted is now refused, and
no press that was refused is now permitted -- the same conditions decide, at an
earlier moment. Nothing here weakens a condition.

**AND THE BASIS-LESS PRE-PRESS VERDICT IS A REFUSAL, NOT A PERMIT.** `/in/me/`
declares no basis, so his own profile is ADMITTED (condition 1, on its own
merits) and NOT PERMITTED TO PRESS. The refusal is NOT-YET -- declaring a basis
for the surface is an available ruling and the verdict names it -- and the
alternative was making the verdict true by declaration, which is what a permit
on a surface the gate would refuse anyway amounts to.

**THE SECOND INSTANCE, same root cause, found by enumerating the branches.**
:func:`evaluate` inferred "I am being called before a press" from the ABSENCE of
counter readings. A ``read_counters`` that returns ``None`` produces exactly
that shape AFTER a real click, so the gate clicked, dismissed, skipped
conditions 3 and 4 entirely and returned ``permitted_to_attempt: True`` with no
refusal at all -- worse than refusing late, because a caller testing
``refused`` sees nothing wrong. A moment is not inferable from its inputs:
``already_pressed`` says it instead.

## WHY THE CALLER CANNOT HAND IN A SELECTOR

:func:`disclose` takes a SHAPE KEY from a closed tuple, not a selector string.
An arbitrary string can never become a press target -- the same property
``dom.MESSAGING_FILTERS`` gives the one sanctioned read-path click already in
the package, and the same reason: a permission phrased as "may press on that
page" is a different and much wider thing than "may press one of these shapes".

## WHAT IS REFUSED REGARDLESS, and one of these is a finding of this repository

* **COMPOSERS AND EDITORS.** The autosave class. `/article/new/` is admitted for
  READING and opening it may autosave a draft **no surface here can detect** --
  17 draft-listing addresses were run against the boundary and all 17 refused.
  A composer is not a disclosure even when it renders like one.
* **NAVIGATION AND SUBMISSION.**
* **THIRD-PARTY SURFACES.** A press that could register an interaction visible
  to another person is outward-facing, and outward-facing is not the lead's to
  grant. A profile view is the clear case: it discloses content to this server
  AND discloses this server to the person.
* **TYPING.**

## NOT-YET versus NEVER-BY-THIS-ROUTE, and why the distinction is in the output

Every refusal carries ``reachable_by_this_route``. A caller must be able to tell
a control that this mechanism will reach once something else lands from one it
will NEVER reach, because -- in the words of the wave that measured it --
*"filing either as blocked-on-the-mechanism would have been wrong in a way that
looks patient."*

**A DEFERRAL THAT WILL NEVER RESOLVE IS WORSE THAN A REFUSAL, because it
consumes a future wave.** Measured cases that are NEVER, not yet:

* the contact-info control carries **neither** sanctioned attribute. It is
  wired -- ``getEventListeners`` shows a click listener, against a negative
  control of NONE on three static nodes -- but **it declares nothing**, so the
  only way to match it is by LABEL TEXT, which condition 2 forbids. It is also
  refused a second time for opening an editor.
* the intro editor's 11 fields: **0 carry either attribute**, every ``id``
  shapes to opaque, no field has a ``name``.

**AND A LISTENER-PRESENCE MATCHER IS NOT THE ANSWER.** It would admit nearly
every interactive node on the page -- the family wildcard condition 2 exists to
forbid, the same shape as the settings-family pattern that would have admitted
six account-ending spellings. If a third shape is ever needed it is a RULING
REQUEST with a measured blast radius, not an edit here.

## THE OPEN-MOMENT READING, AND WHY IT IS A TABLE AND NOT A CALLBACK

**ADDED 2026-09-23, because until then no reader could read what a press
disclosed.** The witness below counts a closed set and the dismissal follows it
immediately, so the only instant at which disclosed content exists was spent on
integers that say THAT something opened and never WHAT. Every row this gate was
ruled for (a panel on his analytics, a feed item's menu) wants the what.

**THE READING OBEYS THE WITNESS'S OWN RULE: A CLOSED SET, NEVER A CALLER'S
CALLABLE.** A caller names a KEY from :data:`OPEN_READINGS`, exactly as it
names a shape key, and the table decides everything else: which surfaces the
reading is sanctioned on, and which PHRASES go into the page. The page answers
through ``dom.read_count_lines`` -- a script already declared, already
scanned, at a call site already inside the evaluate budget -- with PHRASE
POSITIONS AND INTEGERS. No page string crosses the boundary, so the reading
can only ever publish this module's own literals and numbers.

**IT IS TAKEN TWICE, AND THE PAIR IS THE POINT**, for the witness's reason: a
phrase can already be on the page before anything is pressed (a feed post's
own text can say anything). So the same reading is taken immediately before
the click and again at the open moment, and ``appeared`` names only what the
press brought into view.

**IT RIDES ALONGSIDE THE VERDICT AND NEVER DECIDES IT**, like the witness. A
reading does not make a press permitted or refused, and it is attached to a
refusal too. **A reading taken during a press the verdict REFUSED is not a
delivered read**, and a caller that banks one is banking a write's side effect.

## AIMING WITHOUT A LABEL: THE SCOPE TABLE

``index`` is a POSITION over the whole page, and page chrome comes first in
document order -- on the analytics page the nav and a skip-link menu precede
``main``. So a package caller could only aim by a position whose meaning moves
with LinkedIn's chrome. :data:`PRESS_SCOPES` narrows the candidates to
``<scope> <shape>`` BEFORE the index is applied. A scope is a closed-table KEY
like everything else here, it is structural (a landmark or a component name
LinkedIn's own code writes), never a label, and it can only REMOVE candidates:
whatever it selects still matches a sanctioned shape.
"""
from __future__ import annotations

from typing import Any, Callable, Optional
from urllib.parse import urlsplit

from linkedin_server import readonly

#: THE ENUMERATED DISCLOSURE SHAPES. The whole of what may be pressed.
#:
#: Attribute selectors, matched by EXACT MEMBERSHIP in this tuple. A caller
#: names a shape; it cannot supply one. The list grows only by a further
#: ruling, exactly as the URL allowlist does.
SANCTIONED_SHAPES: tuple[str, ...] = (
    "[aria-expanded]",
    "[aria-haspopup]",
)

#: Address fragments that mark a COMPOSER OR EDITOR. Refused for pressing even
#: when the address is admitted for READING -- which `/article/new/` is.
#:
#: **THE PRESS ALLOWLIST IS A STRICT SUBSET OF THE READ ALLOWLIST**, and this
#: tuple is the difference. Stated explicitly because the tempting shortcut is
#: to treat "readable" as "pressable", and the autosave class is precisely the
#: counterexample: a page this server may open is not thereby a page whose
#: controls it may activate.
_COMPOSER_MARKERS: tuple[str, ...] = (
    "/article/new",
    "/preload/sharebox",
    "/messaging/compose",
    "/edit/",
    "/newsletter/new",
    "/post/new",
)

#: A member path segment that is NOT his own. ``/in/me/`` resolves to whoever
#: is signed in; anything else under ``/in/`` is a third party's surface.
_SELF_SEGMENTS = frozenset({"me"})

#: HOW CONDITION 3 MAY BE SATISFIED, PER SURFACE, AS A CLOSED TABLE.
#:
#: **RULED 2026-09-19** (``_audit/2026-09-19-two-census-conventions-ruled.md``
#: section 5). ``check_counters`` used to pass on any counter READ at both
#: ends, and ``priced_by`` named those -- so condition 3 could be shown
#: PASSING and could never be shown capable of FAILING, which is this
#: repository's own definition of a check that certifies nothing.
#:
#: Requiring SENSITIVITY alone was rejected and the reason is not leniency: a
#: counter is shown sensitive only by a press of that class moving it, which
#: for an outward counter is the write this gate exists to prevent. **A
#: condition nothing can satisfy is a disabled gate, not a stricter one.**
#:
#: So condition 3 is satisfied in EITHER of two ways, and the verdict says
#: WHICH:
#:
#: * ``sensitive``  -- a counter shown SENSITIVE to this press class. The
#:   worked example is ``off_state`` for a feed press: sensitivity derived
#:   from what the label constant MEANS rather than from watching it move,
#:   with availability verified and sensitivity marked derived.
#: * ``structural`` -- an explicit argument that NO outward effect is possible
#:   from this surface. Made in writing, recorded here, open to refutation.
#:
#: **A MERELY READABLE COUNTER IS NEITHER AND NO LONGER PRICES ANYTHING.**
#:
#: THE TABLE IS CLOSED AND KEYED BY SURFACE, not supplied by a caller, for the
#: same reason ``SANCTIONED_SHAPES`` is: a basis a caller can assert is a basis
#: a caller can invent, and "no outward effect is possible here" is exactly the
#: claim somebody in a hurry would assert about a surface they had not read.
#: **WHAT A ROUTE (b) ENTRY MUST CARRY.** A bare assertion is not an argument,
#: and the shape is taken from the first one written
#: (``_audit/2026-09-19-the-first-sanctioned-press.md`` section 8) rather than
#: invented: the claims, THE BOUND it does not exceed, and what would REFUTE
#: it. Enforced at runtime below and asserted in ``tests/test_press.py``.
#:
#: **ROUTE (b) IS WEAKER THAN ROUTE (a) AND MUST TRAVEL SAYING SO.** It is an
#: argument, not a measurement. The ruling admits it because (a) is
#: unsatisfiable on some surfaces, **not because the two are equivalent** --
#: and the first structural argument on the record is exactly the one most
#: likely to be cited later as though it were a measurement.
_STRUCTURAL_REQUIRED = ("why", "bound", "refuters")

SENSITIVITY_BASES: tuple[tuple[str, dict[str, Any]], ...] = (
    (
        "/feed/",
        {
            "kind": "sensitive",
            "counters": ("off_state",),
            "why": (
                "read_reaction_surface publishes off_state, a count of "
                "reaction controls wearing the reaction-OFF label. A reaction "
                "necessarily moves it, which follows from what that label "
                "constant MEANS rather than from having watched it move, and "
                "a reaction is visible to the post's author -- so it is "
                "OUTWARD. Availability verified by instrument (non-zero, read "
                "3 on a live feed); sensitivity DERIVED and marked as such."
            ),
        },
    ),
    (
        "/analytics/profile-views/",
        {
            "kind": "structural",
            # WRITTEN BY THE WAVE THAT PRESSED HERE, not by this module.
            # Recorded verbatim in shape from
            # _audit/2026-09-19-the-first-sanctioned-press.md section 8, which
            # is where the full argument and its provenance live.
            "why": (
                "(1) THE SURFACE ADDRESSES NO ONE -- it renders his own "
                "profile-view analytics, with no recipient, no composer, no "
                "third-party subject and nothing naming another account as a "
                "destination; on this package's DESTINATION vs CONTENT line "
                "an outward effect requires a destination and this page has "
                "none. (2) THE PRESS TARGET'S SEMANTICS ARE VISIBILITY, NOT "
                "SUBMISSION -- aria-expanded denotes the expanded state of a "
                "region the control owns, over content already delivered to "
                "the client. (3) THE RULING ALREADY REFUSES THE ALTERNATIVES "
                "INDEPENDENTLY -- navigation, submission, composers, typing "
                "and third-party surfaces are out by construction."
            ),
            "bound": (
                "THIS ARGUES NO OUTWARD EFFECT, NOT NO EFFECT. An expansion "
                "could plausibly cause a client-side or remembered-filter "
                "write. That is a write in the weak sense and NO OTHER PERSON "
                "CAN OBSERVE IT, which is precisely what an outward counter "
                "measures. Anyone using this argument for a surface where "
                "that distinction does not hold is misusing it."
            ),
            "refuters": (
                "the expanded region containing any control that addresses a "
                "person (message, invite, follow, endorse)",
                "the expansion issuing a request whose effect another account "
                "could observe",
                "LinkedIn surfacing a third-party-visible signal from this "
                "page, as a profile view is surfaced to its owner",
                "any counter later shown sensitive to a press here -- which "
                "would not refute the press but would move it from (b) to "
                "the stronger (a)",
            ),
        },
    ),
)


def sensitivity_basis(url: Optional[str]) -> Optional[dict[str, Any]]:
    """The declared basis for this surface, or None. PURE.

    None means condition 3 has no way to be satisfied here yet -- not that the
    press is unsafe, and not that no basis could ever exist. Supplying one is
    an edit to the table above with an argument, which is the point.
    """
    if not url:
        return None
    path = urlsplit(str(url).strip()).path
    for marker, basis in SENSITIVITY_BASES:
        if marker in path:
            return basis
    return None


#: THE OPEN-MOMENT READINGS, AS A CLOSED TABLE. See the module docstring.
#:
#: Each entry names the EXACT paths it is sanctioned on (equality, not
#: containment: a reading measured on one surface says nothing about another
#: that happens to share a prefix) and the phrases it ships into the page, as
#: ``(term, phrase)`` pairs. A phrase is already in the normalised form
#: ``dom.COUNT_LINES_JS`` compares against -- lowercase ASCII letters and
#: digits, single-spaced -- and ``tests/test_press_open_reading.py`` asserts
#: that of every entry, so a phrase that could never match cannot sit here
#: looking like a measurement.
#:
#: **WHAT COMES BACK IS A TERM AND AN INTEGER.** The term is the first element
#: of a pair in this table; the integer is the number the page drew beside the
#: phrase, when it drew one of the two shapes that carry a value. Nothing else.
_READING_REQUIRED = ("surfaces", "phrases", "why")

OPEN_READINGS: tuple[tuple[str, dict[str, Any]], ...] = (
    (
        "feed_item_share_menu",
        {
            "surfaces": ("/feed/",),
            "phrases": (
                ("copy_link", "copy link to post"),
                ("copy_link", "copy link"),
                ("embed", "embed this post"),
                ("share_via", "share via"),
            ),
            "why": (
                "M C72, the READ half of sharing a post off LinkedIn: the "
                "off-platform items a feed item's menu builds on demand. The "
                "needles are the three scripts/_probe_off_platform_controls.py "
                "counted at 0 on the unpressed feed on 2026-09-19, behind a "
                "detector control that matched each of them -- absent until "
                "a menu opens, which is exactly what a reading at the open "
                "moment is for."
            ),
        },
    ),
    (
        "profile_views_filter_menu",
        {
            "surfaces": ("/analytics/profile-views/",),
            "phrases": (
                ("time_range", "past 7 days"),
                ("time_range", "past 14 days"),
                ("time_range", "past 28 days"),
                ("time_range", "past 30 days"),
                ("time_range", "past 90 days"),
                ("time_range", "past 365 days"),
                ("time_range", "past year"),
                ("all_viewers", "all viewers"),
                ("interesting_viewers", "interesting viewers"),
                ("recruiters", "recruiters"),
                ("hiring_managers", "hiring managers"),
                ("your_network", "your network"),
                ("your_company", "people at your company"),
                ("senior_leaders", "senior leaders"),
                ("decision_makers", "decision makers"),
                ("show_results", "show results"),
                ("reset", "reset"),
                ("cancel", "cancel"),
                ("apply", "apply"),
                # TWO CONTROLS THAT CARRY NO SANCTIONED ATTRIBUTE (measured on
                # a capture, section 2.1 of the 2026-09-23 record). Present
                # here so the reading says whether each is DRAWN -- they read
                # as `held` if so -- which the structural probe cannot: it
                # lists only nodes a press could name.
                ("show_more_analytics", "show more analytics"),
                ("all_filters", "all filters"),
            ),
            "why": (
                "P O3 and N 134: what the filter pills on his profile-views "
                "analytics disclose when opened -- which time ranges, which "
                "viewer categories, and the menu's own controls. The three "
                "pills carry [aria-expanded] and a <label> caption (captions "
                "per dom.PROFILE_VIEWS_INSIGHTS_JS's measured block: a time "
                "range, 'Interesting viewers', 'Company'). The Company pill's "
                "options are OTHER PEOPLE'S EMPLOYERS; this entry carries no "
                "phrase that could match one, and a reading can only ever "
                "publish these terms and integers, so opening it discloses "
                "nothing further through this reading."
            ),
        },
    ),
)


def open_reading(key: Optional[str]) -> Optional[dict[str, Any]]:
    """The table entry for a reading key, or None. PURE."""
    for name, entry in OPEN_READINGS:
        if name == key:
            return entry
    return None


def check_reading(url: Optional[str], reading: Optional[str]) -> dict[str, Any]:
    """The reading half of the pre-press gate. PURE, and TERMINAL when it refuses.

    ``None`` is no reading asked for, which is the gate as it always was. A key
    outside :data:`OPEN_READINGS` is refused the way an off-list shape is: a
    caller cannot supply a reading, only name one. A key named on a surface its
    entry does not list is refused too -- the phrases were chosen for a page,
    and shipping them into another one measures nothing anybody chose.
    """
    if reading is None:
        return {"pressed": False, "reading_ok": True}
    entry = open_reading(reading)
    if entry is None:
        return _refuse(
            "reading_not_sanctioned",
            "the reading is not a key of press.OPEN_READINGS. A caller NAMES a "
            "reading and cannot supply one: the open moment is the most "
            "privileged instant this module has, and code handed in from "
            "outside would run inside it.",
            terminal=True,
        )
    path = urlsplit(str(url or "").strip()).path
    if path not in tuple(entry.get("surfaces") or ()):
        return _refuse(
            "reading_not_for_this_surface",
            "this reading is sanctioned only on the surfaces its entry in "
            "press.OPEN_READINGS lists, and this address is not one of them. "
            "Its phrases were chosen for a page; on another page they measure "
            "nothing anybody chose.",
            terminal=True,
        )
    return {"pressed": False, "reading_ok": True}


#: WHERE A PRESS MAY LOOK FOR ITS CONTROL, AS A CLOSED TABLE. See the module
#: docstring. A scope is a selector for a CONTAINER, and the press looks for
#: its shape only inside it: ``<scope> <shape>``. It narrows and never widens.
#:
#: **A SCOPE IS STRUCTURAL, NEVER A LABEL**, for condition 2's reason, and
#: ``tests/test_press_open_reading.py`` refuses any entry that reads text or an
#: accessible name.
_SCOPE_REQUIRED = ("selector", "why")

PRESS_SCOPES: tuple[tuple[str, dict[str, Any]], ...] = (
    (
        "main",
        {
            "selector": "main",
            "why": (
                "the page's own content landmark. Document order puts the "
                "global nav and a skip-link jump menu AHEAD of it, and both "
                "draw disclosure controls: the 2026-09-05 controls census of "
                "/analytics/profile-views/ surfaced the nav's business menu "
                "on a press. A page-wide index therefore names chrome before "
                "it names anything of his."
            ),
        },
    ),
)


def press_scope(key: Optional[str]) -> Optional[dict[str, Any]]:
    """The table entry for a scope key, or None. PURE."""
    for name, entry in PRESS_SCOPES:
        if name == key:
            return entry
    return None


def check_scope(scope: Optional[str]) -> dict[str, Any]:
    """The scope half of the pre-press gate. PURE, and TERMINAL when it refuses."""
    if scope is None:
        return {"pressed": False, "scope_ok": True}
    if press_scope(scope) is None:
        return _refuse(
            "scope_not_sanctioned",
            "the scope is not a key of press.PRESS_SCOPES. A caller names a "
            "scope and cannot supply one, for the reason it cannot supply a "
            "shape: a selector handed in from outside is a press target "
            "chosen by whoever wrote it.",
            terminal=True,
        )
    return {"pressed": False, "scope_ok": True}



#: THE WITNESS. What is counted at the open moment, as a CLOSED SET.
#:
#: **ADDED 2026-09-19 because the gate could not see disclosure at all.** The
#: first version read the control's ``aria-expanded`` before the click and
#: again AFTER the dismissal, so nothing observed the open state -- and
#: ``check_closure`` requires those two to be equal, which a successful Escape
#: guarantees whether or not anything ever opened. The gate was structurally
#: unable to distinguish "opened and closed cleanly" from "never opened".
#: Measured and handed over by the wave that took the first sanctioned press.
#:
#: **A CLOSED SET, NEVER A CALLER'S CALLABLE.** A seam that accepts arbitrary
#: code at the open moment is a press seam wearing an observer's clothes: it
#: would hand a caller execution at the single most privileged instant this
#: module has, which is exactly what :data:`SANCTIONED_SHAPES` exists to
#: prevent one line earlier.
#:
#: **PAGE-WIDE, NOT ONLY THE PRESSED CONTROL, and the dialog case decides it.**
#: A witness reading only the pressed control's own ``aria-expanded`` sees
#: ``false`` while a dialog is open elsewhere on the page, and reports real
#: disclosure as a MISS. **A false negative is worse than no witness**, because
#: it manufactures a confident wrong answer where there was honest silence.
WITNESS_SELECTORS: tuple[tuple[str, str], ...] = (
    ("expanded_true", '[aria-expanded="true"]'),
    ("dialogs", '[role="dialog"]'),
    ("menus", '[role="menu"]'),
    ("menuitems", '[role="menuitem"]'),
    ("listboxes", '[role="listbox"]'),
)


def _refuse(reason: str, why: str, *, terminal: bool) -> dict[str, Any]:
    """A refusal that names what it saw and says whether it can ever pass.

    ``reachable_by_this_route`` is the half a caller cannot derive and must not
    guess. See the module docstring: a deferral that will never resolve costs a
    future wave, so NEVER is reported as NEVER rather than as not-yet.
    """
    return {
        "pressed": False,
        "refused": reason,
        "why": why,
        "reachable_by_this_route": not terminal,
    }


def check_address(url: Optional[str]) -> dict[str, Any]:
    """Conditions 1 and the composer/third-party refusals. PURE.

    Separated from the press so the whole gate is testable with no browser at
    all, which is what let this module be written and proven while the ruling's
    own instruction stood: nobody presses anything until the mechanism exists,
    including to test it.
    """
    if not url or not str(url).strip():
        return _refuse(
            "no_address",
            "a press with no address cannot be shown to be on an admitted "
            "page, and this gate refuses what it cannot establish.",
            terminal=True,
        )

    address = str(url).strip()
    if not readonly.is_read_url(address):
        return _refuse(
            "address_not_admitted",
            "the page is not on the read allowlist. A PRESS NEVER EXTENDS "
            "REACH: if the address is refused, every control on it is "
            "refused, and no press is a route to a surface the allowlist "
            "will not admit.",
            terminal=True,
        )

    path = urlsplit(address).path.lower()

    for marker in _COMPOSER_MARKERS:
        if marker in path:
            return _refuse(
                "composer_or_editor",
                "composers and editors are refused for pressing even when "
                "admitted for reading. Opening one may autosave a draft this "
                "server has no reachable surface to detect -- 17 candidate "
                "draft-listing addresses were run against the boundary and "
                "all 17 were refused. A composer is not a disclosure even "
                "when it renders like one.",
                terminal=True,
            )

    segments = [segment for segment in path.split("/") if segment]
    if "in" in segments:
        index = segments.index("in")
        member = segments[index + 1] if index + 1 < len(segments) else ""
        if member not in _SELF_SEGMENTS:
            return _refuse(
                "third_party_surface",
                "a press on another person's surface could register an "
                "interaction visible to them. That is outward-facing, and "
                "outward-facing is not this ruling's to grant.",
                terminal=True,
            )

    return {"pressed": False, "admitted": True}


def check_shape(shape: Optional[str]) -> dict[str, Any]:
    """Condition 2. PURE, and it is exact membership rather than a pattern."""
    if shape not in SANCTIONED_SHAPES:
        return _refuse(
            "shape_not_sanctioned",
            "the control does not match an enumerated disclosure shape. Only "
            f"{list(SANCTIONED_SHAPES)} may be pressed, matched BY ATTRIBUTE "
            "and never by label text -- a label is page text and this server "
            "does not read page text into decisions. A control that is wired "
            "but declares neither attribute can only be matched by its label, "
            "which is why it is refused here and why a listener-presence "
            "matcher is not the remedy: that would admit nearly every "
            "interactive node on the page.",
            terminal=True,
        )
    return {"pressed": False, "shape_ok": True}


def _basis_refusal(
    basis: Optional[dict[str, Any]],
    *,
    read_at_both_ends: Optional[list] = None,
) -> Optional[dict[str, Any]]:
    """CONDITION 3'S URL-DERIVABLE HALF. Returns a refusal, or None. PURE.

    Held in one function because it is consulted from TWO MOMENTS -- before any
    page contact by :func:`check_basis`, and again with the readings in hand by
    :func:`check_counters` -- and a refusal whose reasoning is written twice is
    a refusal whose two copies drift apart. ``read_at_both_ends`` is the only
    difference between them, and it is a difference of EVIDENCE, not of rule:
    after a press the refusal can also say what WAS read and why that is not
    enough.
    """
    if basis is None:
        if read_at_both_ends is None:
            preamble = (
                "no basis is declared for this surface, so condition 3 has no "
                "way to be satisfied here whatever the counters turn out to "
                "say. This is known from the ADDRESS alone and is refused "
                "before anything is touched. "
            )
        else:
            preamble = (
                f"counters {sorted(read_at_both_ends)} were read at both ends "
                "and did not move, which shows they are READABLE and nothing "
                "more. "
            )
        return _refuse(
            "no_sensitivity_basis",
            preamble
            + "Condition 3 is satisfied only by a counter shown SENSITIVE to "
            "this press class, or by an explicit structural argument that no "
            "outward effect is possible from this surface. A merely readable "
            "counter is neither and prices nothing. Declare a basis for this "
            "surface in press.SENSITIVITY_BASES.",
            terminal=False,
        )

    if str(basis.get("kind")) != "structural":
        return None

    # A BARE ASSERTION IS NOT AN ARGUMENT. An entry without its BOUND and its
    # REFUTERS cannot be attacked, and an argument nobody can attack is the
    # shape this package refuses everywhere else.
    missing = [f for f in _STRUCTURAL_REQUIRED if not basis.get(f)]
    if missing:
        return _refuse(
            "structural_argument_incomplete",
            f"this surface declares a structural basis missing {missing}. "
            "Route (b) must state its claims, THE BOUND it does not exceed, "
            "and what would REFUTE it -- otherwise it is an assertion wearing "
            "an argument's clothes.",
            terminal=False,
        )
    return None


def check_basis(url: Optional[str]) -> dict[str, Any]:
    """CONDITION 3, THE HALF ANSWERABLE BEFORE ANY PAGE CONTACT. PURE.

    :data:`SENSITIVITY_BASES` is keyed by SURFACE and :func:`sensitivity_basis`
    is a pure function of the url, so whether condition 3 has ANY way to be
    satisfied here is decided by the address. That makes it a PRE-PRESS
    question, and until 2026-09-21 it was asked after the click. See the module
    docstring and `_audit/2026-09-21-refuse-before-the-click.md`.

    On success the verdict carries the basis KIND and, for route (a), the
    counters the surface declares sensitive -- so a caller knows what its
    ``read_counters`` must return before it builds one, rather than discovering
    ``sensitive_counter_not_read`` after a press.
    """
    basis = sensitivity_basis(url)
    refusal = _basis_refusal(basis)
    if refusal is not None:
        return refusal
    # ``_basis_refusal`` refuses every None basis, so one exists here. Written
    # as ``basis or {}`` rather than as an ``assert``: an assert is removed
    # under ``-O``, and a safety module must not narrow a type with a statement
    # the interpreter is allowed to delete.
    declared = basis or {}
    return {
        "pressed": False,
        "basis_declared": True,
        "basis": str(declared.get("kind")),
        "requires_counters": sorted(declared.get("counters") or ()),
    }


def check_counters(
    before: Optional[dict],
    after: Optional[dict],
    *,
    basis: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Condition 3. PURE, and READABILITY IS NOT ENOUGH.

    Each argument is a mapping of counter name to an integer, or None where the
    counter could not be read. **An unreadable counter is not a zero**, and a
    press it cannot price is refused -- UNMEASURABLE RESOLVES AGAINST THE PRESS.
    """
    if not before or not after:
        return _refuse(
            "no_counter_reading",
            "a press must be SHOWN not to move an outward counter, before and "
            "after. With no reading at either end there is nothing to show, "
            "and unmeasurable resolves AGAINST the press rather than for it.",
            terminal=False,
        )

    unreadable = sorted(
        name for name, value in before.items() if value is None
    ) + sorted(
        name for name, value in after.items() if value is None
    )
    if unreadable:
        return _refuse(
            "counter_unreadable",
            f"these counters did not read: {sorted(set(unreadable))}. An "
            "unreadable counter is not a zero and is never treated as one.",
            terminal=False,
        )

    shared = set(before) & set(after)
    if not shared:
        return _refuse(
            "no_counter_prices_this_press",
            "no counter was read at BOTH ends, so nothing prices this press. "
            "Where no counter can price it, the press is not permitted.",
            terminal=False,
        )

    moved = sorted(name for name in shared if before[name] != after[name])
    if moved:
        return _refuse(
            "counter_moved",
            f"these counters moved across the press: {moved}. A PRESS THAT "
            "MOVES AN OUTWARD COUNTER IS A WRITE, whatever it looked like. "
            "This is the condition that catches the autosave class "
            "empirically rather than by enumeration.",
            terminal=True,
        )

    # CONDITION 3 IS NOT SATISFIED BY READABILITY. See SENSITIVITY_BASES.
    #
    # BOTH OF THESE REFUSALS ARE ALSO TAKEN BEFORE THE PRESS, by
    # :func:`check_basis` -- they are pure functions of the surface. They are
    # still reached here because this function is PUBLIC and a caller can
    # arrive with readings in hand having skipped :func:`evaluate` entirely;
    # what is not duplicated is their reasoning, which lives in one place.
    #
    # THE ORDER IS DELIBERATE AND IS NOT THE SAME AS THE PRE-PRESS ORDER.
    # ``counter_moved`` above is TERMINAL and is a measurement of a real
    # write, so once readings exist it outranks a missing basis: the
    # strongest true thing to say about a press that moved an outward counter
    # is that it was a write, not that the surface lacked paperwork.
    refusal = _basis_refusal(basis, read_at_both_ends=sorted(shared))
    if refusal is not None:
        return refusal

    kind = str(basis.get("kind"))
    if kind == "structural":
        return {
            "pressed": False,
            "counters_ok": True,
            "condition_3_route": "structural_argument",
            # NOT established by measurement. Route (b) is an ARGUMENT, and
            # this field is what stops it being read as the stronger thing.
            "sensitivity_established": False,
            "basis": "structural",
            "priced_by": [],
            "why": basis.get("why"),
            "bound": basis.get("bound"),
            "refuters": list(basis.get("refuters") or ()),
            "weaker_than_route_a": (
                "route (b) is an argument, not a measurement. It is admitted "
                "because (a) is unsatisfiable on this surface, NOT because "
                "the two are equivalent."
            ),
            "read_at_both_ends": sorted(shared),
        }

    named = [name for name in basis.get("counters") or () if name in shared]
    if not named:
        return _refuse(
            "sensitive_counter_not_read",
            f"this surface declares {list(basis.get('counters') or ())} as "
            f"sensitive, and none of them was read at both ends -- only "
            f"{sorted(shared)} was. A basis that names a counter nobody read "
            "prices nothing.",
            terminal=False,
        )

    return {
        "pressed": False,
        "counters_ok": True,
        "condition_3_route": "sensitive_counter",
        # Established, though DERIVED rather than watched: off_state's
        # sensitivity follows from what the label constant MEANS.
        "sensitivity_established": True,
        "basis": "sensitive",
        # NOW MEANS: shown sensitive to this press class AND read at both ends.
        "priced_by": sorted(named),
        "why": basis.get("why"),
        "read_at_both_ends": sorted(shared),
    }


def witness_verdict(
    before: Optional[dict], after: Optional[dict], *, control_open: Any = None
) -> dict[str, Any]:
    """DID ANYTHING ACTUALLY OPEN? A READING, NEVER A GATE. PURE.

    **NOT A FIFTH CONDITION, DELIBERATELY.** Permission stays decided on safety
    alone. Folding disclosure into permission would turn a reading into a gate
    and refuse a perfectly safe press for the sin of being uninformative -- and
    "this press disclosed nothing" is a fact about the control, not a reason the
    press should not have happened.

    **THE PAIR IS THE POINT.** A page-wide count means nothing without its
    baseline: the live analytics page already carried nine ``[aria-expanded]``
    nodes before any press. So the same readings are taken at both moments and
    compared, rather than a single count being read as evidence.

    Returns ``disclosed`` True / False / None, where **None is
    UNDETERMINED and is not False** -- a reading that did not happen is not a
    reading that saw nothing.
    """
    if not before or not after:
        return {
            "disclosed": None,
            "why": (
                "no witness reading at one or both moments, so whether "
                "anything opened is UNDETERMINED. That is not the same as "
                "nothing having opened."
            ),
        }
    shared = sorted(set(before) & set(after))
    if not shared:
        return {
            "disclosed": None,
            "why": "no reading was taken at both moments; nothing to compare.",
        }
    moved = sorted(name for name in shared if before[name] != after[name])
    if moved:
        return {"disclosed": True, "moved": moved, "witnessed_by": shared}
    if control_open is not None and str(control_open).lower() == "true":
        # The control says it is open even though no page count moved --
        # believed, because a control reporting its own state is the narrower
        # and more direct claim.
        return {
            "disclosed": True,
            "moved": ["control_aria_expanded"],
            "witnessed_by": shared,
        }
    # THE WITNESS MAY NOT SPEAK FOR THE VERDICT. This text used to read "the
    # press was permitted and safe" -- a claim about PERMISSION, which the
    # witness never sees and which is FALSE every time the witness rides on a
    # refusal. Measured 2026-09-21: a press refused for ``no_counter_reading``
    # came back carrying "the press was permitted and safe". The module
    # docstring is emphatic that the witness never DECIDES permission; a
    # surface may not print a claim it cannot derive, so it must not REPORT it
    # either.
    return {
        "disclosed": False,
        "moved": [],
        "witnessed_by": shared,
        "why": (
            "nothing this witness counts changed between the press and the "
            "dismissal. That is a MISS rather than a failure: whatever the "
            "verdict decided, this press disclosed nothing the witness set "
            "can see."
        ),
    }


def check_closure(expanded_before: Any, expanded_after: Any) -> dict[str, Any]:
    """Condition 4. PURE.

    A disclosure left open is a change to the rendered state the next reader
    inherits, so the toggle must read as it did before the press.
    """
    if expanded_before is None or expanded_after is None:
        return _refuse(
            "closure_unverifiable",
            "the control's expanded state did not read at one end, so the "
            "closure cannot be verified. An unverified closure is treated as "
            "an open one.",
            terminal=False,
        )
    if expanded_before != expanded_after:
        return _refuse(
            "not_restored",
            f"the control was {expanded_before!r} before and "
            f"{expanded_after!r} after. The page was not left as it was "
            "found.",
            terminal=False,
        )
    return {"pressed": False, "closed": True}


def evaluate(
    *,
    url: Optional[str],
    shape: Optional[str],
    before: Optional[dict] = None,
    after: Optional[dict] = None,
    expanded_before: Any = None,
    expanded_after: Any = None,
    already_pressed: bool = False,
    reading: Optional[str] = None,
    scope: Optional[str] = None,
) -> dict[str, Any]:
    """THE WHOLE GATE, PURE AND BROWSER-FREE. Conjunctive, in order.

    **THE ORDER IS PART OF THE CONTRACT.** Address first, shape second, then
    the caller's two other KEYS (``reading`` and ``scope``, each checked
    against its closed table), the BASIS after them, and only then anything
    that requires the press to have happened. A caller that runs this with no
    counters gets a refusal BEFORE pressing, which is the point: the pre-press
    half can be evaluated on its own and must pass before any control is
    touched.

    ``already_pressed`` SAYS WHICH MOMENT THIS IS instead of inferring it. The
    pre-press branch used to be selected by ``before is None and after is
    None``, which a ``read_counters`` returning ``None`` reproduces exactly
    AFTER a real click -- so a press that had happened came back as a pre-press
    permit with conditions 3 and 4 never evaluated. :func:`disclose` passes
    True. See the module docstring.

    Returns the first refusal, or a permit. It never raises: one unusable
    control is not an error.
    """
    verdict = check_address(url)
    if verdict.get("refused"):
        return verdict
    verdict = check_shape(shape)
    if verdict.get("refused"):
        return verdict
    # THE CALLER'S OTHER TWO KEYS, both closed tables, both pure functions of
    # the arguments -- so both are refused here, before the basis and before
    # any contact, on the same footing as an off-list shape.
    verdict = check_reading(url, reading)
    if verdict.get("refused"):
        return verdict
    verdict = check_scope(scope)
    if verdict.get("refused"):
        return verdict

    if not already_pressed and before is None and after is None:
        # THE PRE-PRESS VERDICT: everything checkable without acting -- AND
        # CONDITION 3'S BASIS IS CHECKABLE WITHOUT ACTING, which is the whole
        # of the 2026-09-21 repair. A surface with no declared basis can only
        # ever end in ``no_sensitivity_basis``, so a permit here was a promise
        # the gate had already decided not to keep.
        verdict = check_basis(url)
        if verdict.get("refused"):
            return verdict
        still_to_show = ["counters_unmoved", "closure_verified"]
        if verdict.get("basis") == "sensitive":
            # Route (a) can still fail on the READING -- a basis naming a
            # counter nobody read prices nothing -- so the permit says so
            # rather than leaving the caller to discover it after a press.
            still_to_show.insert(0, "sensitive_counter_read")
        permit: dict[str, Any] = {
            "pressed": False,
            "permitted_to_attempt": True,
            "basis": verdict.get("basis"),
            "requires_counters": verdict.get("requires_counters"),
            "still_to_show": still_to_show,
        }
        # ECHOED ONLY WHEN ASKED FOR, so the permit every existing caller
        # receives is byte-for-byte the permit it received before these keys
        # existed.
        if reading is not None:
            permit["reading"] = reading
        if scope is not None:
            permit["scope"] = scope
        return permit

    # THE BASIS IS RESOLVED FROM THE SURFACE, never handed in. See
    # SENSITIVITY_BASES: a basis a caller can assert is a basis a caller can
    # invent, and "no outward effect is possible here" is exactly the claim
    # somebody in a hurry would make about a surface they had not read.
    verdict = check_counters(before, after, basis=sensitivity_basis(url))
    if verdict.get("refused"):
        return verdict
    priced_by = verdict.get("priced_by")
    basis_kind = verdict.get("basis")
    basis_why = verdict.get("why")
    read_at_both_ends = verdict.get("read_at_both_ends")
    verdict = check_closure(expanded_before, expanded_after)
    if verdict.get("refused"):
        return verdict

    return {
        "pressed": True,
        "permitted": True,
        # WHICH OF THE TWO WAYS CONDITION 3 WAS SATISFIED. The ruling requires
        # the verdict to say which, because "priced" meant two different
        # things and only one of them was ever established.
        "basis": basis_kind,
        "basis_why": basis_why,
        "priced_by": priced_by,
        # Kept separate and deliberately NOT called priced_by: these are the
        # counters READ at both ends, which is a weaker fact and used to be
        # reported as the stronger one.
        "read_at_both_ends": read_at_both_ends,
        "shape": shape,
    }


async def disclose(
    page: Any,
    *,
    shape: str,
    index: int = 0,
    read_counters: Optional[Callable] = None,
    reading: Optional[str] = None,
    scope: Optional[str] = None,
) -> dict[str, Any]:
    """Press ONE enumerated disclosure control, or refuse and touch nothing.

    ``shape`` is a KEY FROM :data:`SANCTIONED_SHAPES`, never a selector. An
    arbitrary string cannot become a press target.

    ``reading`` and ``scope`` are KEYS too, from :data:`OPEN_READINGS` and
    :data:`PRESS_SCOPES`, and both are checked before anything is touched.
    ``scope`` narrows where the ``index``-th control is looked for; ``reading``
    is taken immediately before the click and again at the open moment, and
    rides on the verdict as ``reading`` beside the witness, deciding nothing.
    Leave both ``None`` and this is the gate exactly as it was.

    ``read_counters`` is an async callable returning a MAPPING of counter name
    to int-or-None. It is REQUIRED: with no way to price the press, condition 3
    refuses before anything is touched. **IT MUST RETURN A MAPPING, NEVER
    ``None``** -- a reader that returns ``None`` used to make the post-press
    verdict indistinguishable from a pre-press one, which disarmed conditions 3
    and 4 after a real click. ``already_pressed`` closes that; a ``None``
    reading is now ``no_counter_reading``, which is what it always meant.

    **THE PRE-PRESS GATE RUNS FIRST AND RETURNS BEFORE ANY CONTROL IS
    TOUCHED.** That ordering is the difference between a guard and a report,
    and as of 2026-09-21 the sentence is TRUE OF CONDITION 3 AS WELL: the
    pre-press verdict consults :func:`check_basis`, so a surface with no
    declared sensitivity basis is refused with the page never asked for a
    locator. It was not true before, and the surface where that was measured
    lists other people.
    """
    pre = evaluate(
        url=getattr(page, "url", None), shape=shape, reading=reading, scope=scope
    )
    if pre.get("refused"):
        return pre

    if read_counters is None:
        return _refuse(
            "no_counter_reader_supplied",
            "condition 3 requires the press to be SHOWN not to move an "
            "outward counter. Without a reader there is no way to show it, "
            "and unmeasurable resolves against the press.",
            terminal=False,
        )

    # THE CANDIDATES. With no scope this is the page-wide locator, built by the
    # same two calls it always was; with one, the shape is looked for only
    # inside the scope's container. check_scope has already refused any key
    # outside the table, so the entry exists whenever a scope was named.
    scope_selector = (press_scope(scope) or {}).get("selector") if scope else None

    def _candidates():
        if scope_selector:
            return page.locator(scope_selector).locator(shape)
        return page.locator(shape)

    locator = _candidates().nth(index)
    reading_before: Optional[dict[str, Any]] = None
    reading_open: Optional[dict[str, Any]] = None
    try:
        if not int(await _candidates().count()):
            return _refuse(
                "shape_absent_on_this_page",
                "the page draws no control of this shape. That is a fact "
                "about this page, not about the shape.",
                terminal=False,
            )
        expanded_before = await locator.get_attribute("aria-expanded")
        # THE BASELINE HALF OF THE WITNESS, taken before anything is pressed.
        # A page-wide count is meaningless without it.
        witness_before = await _read_witness(page)
        # AND THE BASELINE HALF OF THE READING, for the witness's reason: a
        # phrase already on the page is not something the press disclosed.
        if reading is not None:
            reading_before = await _take_reading(page, reading)
        before = await read_counters()
        await locator.click(timeout=CLICK_TIMEOUT_MS)
        after = await read_counters()
        # THE OBSERVATION AT THE OPEN MOMENT, and it is the whole of the fix.
        # This is the ONLY instant at which disclosure exists to be seen: the
        # dismissal below destroys it, and every earlier version of this
        # function read the control's state only before the press and after
        # the dismissal, so it could not tell an open-and-closed from a
        # never-opened.
        witness_after = await _read_witness(page)
        control_open = await locator.get_attribute("aria-expanded")
        # THE READING AT THE OPEN MOMENT, BEFORE THE DISMISSAL -- the one place
        # it can be taken. It cannot raise (see _take_reading), so it cannot
        # skip the Escape below.
        if reading is not None:
            reading_open = await _take_reading(page, reading)
        # CLOSE IT. Escape first, because it is the dismissal this repository's
        # probes already use and it closes a menu that has no toggle.
        await page.keyboard.press("Escape")
        expanded_after = await locator.get_attribute("aria-expanded")
    except Exception as exc:  # noqa: BLE001
        # ONLY THE EXCEPTION TYPE. A library's message is composed by code
        # nobody here controls and has been measured carrying selectors and
        # urls.
        return _refuse(
            "press_failed",
            f"the press raised {type(exc).__name__}. Nothing is claimed about "
            "what the page did; a failure is not a refusal and is not a "
            "success.",
            terminal=False,
        )

    verdict = evaluate(
        url=getattr(page, "url", None),
        shape=shape,
        before=before,
        after=after,
        expanded_before=expanded_before,
        expanded_after=expanded_after,
        # THE PRESS HAS HAPPENED. Said rather than inferred: a reader that
        # returns None makes ``before``/``after`` indistinguishable from a
        # pre-press call, and the gate then skipped conditions 3 and 4 and
        # reported a permit for a click it had already taken.
        already_pressed=True,
        reading=reading,
        scope=scope,
    )
    # THE WITNESS RIDES ALONGSIDE THE VERDICT AND NEVER DECIDES IT. It is
    # attached to a refusal too, because "the press was refused on its
    # counters AND nothing opened" is a different fact from "refused", and a
    # reader who has to infer which one they have will infer wrong.
    verdict["witness"] = witness_verdict(
        witness_before, witness_after, control_open=control_open
    )
    # THE READING RIDES THE SAME WAY, and for the same two reasons: it never
    # decides the verdict, and it is attached to a refusal as well -- where it
    # is evidence about the press and NOT a delivered read.
    if reading is not None:
        verdict["reading"] = reading_verdict(reading, reading_before, reading_open)
    return verdict


async def _take_reading(page: Any, key: str) -> dict[str, Any]:
    """One reading of a table entry's phrases. NEVER RAISES.

    Returns ``{"read": True, "terms": {term: numeral}, ...}`` or
    ``{"read": False, "unreadable": <exception TYPE>}``. It must not raise
    because it runs between the click and the Escape: an exception here would
    skip the dismissal and leave a disclosure open for the next reader.

    The page answers through ``dom.read_count_lines`` -- a declared script at a
    waived call site -- with phrase POSITIONS and integers. Imported here
    rather than at module level so this module stays importable, and testable,
    with no browser-facing module loaded at all.
    """
    entry = open_reading(key) or {}
    pairs = tuple(entry.get("phrases") or ())
    try:
        from linkedin_server import company_root, dom

        raw = await dom.read_count_lines(
            page,
            phrases=[phrase for _term, phrase in pairs],
            hidden=dom.CARD_HIDDEN_SELECTOR,
        )
        terms: dict[str, Any] = {}
        for match in (raw or {}).get("matches") or []:
            position = int(match.get("phrase", -1))
            if not 0 <= position < len(pairs):
                # A POSITION OUTSIDE THE LIST IS REFUSED, never clamped onto
                # the first phrase -- that would rename one term to another.
                continue
            term = pairs[position][0]
            numeral = company_root.term_for(int(match.get("shape", 0)))
            value = (
                int(match.get("value", 0))
                if numeral in ("plain_digits", "grouped_digits")
                else None
            )
            prior = terms.get(term)
            # ONE TERM MAY HAVE SEVERAL PHRASES. A match that carries a number
            # beats one that does not; otherwise the first match stands.
            if prior is None or (prior["value"] is None and value is not None):
                terms[term] = {"numeral": numeral, "value": value}
        return {
            "read": True,
            "terms": terms,
            # THE TWO SIZES OF WHAT THE WALK SAW, so a VOCABULARY MISS is
            # visible: a press that brought ten new lines into view and matched
            # none of them reads differently from one that brought nothing.
            "elements": _as_int((raw or {}).get("elements")),
            "chunks": _as_int((raw or {}).get("chunks")),
            "hidden_skipped": _as_int((raw or {}).get("hidden_skipped")),
            "chunks_capped": bool((raw or {}).get("chunks_capped")),
        }
    except Exception as exc:  # noqa: BLE001 - a reading never breaks a press
        return {"read": False, "unreadable": type(exc).__name__}


def _as_int(value: Any) -> int:
    """A count or 0, for the two integer fields a reading reports. PURE."""
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def reading_verdict(
    key: str, before: Optional[dict], open_: Optional[dict]
) -> dict[str, Any]:
    """WHAT THE PRESS BROUGHT INTO VIEW, from the two readings. PURE.

    ``appeared`` is the terms read at the open moment and NOT before the click
    -- the only terms the press can be credited with. ``held`` were there at
    both moments, so the press cannot be credited with them; ``gone`` were
    there before and not while open. **``appeared`` is None, never empty,
    when either moment did not read**: a reading that did not happen is not a
    reading that found nothing.
    """
    out: dict[str, Any] = {"key": key, "before": before, "open": open_}
    if not before or not open_ or not before.get("read") or not open_.get("read"):
        out.update(
            {
                "appeared": None,
                "held": None,
                "gone": None,
                "new_lines": None,
                "new_elements": None,
            }
        )
        return out
    was = set((before.get("terms") or {}))
    now = set((open_.get("terms") or {}))
    out.update(
        {
            "appeared": sorted(now - was),
            "held": sorted(now & was),
            "gone": sorted(was - now),
            # HOW MUCH ARRIVED, whatever it said. ``appeared`` empty with
            # ``new_lines`` large is a VOCABULARY MISS, not an empty disclosure;
            # both zero is a press that brought nothing a walk can see. A
            # capped walk makes the line count a floor, and says so.
            "new_lines": _as_int(open_.get("chunks")) - _as_int(before.get("chunks")),
            "new_elements": (
                _as_int(open_.get("elements")) - _as_int(before.get("elements"))
            ),
            "lines_capped": bool(before.get("chunks_capped") or open_.get("chunks_capped")),
        }
    )
    return out


async def _read_witness(page: Any) -> dict[str, Any]:
    """Count the closed witness set. Returns None per reading that failed.

    **An unreadable count is not a zero**, for the same reason an unreadable
    counter is not one: a reading that did not happen and a reading that saw
    nothing are different facts, and only one of them is evidence.
    """
    out: dict[str, Any] = {}
    for name, selector in WITNESS_SELECTORS:
        try:
            out[name] = int(await page.locator(selector).count())
        except Exception:  # noqa: BLE001
            out[name] = None
    return out


#: The one timeout, named here rather than inline so a reviewer finds it.
CLICK_TIMEOUT_MS = 5_000
