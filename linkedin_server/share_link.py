"""Copy the operator's OWN post's link through its OWN "Copy link to post" item.

MEASURED LIVE (see the wave's own record), on his own post's permalink page
``/feed/update/urn:li:activity:<digits>/``, with the control menu opened
through the shipped press gate and snapshotted 1.5s after the click:

* the trigger is the ONLY element in ``main [aria-expanded]`` whose
  aria-label, normalised, STARTS WITH "open control menu" -- of 4
  ``[aria-expanded]`` controls in ``main``, exactly 1 matched;
* the items render AFTER the click (absent from the closed page and from an
  immediate read; present 1.5s later) as ``div[role=button]`` inside ``li``
  inside ``ul``, all inside ``main`` -- no ``role=menu``, no
  ``role=menuitem`` anywhere;
* the normalised item texts, in order: "feature on top of profile", "save",
  "copy link to post", "embed this post", "edit post", "delete post", "who
  can comment on this post", "who can see this post". Several are WRITES
  (delete, edit, visibility, feature, save). ONLY "copy link to post" may
  ever be pressed by this module.

THIS MODULE GOVERNS ONE CAPABILITY AND NOTHING NEXT TO IT. It reads the
trigger, opens the SAME menu :mod:`linkedin_server.press` already knows how
to gate, refuses to touch anything but the one phrase named above, and
copies the link INTO AN IN-PAGE CAPTURE BOX instead of the operator's OS
clipboard. See :data:`CLIPBOARD_JS`: it REPLACES
``navigator.clipboard.writeText``, ``navigator.clipboard.write`` and
``document.execCommand("copy")`` with functions that keep the text in the
box and resolve WITHOUT writing anything, and it adds a capturing ``copy``
listener that calls ``preventDefault()``. **THAT COVERS EVERY ROUTE THE PAGE
LOOKS UP AT THE MOMENT IT COPIES, AND ONE ROUTE IT DOES NOT:** a reference to
the clipboard API the page took before the capture was installed. Nothing in
the page can see that route; the box stays empty and the answer reads
``copied: False`` -- never a fabricated link, and never a claim about the
operator's clipboard either way. :data:`CLIPBOARD_JS`'s own comment has the
detail, and a fixture variant pins the answer.

## THE GATE IS press's OWN FOUR CHECKS, CALLED EXPLICITLY, NOT press.evaluate()

The disclosing-press ruling (`_audit/2026-09-19-the-disclosing-press-ruling.md`,
documented at the top of ``press.py``) already answers "may this server open a
menu on this page" -- address admitted, control matches an enumerated
ATTRIBUTE shape, the scope narrows the candidates, the press priced against an
outward counter, the closure verified. This module does not re-litigate any of
that. It calls the four PURE, page-untouching component checks
``press.evaluate`` itself runs internally, in the same order that function
runs them, and refuses on the first one that refuses:

    press.check_address(url)          -- is the address already admitted?
    press.check_shape("[aria-expanded]")  -- is the control an enumerated shape?
    press.check_scope("main")         -- is the scope one of the closed table?
    press.check_basis(url)            -- does the surface declare a pricing basis?

**THIS IS NOT ``press.evaluate`` CALLED PIECE BY PIECE FOR STYLE.** An
earlier version of this module imported ``press.evaluate`` under an alias
(``_pre_press_gate``) specifically to dodge a coincidental collision: both
``readonly.scan_source_for_mutations`` and
``tests/test_readonly.py``'s ``_scripts_this_package_executes`` match on the
attribute name ``evaluate`` immediately followed by an opening parenthesis
(or, for the second, any attribute name STARTING WITH "evaluate"), with no
regard for what object it is called on -- and
``press.evaluate`` is a plain, pure Python function that happens to share
that one word with Playwright's ``page.evaluate``. Importing around a
package-wide instrument is scanner evasion: the instrument exists to make
every mutating call in this package visible to a reviewer in one place, and
a call written specifically so the instrument cannot see it defeats that
regardless of the call's own safety. Calling the four checks BY THEIR OWN
NAMES is not evasion -- it is what ``reveal.check_reveal`` and
``view_switch.check_switch`` already do, for the identical reason: they need
``press.check_address`` and ``press.check_basis`` on their own, not the
whole disclosure-menu-specific ``press.evaluate`` sequence, and no scanner
anywhere in this package treats ``check_address``, ``check_shape``,
``check_scope`` or ``check_basis`` as a mutation, because none of the four
performs one.

What THIS module adds on top of the four checks is narrower than any of
them: which ONE of the (up to eight) items that render inside that menu may
be pressed, and what happens to whatever LinkedIn hands back.

## WHY THE OWNER CHECK EXISTS AND WHAT IT DOES NOT PROVE

The menu renders identically whether or not this is his own post -- the
only public difference measured is that "edit post" and "delete post" are
absent from another member's item. So :data:`OWNER_PHRASES` is read from the
SAME normalised item list the copy phrase is read from, before the copy item
is ever clicked, and their absence refuses ``not_his_post`` WITHOUT clicking
anything. This is a NEGATIVE PROOF ONLY -- their presence is evidence he can
edit and delete the post, which on a page this server never opens for a
third party (see ``readonly.py``: no press ever extends reach past an
already-admitted address) is evidence enough that it is his.

## THE TWO DRAIN POINTS, AND WHY THERE ARE EXACTLY TWO

``readonly.SANCTIONED_MUTATIONS`` admits an entry -- ``(module, enclosing
function, kind)`` -- as covering exactly ONE call site, "not a licence"
(the same package's own words, in ``readonly.py``'s module docstring). This
module makes two clicks (the trigger, the copy item) and two evaluates
(install the clipboard hook, read it back), which would need FOUR entries
under four different kinds spread across ONE function if written inline --
this module's first version did exactly that, and it worked, but it left
five separate call sites for three kinds where the house pattern (see
``linkedin_server/view_switch.py``'s ``_activate`` and
``linkedin_server/reveal.py``'s single click inside ``reveal``) asks for one
call site per kind. So:

* :func:`_activate` is the ONLY place this module clicks. Both the trigger
  and the copy item are clicked by calling it, never by a second literal
  click call anywhere else.
* :func:`_clipboard` is the ONLY place this module evaluates. Installing the
  hook and reading it back are both calls to it, with ``mode`` selecting
  which -- never a second page-evaluate call anywhere else. ``mode`` is
  validated BEFORE the page is touched, closed to ``"install"`` and
  ``"read"``, for the same reason :mod:`linkedin_server.press` refuses a
  caller-supplied selector: a function that evaluates an unvalidated
  argument is one edit away from evaluating whatever a caller hands it.

``tests/test_share_link.py`` pins both drain points by AST: the only caller
of :func:`_activate` and the only caller of :func:`_clipboard` is
:func:`copy_own_post_link`, and the module source holds exactly one literal
``.click`` and exactly one literal ``.evaluate``.

**THE ESCAPE PRESS STAYS INLINE, DELIBERATELY NOT A THIRD DRAIN POINT.**
There is already exactly one keyboard-press call in this
module (see :func:`copy_own_post_link`'s own body) -- one entry already
covers it, so a drain point would rename one call site without reducing the
count that matters.

## WHAT THIS MODULE REFUSES, AND NEVER RAISES DOING IT

Every named failure returns a dict carrying ``refused`` and a ``why`` this
module writes -- never the library's own exception text, which has been
measured elsewhere in this package to carry selectors and urls nobody chose
to publish. An exception from the page is converted to ``refused:
"press_failed"`` with ONLY the exception's TYPE name, exactly as
``press.disclose`` already does it, and for the same reason: a library's
message is composed by code nobody here controls.

## WHAT THIS MODULE NEVER DOES

It never navigates -- the caller navigates, this module only presses and
reads. No page string it reads may leave the module except the one field
this whole exercise exists to deliver, ``link``: the raw text the "Copy
link to post" item produced, captured before it ever reached a clipboard.
Everything else this module returns is a package literal, a boolean, or an
integer.
"""
from __future__ import annotations

import re
from typing import Any, Optional
from urllib.parse import urlsplit

from linkedin_server import dom, press

#: THE ITEM'S OWN REACTION TOGGLE, IN THE PERMALINK'S DIALECT -- what prices a
#: press on this page. MEASURED on his own post's permalink, 2026-09-23 22:38
#: and 2026-09-24 00:15: ONE toggle labelled "Unreact Like" (the item liked)
#: and ZERO in the feed's dialect ("Reaction button state: ..."), which
#: ``/feed/`` itself draws three of. So ``dom.read_reaction_surface``'s
#: ``off_state`` -- the counter the ``/feed/`` basis names, and which reaches
#: this page by path prefix -- reads 0 here at both ends of ANY press: a price
#: that cannot move. That is how the first live fire of this module was
#: priced, and why these two exist. The OFF form ("React <kind>") is inferred
#: from the ON form and not yet seen live; a page drawing a toggle in neither
#: dialect is refused by :func:`price_can_move` before anything is pressed.
TOGGLE_ON_SELECTOR = 'button[aria-label^="Unreact "]'
TOGGLE_OFF_SELECTOR = 'button[aria-label^="React "]'

#: The counters :func:`read_item_price` reads, in the order it reads them.
#: ``off_state`` stays first because the gate requires the counter its basis
#: NAMES to be read at both ends; the two toggles are what can actually move.
PRICE_COUNTERS = ("off_state", "toggle_on", "toggle_off")

#: The permalink this module's caller is expected to have already navigated
#: to. Built here so a caller can construct the SAME address this module
#: reads ``page.url`` against, never so this module can navigate to it --
#: see the module docstring: this module never calls ``goto``.
POST_URL_TEMPLATE = "https://www.linkedin.com/feed/update/urn:li:activity:{digits}/"

#: The normalised prefix of the control-menu trigger's aria-label. Matched by
#: ``startswith`` because the measured live label is exactly "Open control
#: menu for post" and this package does not read page text into a decision
#: beyond what it has to -- a prefix match is the narrowest test that still
#: tolerates LinkedIn appending nothing or appending more.
MENU_PREFIX = "open control menu"

#: The one item this module may ever click, normalised.
COPY_PHRASE = "copy link to post"

#: Items that mean "this is his own post". Read from the SAME menu the copy
#: phrase is read from and never clicked, before the copy item is clicked --
#: see the module docstring's owner-check section.
OWNER_PHRASES = ("delete post", "edit post")

#: Where a menu's items render, measured live: ``div[role=button]`` inside
#: ``li`` inside ``ul``, all inside ``main``. No ``role=menu``, no
#: ``role=menuitem`` anywhere on the real page.
ITEM_SELECTOR = "main li div[role=button]"

#: How long this module waits for the items to render after the trigger is
#: clicked. Measured live: absent from an immediate read, present 1.5s
#: later; this is a generous multiple of that, not a tuned minimum.
OPEN_WAIT_MS = 5000

#: The one timeout this module clicks under, taken from ``press.py`` rather
#: than restated, so the two never drift apart.
CLICK_TIMEOUT_MS = press.CLICK_TIMEOUT_MS

#: A run of characters outside [a-z0-9], collapsed to one space by
#: normalisation. Applied everywhere this module compares page text: lower,
#: substitute, strip -- in that order, and nowhere else in this module.
_NON_ALNUM_RUN = re.compile(r"[^a-z0-9]+")

#: 1-20 ASCII digits, and ONLY ASCII digits -- ``[0-9]``, never ``\d``.
#: ``\d`` on a Python str pattern matches any Unicode decimal digit, which
#: this repository has already measured admitting non-ASCII spellings of an
#: id through a boundary that meant to be numeric-only
#: (``readonly.py``'s groups-id entry records the same defect and the same
#: fix). Bounded at 20 for the same reason ``groups.group_identifier`` is:
#: an unbounded repetition on a caller-shaped input is a cost nobody chose.
_ACTIVITY_DIGITS_RE = re.compile(r"^[0-9]{1,20}$")

#: The closed set :func:`_clipboard` accepts. Anything else raises
#: ``ValueError`` before the page is ever touched.
_CLIPBOARD_MODES = ("install", "read")

#: How long the read mode of :data:`CLIPBOARD_JS` waits for the FIRST kept
#: text when none has arrived yet. The script carries the same number as a
#: literal (it has to be a module constant to be certified at all -- see
#: ``tests/test_readonly.py``'s ``evaluate_targets``), and a test pins the
#: two equal. A bound on a wait the write itself ends, not a sleep.
READ_WAIT_MS = 3000


def _normalise(text: Optional[str]) -> str:
    """Lower-case, collapse every run outside [a-z0-9] to one space, strip.

    PURE, and applied identically to an aria-label and to an item's own text
    -- the same function, so the trigger match and the item match can never
    silently use two different rules.
    """
    return _NON_ALNUM_RUN.sub(" ", str(text or "").lower()).strip()


def validated_activity_digits(value: Any) -> str:
    """1-20 ASCII digits, or raise. The message NEVER includes ``value``.

    A bad activity id is refused before this module ever touches a page --
    see :func:`copy_own_post_link`'s first step -- and the exception this
    raises is what lets that refusal happen with zero page contact. The
    message is a fixed sentence rather than an interpolation of ``value``
    for the same reason ``press.py``'s refusals never carry a library's raw
    text: whatever was handed in is not this function's to publish.
    """
    if isinstance(value, str) and _ACTIVITY_DIGITS_RE.match(value):
        return value
    raise ValueError(
        "activity id must be 1-20 ASCII digits ([0-9] only); refusing "
        "rather than guessing what was meant."
    )


def post_url(digits: Any) -> str:
    """:data:`POST_URL_TEMPLATE` filled with validated digits."""
    return POST_URL_TEMPLATE.format(digits=validated_activity_digits(digits))


async def read_item_price(page: Any) -> dict[str, Optional[int]]:
    """The counters that price a press on an item's permalink: integers, or
    None for one that did not read -- never a page string.

    ``off_state`` is the ``/feed/`` basis's own counter, from the shipped
    reader; ``toggle_on`` / ``toggle_off`` count the item's reaction toggle in
    the permalink's dialect (see :data:`TOGGLE_ON_SELECTOR`). A reaction by
    this press, in either direction, moves one of the toggles.
    """
    surface = await dom.read_reaction_surface(page)
    off_state = surface.get("off_state") if isinstance(surface, dict) else None
    reading: dict[str, Optional[int]] = {
        "off_state": (
            off_state
            if isinstance(off_state, int) and not isinstance(off_state, bool)
            else None
        )
    }
    for name, selector in (
        ("toggle_on", TOGGLE_ON_SELECTOR),
        ("toggle_off", TOGGLE_OFF_SELECTOR),
    ):
        try:
            reading[name] = int(await page.locator(selector).count())
        except Exception:  # noqa: BLE001 - an unread counter is None, not 0
            reading[name] = None
    return reading


def price_can_move(reading: Any) -> bool:
    """PURE. May this reading price a press at all?

    True only when EVERY counter in :data:`PRICE_COUNTERS` read as an integer
    AND at least one reaction toggle is drawn, in either dialect. A reading of
    all zeros is not a clean price: nothing drawn there can move, so an
    outward act would leave it exactly as it found it. The gate compares what
    it is handed and cannot tell "did not move" from "could not move"; this
    is asked before the first press, so the answer costs no press.
    """
    if not isinstance(reading, dict):
        return False
    values = [reading.get(name) for name in PRICE_COUNTERS]
    if any(isinstance(value, bool) or not isinstance(value, int) for value in values):
        return False
    return sum(values) >= 1


def link_shape(link: Any, digits: str) -> dict[str, Any]:
    """What KIND of thing ``link`` is, never a fragment of ``link`` itself.

    PURE. Returns only booleans, one of the closed ``path_kind`` literals,
    and an integer -- never a substring of ``link``, so a caller that logs
    or reports this dict cannot accidentally publish the link's own
    identifying parts through it. The raw link is deliberately a SEPARATE
    field on :func:`copy_own_post_link`'s return, carried once rather than
    reconstructed from pieces here.

    ``path_kind`` is one of:

    * ``"posts"`` -- the shareable form LinkedIn's own "Copy link to post"
      control is measured to produce (``/posts/<slug>-activity-<id>-...``);
    * ``"feed_update"`` -- the permalink form this package navigates to
      (``/feed/update/urn:li:<type>:<id>/``, the same shape
      ``readonly._ALLOWED_URL_PATTERNS`` admits for reading);
    * ``"other"`` -- anything else, including a non-LinkedIn host, a
      malformed string, or a LinkedIn path this module was not written to
      recognise.

    ``carries_activity_id`` is True only when ``digits`` appears as a WHOLE
    number inside ``link`` -- bounded on both sides by a non-digit or an
    edge of the string -- so a activity id that is merely a substring of a
    longer number does not count.
    """
    text = str(link)
    try:
        parsed = urlsplit(text)
        scheme = (parsed.scheme or "").lower()
        host = (parsed.hostname or "").lower()
        path = parsed.path or ""
        has_query = bool(parsed.query)
    except ValueError:
        # A string urlsplit refuses to parse (a malformed IPv6-shaped host
        # is the documented case) carries no scheme, host or query this
        # module can trust, so every field falls back to the "tells us
        # nothing" answer rather than raising out of a PURE function.
        scheme = ""
        host = ""
        path = ""
        has_query = False

    if path.startswith("/posts/"):
        path_kind = "posts"
    elif path.startswith("/feed/update/"):
        path_kind = "feed_update"
    else:
        path_kind = "other"

    digit_run = re.escape(str(digits))
    carries_activity_id = bool(
        re.search(r"(?<!\d)" + digit_run + r"(?!\d)", text)
    )

    return {
        "is_https": scheme == "https",
        "host_is_linkedin": host in ("www.linkedin.com", "linkedin.com"),
        "path_kind": path_kind,
        "carries_activity_id": carries_activity_id,
        "has_query": has_query,
        "length": len(text),
    }


#: Installs an in-page capture box (mode "install") and REPLACES every route
#: this module knows of that could reach the OS clipboard, or reads the box
#: back (mode "read"). ONE script for both, so the module holds ONE
#: ``page.evaluate`` call site (:func:`_clipboard`) rather than two --
#: ``readonly.SANCTIONED_MUTATIONS`` admits one call per entry, and merging
#: what were two named scripts (formerly ``CLIPBOARD_HOOK_JS`` and
#: ``CAPTURED_JS``) into one keyed by ``mode`` is what makes a single entry
#: cover both without losing either half.
#:
#: Idempotent on install -- installing it twice on the same page changes
#: nothing the second time -- because a page that already carries it (a
#: prior call in the same test) must not end up with two stacked "copy"
#: listeners or a re-wrapped ``execCommand`` wrapping its own wrapper.
#:
#: WHAT INSTALL COVERS:
#:
#: 1. ``navigator.clipboard.writeText`` / ``.write`` are REPLACED with
#:    functions that keep the text in the box and resolve -- so the real API
#:    is never called at all, not merely intercepted after the fact.
#:    ``write`` keeps the ``text/plain`` part of each item it is handed, read
#:    from the item itself; an item carrying no text keeps an empty string,
#:    so the write is counted and never mistaken for a link.
#: 2. ``document.execCommand`` is wrapped so ``"copy"`` keeps
#:    ``String(window.getSelection())`` and returns ``true`` WITHOUT copying
#:    and without firing a copy event, while every other command passes
#:    through to the real implementation unchanged -- a page calling
#:    ``execCommand("selectAll")`` for an unrelated reason must keep working.
#: 3. A CAPTURING ``copy`` listener on ``document`` calls
#:    ``preventDefault()``, for a copy event that reaches the page anyway (a
#:    real Ctrl+C in this tab, or the copy command reached through a
#:    reference taken before the wrapper). It NARROWS that route and does not
#:    close it: in Chromium a cancelled copy event writes whatever the page's
#:    own copy handlers put into ``clipboardData`` in place of the selection.
#:
#: AND THE ROUTE NONE OF THE THREE COVERS: a reference to
#: ``navigator.clipboard.writeText`` or ``.write`` that the page took BEFORE
#: install. The async clipboard API fires no copy event, so nothing here
#: sees it; the box stays empty, :func:`copy_own_post_link` returns
#: ``copied: False``, and whether the operator's clipboard was written cannot
#: be read from inside the page. The fixture's ``capturedReference`` variant
#: pins exactly that answer.
#:
#: ON READ: the kept texts, or ``null`` if the hook was never installed on
#: this page -- never an empty array standing in for "not installed",
#: because those are different facts and this module does not collapse them
#: (the same discipline ``press.py`` states for an unreadable counter: it is
#: not a zero). **THE READ WAITS FOR THE FIRST TEXT**, up to 3000 ms (the
#: literal below, pinned equal to :data:`READ_WAIT_MS`), because a page may
#: write after an ``await`` of its own -- after the click has already
#: returned -- and a read taken before that write would report a copy that
#: happened as one that did not. It is woken by the write itself, not by
#: polling; the bound only ends the wait for a copy that never comes.
CLIPBOARD_JS = """
(mode) => {
  if (mode === "install") {
    if (!window.__lqClip) {
      Object.defineProperty(window, "__lqClip", {
        value: { texts: [], waiters: [] },
        writable: true,
        configurable: true,
      });
    }
    const box = window.__lqClip;
    const keep = function (text) {
      box.texts.push(String(text));
      box.waiters.splice(0).forEach(function (wake) { wake(); });
    };

    if (navigator.clipboard && !navigator.clipboard.__lqPatched) {
      navigator.clipboard.writeText = function (text) {
        keep(text);
        return Promise.resolve();
      };
      navigator.clipboard.write = function (items) {
        const list = Array.from(items || []);
        if (!list.length) {
          keep("");
          return Promise.resolve();
        }
        return Promise.all(list.map(function (item) {
          const types = Array.from((item && item.types) || []);
          if (types.indexOf("text/plain") < 0) {
            keep("");
            return undefined;
          }
          return item.getType("text/plain")
            .then(function (blob) { return blob.text(); })
            .then(keep, function () { keep(""); });
        })).then(function () { return undefined; });
      };
      try {
        Object.defineProperty(navigator.clipboard, "__lqPatched", {
          value: true,
          configurable: true,
        });
      } catch (e) {
        // A clipboard object that refuses a new property still had its two
        // methods reassigned above, which is the half that matters.
      }
    }

    if (!document.__lqExecPatched) {
      const original = document.execCommand.bind(document);
      document.execCommand = function (command, ui, value) {
        if (String(command).toLowerCase() === "copy") {
          keep(String(window.getSelection()));
          return true;
        }
        return original(command, ui, value);
      };
      try {
        Object.defineProperty(document, "__lqExecPatched", {
          value: true,
          configurable: true,
        });
      } catch (e) {
        // Same fallback as above: execCommand was already reassigned.
      }
    }

    if (!window.__lqCopyListenerInstalled) {
      document.addEventListener(
        "copy",
        function (event) {
          event.preventDefault();
        },
        true
      );
      window.__lqCopyListenerInstalled = true;
    }
    return true;
  }

  if (mode === "read") {
    const box = window.__lqClip;
    if (!box) {
      return null;
    }
    if (box.texts.length) {
      return box.texts.slice();
    }
    return new Promise(function (resolve) {
      const timer = setTimeout(function () {
        resolve(box.texts.slice());
      }, 3000);
      box.waiters.push(function () {
        clearTimeout(timer);
        resolve(box.texts.slice());
      });
    });
  }

  return null;
}
"""


async def _activate(target: Any) -> None:
    """THE ONE CLICK IN THIS MODULE.

    Called only by :func:`copy_own_post_link` -- once for the trigger, once
    for the copy item -- so the package's mutation scanner sees ONE call
    site for the ``click`` kind rather than two.
    ``tests/test_share_link.py`` pins both halves of that claim: this is the
    only literal ``.click`` in the module's source, and
    ``copy_own_post_link`` is this function's only caller.
    """
    await target.click(timeout=CLICK_TIMEOUT_MS)


async def _clipboard(page: Any, mode: str) -> Any:
    """THE ONE EVALUATE IN THIS MODULE.

    Called only by :func:`copy_own_post_link` -- once with ``"install"``,
    once with ``"read"`` -- so the package's mutation scanner sees ONE call
    site for the ``evaluate`` kind rather than two.
    ``tests/test_share_link.py`` pins both halves of that claim: this is the
    only literal ``.evaluate`` in the module's source, and
    ``copy_own_post_link`` is this function's only caller.

    ``mode`` is validated against :data:`_CLIPBOARD_MODES` BEFORE the page
    is touched at all -- an unrecognised mode raises ``ValueError`` rather
    than reaching :data:`CLIPBOARD_JS``, because a function that forwards an
    unvalidated argument into a page-evaluate call is one edit away from
    evaluating whatever a caller hands it, which is exactly what
    :mod:`linkedin_server.press`'s module docstring refuses a caller for a
    press target ("why the caller cannot hand in a selector").
    """
    if mode not in _CLIPBOARD_MODES:
        raise ValueError(
            "share_link._clipboard mode must be one of "
            f"{_CLIPBOARD_MODES}; refusing rather than guessing what was "
            "meant."
        )
    return await page.evaluate(CLIPBOARD_JS, mode)


async def copy_own_post_link(
    page: Any, *, activity_digits: Any, read_counters: Any
) -> dict[str, Any]:
    """Copy the link of HIS OWN post through its own "Copy link to post" item.

    ``page`` is assumed already on the post's own permalink page -- this
    module never navigates. ``read_counters`` is an async callable
    returning a MAPPING of counter name to int-or-None, exactly as
    ``press.disclose`` requires one: unmeasurable resolves AGAINST the
    press.

    IN ORDER, refusing at the first failed step with a ``refused`` key and a
    ``why`` this module writes, touching nothing on the page after a
    refusal:

    1. ``activity_digits`` validated -- a bad value refuses with NO page
       contact at all.
    2. The trigger found by aria-label prefix, among ``main``'s
       ``[aria-expanded]`` controls -- not exactly one match refuses.
    3. The package's own pre-press checks, called explicitly and in order --
       ``press.check_address``, ``press.check_shape``, ``press.check_scope``,
       ``press.check_basis`` -- a refusal from any of them is returned as
       this module's own refusal, with that check's own verdict attached.
    4. Counters read BEFORE any click -- unreadable refuses before the
       trigger is ever pressed.
    5. The trigger is activated -- the first of this module's two clicks,
       both through :func:`_activate`.
    6. A bounded wait for the copy item to render -- a timeout refuses,
       after the menu is closed.
    7. The owner check, against the SAME rendered items -- absent refuses,
       after the menu is closed, WITHOUT the copy item ever being clicked.
    8. The copy item must be the UNIQUE match -- more than one refuses,
       after the menu is closed.
    9. The clipboard hook is installed, the copy item is activated -- the
       second of this module's two clicks -- and the capture box is read,
       both installs and reads going through :func:`_clipboard`; the read
       waits up to :data:`READ_WAIT_MS` for a write the page makes after
       the click returned. ``captures`` counts what was kept; ``copied`` is
       True only for a NON-EMPTY text, and the first one is the link. No
       text is recorded as ``copied: False``; it is NOT a refusal.
    10. The menu is closed (Escape, if still open) and its closed state
        read, whatever happened above. A refusal from steps 6-8 carries
        ``closure`` too: the menu was opened, so the refusal says whether it
        was left as found. That refusal and a completed copy both carry
        ``escape_pressed``, so the presses made can be counted off them; a
        ``press_failed`` answer does not, and claims nothing about the page.
    11. Counters read again.
    12. The verdict: ``press.check_counters`` and ``press.check_closure``
        against the two readings, reported alongside everything gathered
        above.

    Never raises for a page problem: any exception this module's own steps
    did not already classify becomes ``refused: "press_failed"`` carrying
    only the exception's TYPE name.
    """
    try:
        digits = validated_activity_digits(activity_digits)
    except ValueError:
        return {
            "refused": "bad_activity_id",
            "why": (
                "activity_digits is not 1-20 ASCII digits; refused before "
                "any page contact."
            ),
        }

    try:
        candidates = page.locator("main").locator("[aria-expanded]")
        total = int(await candidates.count())
        trigger_indices: list[int] = []
        for index in range(total):
            label = await candidates.nth(index).get_attribute("aria-label")
            if _normalise(label).startswith(MENU_PREFIX):
                trigger_indices.append(index)
        if len(trigger_indices) != 1:
            return {
                "refused": "control_menu_not_unique",
                "why": (
                    f"{len(trigger_indices)} of {total} [aria-expanded] "
                    "controls in main had an aria-label starting with the "
                    "control-menu prefix; exactly one is required to aim a "
                    "click."
                ),
                "trigger_matches": len(trigger_indices),
            }
        trigger = candidates.nth(trigger_indices[0])

        # THE FOUR PRE-PRESS CHECKS, CALLED BY NAME, IN THE SAME ORDER
        # press.evaluate() runs them internally -- see the module docstring
        # for why this is not that function called piece by piece for style,
        # but the house pattern reveal.py and view_switch.py already use.
        gate_url = getattr(page, "url", None)
        gate = press.check_address(gate_url)
        if not gate.get("refused"):
            gate = press.check_shape("[aria-expanded]")
        if not gate.get("refused"):
            gate = press.check_scope("main")
        if not gate.get("refused"):
            gate = press.check_basis(gate_url)
        if gate.get("refused"):
            return {
                "refused": "gate_refused",
                "why": (
                    "one of the package's own pre-press checks (address, "
                    "shape, scope or basis) refused this page; see gate for "
                    "which one and why."
                ),
                "gate": gate,
            }

        before = await read_counters()
        if not before:
            return {
                "refused": "counters_unreadable",
                "why": (
                    "read_counters returned nothing before any click; "
                    "unmeasurable resolves against the press."
                ),
            }

        expanded_before = await trigger.get_attribute("aria-expanded")
        await _activate(trigger)

        refusal: Optional[str] = None
        refusal_why: str = ""
        owner_item_present = False
        copied = False
        link: Optional[str] = None
        captures: Optional[int] = None

        try:
            await page.locator(ITEM_SELECTOR).filter(
                has_text=COPY_PHRASE
            ).first.wait_for(timeout=OPEN_WAIT_MS)
        except Exception as exc:  # noqa: BLE001 - classified below
            # CLASSIFIED BY NAME, this package's own idiom (see
            # dom.read_job_description_readiness): a timeout is the page
            # answering "not here" within the bound; anything else is this
            # wait failing to ask, and is re-raised into the outer handler.
            if type(exc).__name__ != "TimeoutError":
                raise
            refusal = "copy_item_absent"
            refusal_why = (
                f"no item in ITEM_SELECTOR carried the copy-link phrase "
                f"within {OPEN_WAIT_MS}ms of the trigger click."
            )
        else:
            items = page.locator(ITEM_SELECTOR)
            texts = await items.all_text_contents()
            normalised_texts = [_normalise(text) for text in texts]
            owner_item_present = any(
                text in OWNER_PHRASES for text in normalised_texts
            )
            copy_indices = [
                index
                for index, text in enumerate(normalised_texts)
                if text == COPY_PHRASE
            ]
            if not owner_item_present:
                refusal = "not_his_post"
                refusal_why = (
                    "no item's normalised text equalled an owner-only "
                    "phrase (edit post / delete post); this menu does not "
                    "show the marks of his own post, so the copy item is "
                    "never clicked."
                )
            elif len(copy_indices) != 1:
                refusal = "copy_item_not_unique"
                refusal_why = (
                    f"{len(copy_indices)} items had normalised text equal "
                    "to the copy-link phrase; exactly one is required to "
                    "aim a click."
                )
            else:
                copy_item = items.nth(copy_indices[0])
                await _clipboard(page, "install")
                await _activate(copy_item)
                captured = await _clipboard(page, "read")
                # None (the box is gone) stays None: it is not zero captures.
                # An EMPTY kept text counts as a capture and never as a link
                # -- a write that carried no text copied nothing.
                captured_texts = [
                    text for text in (captured or []) if isinstance(text, str)
                ]
                captures = None if captured is None else len(captured_texts)
                non_empty = [text for text in captured_texts if text]
                if non_empty:
                    copied = True
                    link = non_empty[0]

        # STEP 10, WRITTEN ONCE: every path above -- the timeout, the two
        # in-menu refusals, and the success case -- falls through to here,
        # so the Escape press exists as ONE line in this function's body.
        # It stays inline rather than becoming a third drain point: there is
        # already exactly one page.keyboard.press(...) call site, so a drain
        # point would rename it without reducing the count that matters.
        # EVERY PRESS IS COUNTED IN THE ANSWER. The clicks follow from it --
        # one (the trigger) on a refusal from steps 6-8, two on a copy -- and
        # the Escape happens only when the menu is still open, so the answer
        # says whether it did: a press count read off an envelope that cannot
        # say it is a guess.
        escape_pressed = False
        if await trigger.get_attribute("aria-expanded") == "true":
            await page.keyboard.press("Escape")
            escape_pressed = True
        expanded_after = await trigger.get_attribute("aria-expanded")

        if refusal is not None:
            # THE MENU WAS OPENED BEFORE THIS REFUSAL, so the refusal says
            # whether it was left as found: a menu left open is the next
            # reader's problem, and a refusal that hid it would be quiet
            # about the one thing it changed.
            return {
                "refused": refusal,
                "why": refusal_why,
                "closure": press.check_closure(expanded_before, expanded_after),
                "escape_pressed": escape_pressed,
            }

        after = await read_counters()
    except Exception as exc:  # noqa: BLE001 - only the type name is kept
        return {
            "refused": "press_failed",
            "why": (
                f"the press raised {type(exc).__name__}. Nothing is claimed "
                "about what the page did; a failure is not a refusal and is "
                "not a success."
            ),
        }

    counters = press.check_counters(
        before, after, basis=press.sensitivity_basis(getattr(page, "url", None))
    )
    closure = press.check_closure(expanded_before, expanded_after)
    permitted = bool(not counters.get("refused") and not closure.get("refused"))
    return {
        "permitted": permitted,
        "copied": copied,
        "captures": captures,
        "shape": link_shape(link, digits) if link else None,
        "owner_item_present": owner_item_present,
        "gate": gate,
        "counters": counters,
        "closure": closure,
        "escape_pressed": escape_pressed,
        "link": link,
    }
