"""IS THE PAGE ``/in/me/`` LANDED ON HIS OWN PROFILE? Two signals and one rule.

## WHY THIS MODULE EXISTS

**MEASURED 2026-11-25, the live lane's session 11:** LinkedIn's ``/in/me/``
redirect stopped carrying ``isSelfProfile``. Both landings that night reached
his member path with NO query string at all, and the page itself drew the
marker nowhere -- the 28 ``/in/<member>/?isSelfProfile=...`` links every older
self capture carries are plain ``/in/<member>/`` links on the new landing
(``_audit/2026-11-26-selfprofile26.md`` section 1). Every gate that read the
marker refused his own profile: ``server._goto_self_profile_asserted`` (the two
editor tools, ``linkedin_my_activity_items``, the census's item veto),
``press.self_landing``, and the live harness's two self-profile steps.

## THE TWO SIGNALS

1. **THE URL MARKER**, LinkedIn's ``isSelfProfile`` on the landed url. Kept as
   an accepted signal exactly as it was read: ``true`` asserts self, any other
   value is LinkedIn saying no, and its absence is not an answer.
2. **THE EDIT CONTROLS FOR THE LANDED MEMBER** -- an ``<a>`` with an accessible
   name whose ``href`` is ``/in/<the landed member>/edit/...`` on LinkedIn's
   own host. LinkedIn draws an editor link for a profile on that profile's
   OWNER's view of it and on nobody else's. MEASURED over every capture on
   disk before anything was built on it (section 2 of the record): 4 on the
   new landing, 4 on each of the three older self captures (sessions 2, 3 and
   8), 0 on each of the three tracked captures of another member's profile.

**IT IS A RELATION, NOT A PRESENCE.** The control must name the member the url
landed on. LinkedIn also draws "complete your profile" links to the VIEWER's
own editor on pages that are not his profile (three tracked captures carry
one); on a stranger's profile such a link names the viewer, not the page, and
counts AGAINST it here. And ``/in/me/edit/...`` -- the viewer's own editor
under the self alias -- counts neither way: it says who is signed in, not
whose page this is.

## THE RULE, and every way it refuses

* the marker says ``true``: SELF, as before.
* the marker says anything else: NOT SELF, settled, never retried -- as before.
* NO MARKER, and the page draws at least one edit control for the landed
  member and NO edit route for any other member: SELF, by structure.
* no marker and an edit route for ANOTHER member: AMBIGUOUS. Refused at once,
  never retried, and the counts are named. A page offering to edit somebody
  the url does not name is not a page this module understands.
* no marker and nothing either way, or a reading that failed, or a landing
  that is not a member profile root: ABSENT -- not an answer about whose page
  it is, and the loader asks once more as it always did.

**NEVER "ANY PROFILE UNDER /in/".** The landed path must be a profile ROOT on
``https://www.linkedin.com``, its segment must be a member's (the self alias
``me`` is not one: a landing that never left it was measured on 2026-08-31 as
a page that had not arrived), and the structure must name that member.

## WHAT CROSSES INTO THIS PROCESS

**INTEGERS.** The landed segment goes INTO the page, inside an XPath literal,
after a closed-alphabet check (:data:`_SEGMENT`); the browser's engine counts;
three integers come back. The segment is already the page's own url, so
nothing new is disclosed to the page, and no href, label or segment returns.
:func:`evidence` -- what a refusal names -- is closed words and those integers.

**NO SCRIPT.** These are locator counts, which inject nothing, so this module
spends no ``page.evaluate`` waiver (``tests/test_readonly.py`` holds the
package to 25 and a 26th needs its own ruling).
"""
from __future__ import annotations

import re
from typing import Any, Optional
from urllib.parse import parse_qs, urlsplit

#: LinkedIn's own url claim that a landed profile is the viewer's. The one
#: spelling ``server._SELF_ASSERTION_PARAM`` and ``press._SELF_ASSERTION_PARAM``
#: are bound to, pinned equal by ``tests/test_press.py``.
SELF_ASSERTION_PARAM = "isSelfProfile"

#: The verdicts. The first three are ``server.SELF_ASSERTION_*``'s values.
SELF_TRUE = "true"
SELF_FALSE = "false"
SELF_ABSENT = "absent"
SELF_AMBIGUOUS = "ambiguous"

#: The self alias: resolves to whoever is signed in, and is not a member path.
SELF_ALIAS = "me"

#: LinkedIn's host, as every gate in this package spells it.
_HOST = "www.linkedin.com"

#: A member profile ROOT -- ``/in/<segment>`` with or without the slash and
#: nothing beneath it. ``/in/<member>/edit/intro`` is not the profile.
_PROFILE_ROOT = re.compile(r"^/in/([^/?#]+)/?$")

#: The alphabet a landed segment must be in before it is written into an XPath
#: string literal: letters, digits, hyphens, underscores and the percent sign
#: of an encoded octet. No quote can reach the expression. The same alphabet
#: ``dom.rail_invite_control_selector`` guards with.
_SEGMENT = re.compile(r"^[A-Za-z0-9_%\-]{1,200}$")

_UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_LOWER = "abcdefghijklmnopqrstuvwxyz"
_ASCII_LOWER = str.maketrans(_UPPER, _LOWER)

#: The three counts, by the names a refusal reports them under.
CONTROLS_ON_LANDED = "edit_controls_on_landed_member"
ROUTES_ON_LANDED = "edit_routes_on_landed_member"
ROUTES_ON_ANOTHER = "edit_routes_on_another_member"
COUNT_NAMES = (CONTROLS_ON_LANDED, ROUTES_ON_LANDED, ROUTES_ON_ANOTHER)


def url_marker(url: Any, *, unanimous: bool = False) -> str:
    """The url marker's state: ``true``, ``false`` or ``absent``. PURE.

    ``unanimous`` is the press gate's stricter reading: every value of the
    parameter must say ``true``, so a contradictory url is not an assertion.
    The loader takes any ``true``, as it always has.
    """
    try:
        query = urlsplit(str(url or "")).query
    except ValueError:
        return SELF_ABSENT
    values = [str(value).strip().lower() for value in parse_qs(query).get(SELF_ASSERTION_PARAM, [])]
    if not values:
        return SELF_ABSENT
    agreed = all if unanimous else any
    return SELF_TRUE if agreed(value == "true" for value in values) else SELF_FALSE


def landed_member_segment(url: Any) -> Optional[str]:
    """The member segment of a landed profile ROOT on LinkedIn's host, or None.

    None for any other scheme or host, a page beneath a profile, a segment
    outside :data:`_SEGMENT`'s alphabet, and the self alias. PURE.
    """
    try:
        parts = urlsplit(str(url or "").strip())
    except ValueError:
        return None
    if parts.scheme != "https" or parts.netloc != _HOST:
        return None
    root = _PROFILE_ROOT.match(parts.path)
    if not root:
        return None
    segment = root.group(1)
    if not _SEGMENT.fullmatch(segment) or segment.translate(_ASCII_LOWER) == SELF_ALIAS:
        return None
    return segment


def edit_route_selectors(segment: str) -> dict[str, str]:
    """The three locators :func:`read_edit_routes` counts. PURE, GUARDED.

    Built from constants and a segment that passed :data:`_SEGMENT`, and
    nothing else; anything else raises, so no quote or bracket reaches an
    expression. The segment and each href's path after ``/in/`` are compared
    with ASCII case folded -- vanity segments are case-insensitive, as
    ``named_profile.same_segment`` folds them -- and nothing else is folded.
    """
    text = str(segment or "")
    if not _SEGMENT.fullmatch(text):
        raise ValueError(
            "edit_route_selectors needs a member segment -- letters, digits, "
            "hyphens, underscores or percent-encoded octets; a locator is built "
            "from this string, so nothing else may reach it."
        )
    wanted = text.translate(_ASCII_LOWER)
    on_linkedin = (
        "(starts-with(@href, 'https://www.linkedin.com/in/') or starts-with(@href, '/in/'))"
    )
    rest = "translate(substring-after(@href, '/in/'), '" + _UPPER + "', '" + _LOWER + "')"
    own_segment = "substring-before(" + rest + ", '/')"
    on_landed = "starts-with(" + rest + ", '" + wanted + "/edit/')"
    on_another = (
        "starts-with(substring-after(" + rest + ", '/'), 'edit/')"
        " and string-length(" + own_segment + ") > 0"
        " and not(contains(" + own_segment + ", '?')) and not(contains(" + own_segment + ", '#'))"
        " and " + own_segment + " != '" + wanted + "'"
        " and " + own_segment + " != '" + SELF_ALIAS + "'"
    )
    named = "normalize-space(@aria-label) != ''"
    return {
        CONTROLS_ON_LANDED: "xpath=//a[" + on_linkedin + "][" + on_landed + "][" + named + "]",
        ROUTES_ON_LANDED: "xpath=//a[" + on_linkedin + "][" + on_landed + "]",
        ROUTES_ON_ANOTHER: "xpath=//a[" + on_linkedin + "][" + on_another + "]",
    }


def _count(value: Any) -> Optional[int]:
    """A locator's count, or None. Never raises and never renders its input."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None
    return value


async def read_edit_routes(page: Any, landed_url: Optional[str] = None) -> dict[str, Any]:
    """Count the editor links the page draws for the landed member. NEVER RAISES.

    ``landed_url`` is the url the caller is reasoning about -- the loader's
    landed url, the press gate's ``page.url`` -- and defaults to ``page.url``.
    A reading is meaningful ONLY for the url it was taken against, so every
    caller passes the one it then decides on.

    Returns ``{"read": True, "landed_on_member_path": True, <three counts>}``,
    or ``read: False`` with ``landed_on_member_path`` saying whether the page
    was even asked: a url that is not a member's profile root is not read at
    all, and a count that failed is reported by its exception TYPE only.
    """
    url = landed_url if landed_url is not None else getattr(page, "url", None)
    segment = landed_member_segment(url)
    if segment is None:
        return {"read": False, "landed_on_member_path": False, "unreadable": None}
    out: dict[str, Any] = {"read": True, "landed_on_member_path": True}
    for name, selector in edit_route_selectors(segment).items():
        try:
            counted = _count(await page.locator(selector).count())
        except Exception as exc:  # noqa: BLE001 - a reading never breaks a gate
            return {"read": False, "landed_on_member_path": True, "unreadable": type(exc).__name__}
        if counted is None:
            return {"read": False, "landed_on_member_path": True, "unreadable": "not_a_count"}
        out[name] = counted
    return out


def structural_verdict(reading: Optional[dict[str, Any]]) -> str:
    """``self``, ``foreign``, ``none``, ``unread`` or ``not_a_member_path``. PURE."""
    if not isinstance(reading, dict) or not reading.get("landed_on_member_path"):
        return "not_a_member_path"
    if reading.get("read") is not True:
        return "unread"
    counts = [_count(reading.get(name)) for name in COUNT_NAMES]
    if any(count is None for count in counts):
        return "unread"
    controls, _routes, another = counts
    if another:
        return "foreign"
    return "self" if controls else "none"


def self_state(marker: str, reading: Optional[dict[str, Any]] = None) -> str:
    """THE RULE, PURE: the marker if it answered, else the structure."""
    if marker == SELF_TRUE:
        return SELF_TRUE
    if marker != SELF_ABSENT:
        return SELF_FALSE
    verdict = structural_verdict(reading)
    if verdict == "self":
        return SELF_TRUE
    if verdict == "foreign":
        return SELF_AMBIGUOUS
    return SELF_ABSENT


def self_signal(marker: str, reading: Optional[dict[str, Any]] = None) -> Optional[str]:
    """WHICH signal established self: ``url_marker``, ``edit_controls`` or None."""
    if marker == SELF_TRUE:
        return "url_marker"
    if self_state(marker, reading) == SELF_TRUE:
        return "edit_controls"
    return None


def evidence(marker: str, reading: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    """WHAT WAS SEEN, for a refusal to name: closed words and integers only."""
    read = isinstance(reading, dict) and reading.get("read") is True
    out: dict[str, Any] = {
        "url_marker": marker if marker in (SELF_TRUE, SELF_FALSE, SELF_ABSENT) else SELF_ABSENT,
        "landed_on_member_path": bool(isinstance(reading, dict) and reading.get("landed_on_member_path")),
        "structure_read": read,
        "self_signal": self_signal(marker, reading),
    }
    for name in COUNT_NAMES:
        out[name] = _count(reading.get(name)) if read else None
    return out


def wants_structure(url: Any) -> bool:
    """Is ``url`` a member profile root carrying NO marker -- the one case the
    structure decides? Lets a gate leave every other page untouched. PURE."""
    return landed_member_segment(url) is not None and url_marker(url) == SELF_ABSENT
