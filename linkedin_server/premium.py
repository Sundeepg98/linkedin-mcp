"""Is the account entitled to Premium -- and which states does that NOT settle?

THIS MODULE SHIPS LOGIC THAT ALREADY RAN LIVE, ONCE, ELSEWHERE. Every needle
tuple and the verdict table below are lifted from
``scripts/_probe_premium_entitlement.py``, which opened ``/premium/my-premium/``
under CDP attach and produced them. **THIS MODULE ITSELF OPENS NOTHING AND
NAVIGATES NOWHERE.** Like :func:`events.read_events_home` and
:func:`newsletters.read_newsletter_subscriptions`, it reads a page it is
handed; the caller owns reaching :data:`PREMIUM_URL` and owns whatever
invitation-badge cost accounting that load requires. No new browser session
was opened to build this file -- it packages a proven probe's logic into the
reader/shaper pair the rest of this package ships, so the logic lives in a
module the server can import instead of only in a hand-run script.

## THE THREE-STATE PROBLEM THIS EXISTS TO NARROW, AND IT DOES NOT CLOSE IT

Three states were named about Premium job-posting features and only one was
refuted by the probe's live load:

    A  not entitled
    B  entitled, and the panel is simply not drawn on those postings
    C  entitled, the panel IS drawn, and the reader could not see it

**A LOAD OF ``/premium/my-premium/`` SEPARATES A FROM {B, C} AND DOES NOTHING
ABOUT B VERSUS C.** Said plainly because a number that silently picks one state
is worse than no number. Entitlement lives on this page; whether a panel
renders on a JOB POSTING is a fact about a different surface, and no reading
here can reach it. That is why :func:`premium_entitlement` prints the split on
every branch it can return, including the entitled one -- a caller must not be
able to read "entitled" and quietly assume the panel renders anywhere.

## WHAT THIS MODULE MAY SAY, AND IT IS NOT PAGE TEXT

COUNTS AND OUR OWN AUTHORED STRINGS ONLY. No accessible name, no label, no url,
no plan name, no price, no date leaves :func:`read_premium_surface`.
``tests/test_page_text_is_never_printed.py`` is a real, pinned guard, and this
module adds zero sites to its inventory: every observable it returns is either
an integer, a boolean, ``None``, or one of the two needle tuples this file
itself authors -- never the control text that matched one.

## WHY IT IS A MODULE AND NOT A BLOCK IN ``dom.py``

``dom.py`` is contended by other agents at the moment this was written, and
``git commit --only`` does not protect a neighbour's uncommitted LINES inside a
path you name -- the same reason ``events.py`` and ``newsletters.py`` shipped
standalone rather than as additions to that file. This module's read is a
handful of ``page.locator`` calls with no script injection, so nothing here
needs the ``dom.py``-only ``page.evaluate`` waiver; it could move into
``dom.py`` later with no change in shape, only in address.

## THE SHAPE OF THE CONTRACT

:func:`read_premium_surface` is the DOM read and returns a RAW READING: counts,
a tuple of our own needle strings that matched, and an error slot. It is the
only place page text exists in this process, and it does not leave the
function -- matched control text is folded into a per-needle tally and
discarded; only the tally's shape survives.

:func:`premium_entitlement` is a PURE function -- no page, no I/O -- that takes
that raw reading and names one of five states: ``entitled``, ``not_entitled``,
``ambiguous``, ``unmatched``, or ``error``. ``ambiguous`` and ``unmatched`` are
both reachable and both real answers: a reading that cannot separate two
states, or that matched neither vocabulary at all, must say so in its own
payload rather than being rounded up to a state it did not earn.
"""
from __future__ import annotations

from typing import Any, Optional

from linkedin_server.config import BASE_URL
from linkedin_server.dom import ELEMENT_READ_TIMEOUT_MS

#: THE ADDRESS, built from the module constant and never from anything a page
#: chose -- the form ``tests/test_navigation_is_never_derived.py`` recognises.
#: Admitted to the read allowlist, root only, no query and no sub-path
#: (``linkedin_server/readonly.py``): ``^https://www\\.linkedin\\.com/premium/
#: my-premium/?$``.
PREMIUM_URL = f"{BASE_URL}/premium/my-premium/"

#: Every clickable control on the page. The same aim
#: ``scripts/_probe_premium_entitlement.py`` used: not a class, not a position,
#: because this page's structural classes are not something this package has
#: measured and an accessible-name sweep over every link and button does not
#: need them.
_CONTROL_SELECTOR = "a, button"

#: THE CAP ON HOW MANY CONTROLS ONE READ WILL SCAN, carried over unchanged from
#: the probe. A page with more than this many links and buttons is scanned
#: only up to the cap; ``controls_scanned`` in the raw reading says how many
#: actually were, so a caller can tell a capped read from a complete one.
_MAX_CONTROLS_SCANNED = 400

#: Needles THIS REPOSITORY AUTHORS, matched case-folded against accessible
#: names read off the page. Counting them names nobody, because the count is
#: of our own strings.
#:
#: TWO FAMILIES, AND THE PAIRING IS THE INSTRUMENT. A page offering to SELL a
#: subscription and a page offering to MANAGE one are different pages wearing
#: the same address. Either family alone is ambiguous -- an upsell can appear
#: beside a live subscription, and a "manage" verb can appear on a marketing
#: page -- so :func:`premium_entitlement` reads the PAIR and refuses to
#: collapse a tie.
ENTITLED_NEEDLES: tuple[str, ...] = (
    "cancel subscription",
    "cancel premium",
    "manage subscription",
    "manage plan",
    "your plan",
    "billing",
    "next payment",
    "subscription details",
)
UNENTITLED_NEEDLES: tuple[str, ...] = (
    "start free trial",
    "start your free trial",
    "try premium",
    "retry premium",
    "reactivate",
    "choose plan",
    "select plan",
    "upgrade to premium",
)

#: Both families, for the one loop that tallies against all of them at once.
_ALL_NEEDLES: tuple[str, ...] = ENTITLED_NEEDLES + UNENTITLED_NEEDLES


async def read_premium_surface(page: Any) -> dict[str, Any]:
    """Count our own needles among this page's controls. Publishes no text.

    LOCATOR-ONLY, no ``page.evaluate`` and therefore no ``# readonly-ok``
    waiver. Reads every ``a``/``button`` accessible name into a LOCAL,
    case-folds it, and tallies which of :data:`ENTITLED_NEEDLES` and
    :data:`UNENTITLED_NEEDLES` matched as a substring. That local is the one
    place in this process a control's own text exists, and it does not escape
    this function: what returns is a count per family and the tuple of
    NEEDLE NAMES that matched -- strings this file authors, never a string the
    page authors.

    RETURNS, and every field is an integer, a boolean, ``None``, or one of our
    own needle strings::

        {
          "controls_scanned": int,          # <= _MAX_CONTROLS_SCANNED
          "entitled_hits": int,             # total matches, ENTITLED_NEEDLES
          "unentitled_hits": int,           # total matches, UNENTITLED_NEEDLES
          "needles_fired": tuple[str, ...], # sorted, a subset of _ALL_NEEDLES
          "error": str | None,
        }

    A CONTROL THAT CANNOT BE READ IS SKIPPED, NOT FATAL. The probe this is
    lifted from treats one unreadable control (a detached node, a timeout on a
    single ``inner_text``) as nothing to report and moves on -- the same
    discipline ``newsletters.read_newsletter_subscriptions`` uses for a whole
    read and ``events.read_events_home`` uses per field. Only a failure of the
    INITIAL ``count()`` -- the page has no usable ``a``/``button`` locator at
    all -- is fatal, and it is reported through ``error`` rather than raised,
    so a caller sees a shaped refusal instead of a traceback.
    """
    out: dict[str, Any] = {
        "controls_scanned": 0,
        "entitled_hits": 0,
        "unentitled_hits": 0,
        "needles_fired": (),
        "error": None,
    }
    try:
        controls = page.locator(_CONTROL_SELECTOR)
        total = int(await controls.count())
    except Exception as error:  # noqa: BLE001
        out["error"] = f"{type(error).__name__}: {error}"
        return out

    scanned = min(total, _MAX_CONTROLS_SCANNED)
    tally: dict[str, int] = {needle: 0 for needle in _ALL_NEEDLES}
    for index in range(scanned):
        try:
            name = (
                await controls.nth(index).inner_text(
                    timeout=ELEMENT_READ_TIMEOUT_MS
                )
            ) or ""
        except Exception:  # noqa: BLE001
            continue
        folded = name.strip().lower()
        if not folded:
            continue
        for needle in _ALL_NEEDLES:
            if needle in folded:
                tally[needle] += 1

    out["controls_scanned"] = scanned
    out["entitled_hits"] = sum(tally[needle] for needle in ENTITLED_NEEDLES)
    out["unentitled_hits"] = sum(tally[needle] for needle in UNENTITLED_NEEDLES)
    out["needles_fired"] = tuple(
        sorted(needle for needle in _ALL_NEEDLES if tally[needle])
    )
    return out


def premium_entitlement(reading: Optional[dict[str, Any]]) -> dict[str, Any]:
    """Name the STATE from a raw reading, and refuse to collapse a tie.

    PURE. No page, no I/O -- takes exactly what :func:`read_premium_surface`
    returns (or an equivalent hand-built dict, which is how this function is
    tested) and never anything else.

    FIVE STATES, and both of the unhappy ones are real answers rather than
    failures to reach a happy one:

        entitled       management verbs present, no sales verbs
        not_entitled   sales verbs present, no management verbs
        ambiguous      BOTH families present -- an upsell can sit beside a
                       live subscription, so this does not resolve and does
                       not guess
        unmatched      NEITHER family matched -- a reading about this
                       INSTRUMENT (the aim may be wrong, or the page draws
                       neither vocabulary), not about the account
        error          the reading itself carried a failure -- see below

    **``error`` NEVER FALLS THROUGH TO ``not_entitled``.** A failed read has
    seen no needles at all, and reporting "not entitled" from a read that
    never actually checked is the exact failure mode this module exists to
    avoid: it would read as "he has no Premium" on a day the page simply did
    not load. So ``error`` is checked first and returns before any hit count
    is examined, whatever ``entitled_hits``/``unentitled_hits`` happen to hold
    in a reading that also carries an error.

    ``strength`` is ``"thin"`` when the total hit count is 1 or fewer, and
    ``"corroborated"`` otherwise -- except on ``error``, where no reading was
    taken and ``strength`` is ``None`` because there is nothing to grade.
    ``ambiguous`` can never be thin: it requires a hit in EACH family, so its
    total is always at least 2.

    ``settles`` and ``leaves_open`` are literal strings THIS FUNCTION AUTHORS,
    present and non-empty on every branch. Entitlement lives on
    ``/premium/my-premium/``; whether a panel renders on a JOB POSTING is a
    fact about a different surface, and every branch's ``leaves_open`` says so
    -- the ``entitled`` branch names the B-versus-C split explicitly, because
    that is the one branch where a caller might otherwise assume the panel
    renders somewhere just because the account is entitled to it.
    """
    seen = dict(reading or {})
    error = seen.get("error")
    entitled_hits = int(seen.get("entitled_hits") or 0)
    unentitled_hits = int(seen.get("unentitled_hits") or 0)

    def _verdict(
        state: str, strength: Optional[str], settles: str, leaves_open: str
    ) -> dict[str, Any]:
        return {
            "state": state,
            "strength": strength,
            "entitled_hits": entitled_hits,
            "unentitled_hits": unentitled_hits,
            "settles": settles,
            "leaves_open": leaves_open,
        }

    if error:
        return _verdict(
            "error",
            None,
            settles=(
                "nothing -- the read itself failed before any control could "
                "be counted, so no needle vocabulary was even checked."
            ),
            leaves_open=(
                "everything: state A (not entitled) versus state B "
                "(entitled, panel not drawn on a job posting) versus state C "
                "(entitled, panel drawn but unread on a job posting) all "
                "remain exactly as unmeasured as before this read was "
                "attempted."
            ),
        )

    total = entitled_hits + unentitled_hits
    strength = "thin" if total <= 1 else "corroborated"

    if entitled_hits and not unentitled_hits:
        return _verdict(
            "entitled",
            strength,
            settles=(
                "state A (not entitled) is REFUTED -- management verbs are "
                "present on /premium/my-premium/ with no sales verbs "
                "alongside them."
            ),
            leaves_open=(
                "state B (entitled, and the panel is simply not drawn on a "
                "job posting) versus state C (entitled, the panel IS drawn "
                "on a job posting, and the reader could not see it). That is "
                "a fact about a DIFFERENT surface -- a job posting -- and no "
                "reading of /premium/my-premium/ can reach it."
            ),
        )
    if unentitled_hits and not entitled_hits:
        return _verdict(
            "not_entitled",
            strength,
            settles=(
                "state A (not entitled) -- sales verbs are present on "
                "/premium/my-premium/ with no management verbs alongside "
                "them, so this reading finds no live Premium entitlement."
            ),
            leaves_open=(
                "whether a control this reading's needles do not name would "
                "say otherwise, and whether a job-posting panel renders at "
                "all -- moot while state A holds, but unmeasured by this "
                "module either way, because it never opens a job posting."
            ),
        )
    if entitled_hits and unentitled_hits:
        return _verdict(
            "ambiguous",
            strength,
            settles=(
                "nothing -- both the management vocabulary and the sales "
                "vocabulary are present on /premium/my-premium/, and this "
                "reading refuses to guess which one wins."
            ),
            leaves_open=(
                "state A (not entitled) versus state B/state C (entitled), "
                "which stays open because an upsell can sit beside a live "
                "subscription and a management verb can appear on a "
                "marketing page; a job-posting panel read is unreachable "
                "from here regardless of how this resolves."
            ),
        )
    return _verdict(
        "unmatched",
        strength,
        settles=(
            "nothing about the account -- neither the management vocabulary "
            "nor the sales vocabulary matched anything on "
            "/premium/my-premium/, which is a reading about THIS INSTRUMENT "
            "(the aim may be wrong, or the page drew neither vocabulary), "
            "not about entitlement."
        ),
        leaves_open=(
            "state A versus state B/state C stays exactly as open as before "
            "this read, and so does whether a job-posting panel renders -- a "
            "different surface this reading never opens."
        ),
    )
