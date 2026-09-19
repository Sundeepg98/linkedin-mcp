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
    if basis is None:
        return _refuse(
            "no_sensitivity_basis",
            f"counters {sorted(shared)} were read at both ends and did not "
            "move, which shows they are READABLE and nothing more. Condition "
            "3 is satisfied only by a counter shown SENSITIVE to this press "
            "class, or by an explicit structural argument that no outward "
            "effect is possible from this surface. A merely readable counter "
            "is neither and prices nothing. Declare a basis for this surface "
            "in press.SENSITIVITY_BASES.",
            terminal=False,
        )

    kind = str(basis.get("kind"))
    if kind == "structural":
        return {
            "pressed": False,
            "counters_ok": True,
            "basis": "structural",
            "priced_by": [],
            "why": basis.get("why"),
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
    return {
        "disclosed": False,
        "moved": [],
        "witnessed_by": shared,
        "why": (
            "nothing this witness counts changed between the press and the "
            "dismissal. That is a MISS rather than a failure: the press was "
            "permitted and safe, and it disclosed nothing this set can see."
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
) -> dict[str, Any]:
    """THE WHOLE GATE, PURE AND BROWSER-FREE. Conjunctive, in order.

    **THE ORDER IS PART OF THE CONTRACT.** Address first, shape second, and only
    then anything that requires the press to have happened. A caller that runs
    this with no counters gets a refusal BEFORE pressing, which is the point:
    the pre-press half can be evaluated on its own and must pass before any
    control is touched.

    Returns the first refusal, or a permit. It never raises: one unusable
    control is not an error.
    """
    verdict = check_address(url)
    if verdict.get("refused"):
        return verdict
    verdict = check_shape(shape)
    if verdict.get("refused"):
        return verdict

    if before is None and after is None:
        # The PRE-PRESS verdict: everything checkable without acting.
        return {
            "pressed": False,
            "permitted_to_attempt": True,
            "still_to_show": ["counters_unmoved", "closure_verified"],
        }

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
) -> dict[str, Any]:
    """Press ONE enumerated disclosure control, or refuse and touch nothing.

    ``shape`` is a KEY FROM :data:`SANCTIONED_SHAPES`, never a selector. An
    arbitrary string cannot become a press target.

    ``read_counters`` is an async callable returning a mapping of counter name
    to int-or-None. It is REQUIRED: with no way to price the press, condition 3
    refuses before anything is touched.

    **THE PRE-PRESS GATE RUNS FIRST AND RETURNS BEFORE ANY CONTROL IS
    TOUCHED.** That ordering is the difference between a guard and a report.
    """
    pre = evaluate(url=getattr(page, "url", None), shape=shape)
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

    locator = page.locator(shape).nth(index)
    try:
        if not int(await page.locator(shape).count()):
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
    )
    # THE WITNESS RIDES ALONGSIDE THE VERDICT AND NEVER DECIDES IT. It is
    # attached to a refusal too, because "the press was refused on its
    # counters AND nothing opened" is a different fact from "refused", and a
    # reader who has to infer which one they have will infer wrong.
    verdict["witness"] = witness_verdict(
        witness_before, witness_after, control_open=control_open
    )
    return verdict


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
