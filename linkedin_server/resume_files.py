"""His stored resumes, one at a time, by the card's own options menu: DOWNLOAD one he names.

Census rows ``J 72`` (*Download a stored resume*) and ``P M4`` (*Download a
saved resume*) -- one capability in two slices, so ONE tool,
``linkedin_download_resume``. Lane build28, 2026-11-28, on the orchestrator's
order of that day (the lane's brief, plan section 3 "Lane B": "ONE
resume-download tool over the resume card's menu, using the C8 transport"),
over two of the live lane's captures of ``/jobs/application-settings/``:

* session 11, load 11 (``tests/fixtures/live11/application_settings_words.html``):
  four resume cards, each an ``h3`` holding the file's NAME, a date line, and
  an options button whose menu is EMPTY while closed;
* session 12, load 9 (``tests/fixtures/live12/c_rj26_3_resume_menu-open_words.html``):
  the FIRST card's options menu OPEN -- its trigger ``aria-expanded="true"``,
  its content ``aria-hidden="false"``, and in it TWO items, each a ``div``
  with an icon and one word: ``Delete`` (a furniture word the tracked copy
  keeps) and ``Download`` (by keyed shape). Closed on Escape, nothing chosen.

## WHAT IS PRESSED, IN ORDER, AND EVERY REFUSAL BEFORE IT

Refused BEFORE THE PAGE IS LOADED (the tool's own checks): the transport's
switch off (``LINKEDIN_ENABLE_CDP_DOWNLOADS``), a server not attached to his
browser (``D4-NO-OWN-BROWSER-CONTEXT`` scopes the transport to ATTACH), and a
file name that is not one :func:`linkedin_server.application_settings.read_application_settings`
returns -- the name must already be its own sanitised form, so the match below
is exact over one normalisation, the list tool's.

Then, on the one admitted page, refusing at the first failed step:

1. the page draws its heading, ``Resumes and application data``, once;
2. EXACTLY ONE card's ``h3`` reads the name he gave -- none, or two, refuses,
   naming the count: choosing between two cards of one name is choosing by
   position, for him;
3. that card draws EXACTLY ONE options trigger (``button[aria-expanded]``),
   reading CLOSED, with no menu item drawn; and no other card's trigger reads
   open -- a page already showing a menu is not the state the press starts from;
4. ONE click on that trigger (:func:`_press`, step ``open``); the menu waited
   for, bounded: the trigger reads open and items are drawn;
5. the items' words, each compared WHOLE against :data:`MENU_WORDS` -- the two
   words session 12 measured. A word outside it, or not exactly one
   ``Download``, refuses: the menu is closed by Escape and nothing in it is
   pressed. ``Delete`` is NEVER pressed here;
6. the Download item pressed ONCE (step ``download``), INSIDE the C8
   transport's capture (``cdp_download.capture_download``), which sets where
   his browser writes a download before the press and sets it back after,
   names the file itself (``resume`` and the card's own suffix) and checks its
   first bytes against the kind the card's name says;
7. the menu read again; if it still reads open, ONE Escape on the trigger
   (step ``close``), and the closure verified.

AFTER EACH PRESS, A REFUTER STOPS EVERYTHING: the address moved, or a dialog
drawn. And after the download, the page is re-read for what a download never
changes -- the number of resume cards, the named card still drawn once, both
switches' states -- and any difference is reported as ``page_changed``, loud.

## WHAT THIS IS NOT

Not a write: a download asks LinkedIn for a file HE uploaded and sends nothing
outward -- it notifies no member, changes no setting, stores nothing on
LinkedIn. Not a navigation: nothing here calls ``goto``. Not the profile PDF
of census ``P C8``: that press, behind the profile's More menu, is still
unwired, and ``tests/test_profile_pdf_download_is_blocked_on_transport.py``
still says so -- this module is the transport's one caller it names.

## WHAT LEAVES

Counts, closed words and the transport's own verdict: whether the file was
saved, where (``config.display``'s form, never an absolute path), its size,
whether its first bytes match its kind, and how the menu ended. NOT the file
name he gave (he knows it), NOT any word the page drew outside the closed
vocabulary, and NOT the download's address: the transport never returns it.

## THE TWO WRITES BUILT TO REFUSE: THE DELETE (``P M3``) AND THE UPLOAD (``P M1``)

Ruled by the orchestrator in the lane's brief: "P M3 (delete) and P M1
(upload), each built REFUSING, in the J-19 shape ... P M1 stays GAP, because
its inverse P M3 can only be built refusing and the rule is
inverse-proven-first." ``writes`` holds both specs (``set_resume_deleted`` and
``set_resume_uploaded``, sanctioned and NOT performable) and their preview
reads, which are :func:`read_delete_control` and :func:`read_upload_control`
here -- COUNTS ONLY, pressing nothing -- and their refusals, which name the
capture that lifts each: what the ``Delete`` item opens, and what the page
does with a file handed to its input. Both are built so that one attended
session can run the upload and then the delete on a file he names.

## THE CALL SITES

``readonly.SANCTIONED_MUTATIONS`` holds two lines for this module, both in
:func:`_press`: the click (``open`` on the trigger, ``download`` on the item)
and the one Escape (``close``) -- the share-link module's precedent of one
drain point for a menu's trigger and its item, closed by Escape.
"""
from __future__ import annotations

from typing import Any, Optional

from linkedin_server import application_settings, cdp_download, coerce, people_data, press
from linkedin_server.errors import WriteAttemptError

_refuse = press._refuse

#: The one page this module presses on: the read boundary's admitted line for
#: it, exactly (``application_settings.PAGE_URL``).
PAGE_URL = application_settings.PAGE_URL

#: The page's main region and heading, as the shipped reader reads them.
MAIN = application_settings.MAIN
PAGE_HEADING = application_settings.PAGE_HEADING

#: Each card's file name: an ``h3`` in the main region (measured: four, one per
#: card, on both captures). The card is its grandparent: the ``h3``'s parent
#: holds the name and the date line, and ITS parent holds that and the
#: options-button container (session 12, load 9).
CARD_NAMES = MAIN + " h3"

#: The card's options trigger and its menu's items, inside the card only.
#: Measured on session 12's open capture: ONE ``button[aria-expanded]`` per
#: card, and each item a ``div`` whose class names it an
#: ``artdeco-dropdown__item`` (an attribute read, never a label).
TRIGGER = "button[aria-expanded]"
ITEMS = 'div[class*="artdeco-dropdown__item"]'

#: Every options trigger in the main region: the denominator for "no other
#: card's menu is open".
ALL_TRIGGERS = MAIN + " " + TRIGGER

#: A dialog anywhere on the page, the refuter's count.
DIALOGS = 'div[role="dialog"]'

#: The two switches, by their inputs, as the shipped reader finds them.
SWITCHES = MAIN + ' input[role="switch"]'

#: THE MENU'S WORDS, CLOSED: exactly the two session 12 measured, each to this
#: module's own key. A word outside this table is never pressed and never
#: returned.
MENU_WORDS: dict[str, str] = {"Delete": "delete", "Download": "download"}
DOWNLOAD_WORD = "Download"

#: THE STEPS, CLOSED. ``open`` and ``download`` are one click each -- on the
#: card's trigger, then on its Download item -- and ``close`` is the one key
#: ``Escape`` on the trigger. There is no step that types, and none that
#: presses Delete.
STEPS: dict[str, str] = {"open": "click", "download": "click", "close": "Escape"}

#: The file the transport saves, named by THIS server, never by the page: the
#: label, and the suffix of the kind the card's own name says.
LABEL = "resume"
SUFFIXES: dict[str, str] = {"pdf": ".pdf", "docx": ".docx", "doc": ".doc", "other": ""}

#: The first bytes each kind begins with. ``other`` has none, so its file is
#: saved unchecked and ``magic_ok`` stays ``None``.
MAGIC: dict[str, Optional[bytes]] = {
    "pdf": b"%PDF-",
    "docx": b"PK\x03\x04",
    "doc": b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1",
    "other": None,
}

#: The longest file name matched: the shipped reader's own cap.
FILE_NAME_CAP = application_settings.FILE_NAME_CAP

#: The most cards, triggers and items counted. A cost ceiling, not a measured
#: LinkedIn limit; the captures draw four cards and two items.
MAX_PARTS = 60

#: Bounded waits: the menu opening after the click, and closing after the
#: download. A test sets ``POLL_MS`` to a few milliseconds.
POLLS = 12
POLL_MS = 250
CLICK_TIMEOUT_MS = press.CLICK_TIMEOUT_MS
READ_TIMEOUT_MS = application_settings.READ_TIMEOUT_MS

#: The two refusals the tool takes before it loads anything, in its own words.
DOWNLOADS_OFF = (
    "the download transport is off: set LINKEDIN_ENABLE_CDP_DOWNLOADS=1 in this "
    "server's environment to let it take a file. Nothing was loaded or pressed."
)
NOT_ATTACHED = (
    "this server is not attached to your own browser, and the download transport "
    "works only there (D4-NO-OWN-BROWSER-CONTEXT). Nothing was loaded or pressed."
)


def collapsed(text: Any) -> str:
    """White space collapsed and the ends trimmed; ``""`` for a non-string."""
    return " ".join(text.split()) if isinstance(text, str) else ""


def checked_file_name(file_name: Any) -> tuple[Optional[str], str]:
    """``(name, "")`` when ``file_name`` is a name the list tool can return,
    else ``(None, why)``. PURE, and the why never repeats the value.

    The list tool returns each name through ``people_data.sanitise`` with the
    shipped cap, so a name that is not already its own sanitised form -- an
    invisible character, a run of spaces, an end space, a name over the cap --
    is not one it returned, and the match below would not be exact.
    """
    if not isinstance(file_name, str) or not file_name:
        return None, "no file name was given; pass one name linkedin_application_settings returns."
    if len(file_name) > FILE_NAME_CAP:
        return None, f"the name is longer than {FILE_NAME_CAP} characters, the most the list tool returns."
    if people_data.sanitise(file_name, cap=FILE_NAME_CAP) != file_name:
        return None, (
            "the name is not in the form linkedin_application_settings returns "
            "it (an invisible character, a run of spaces or an end space); pass "
            "the name exactly as that tool returned it."
        )
    return file_name, ""


def kind_of(file_name: str) -> str:
    """The card's kind, by the name's own suffix: ``pdf``, ``docx``, ``doc``
    or ``other``. PURE: the shipped reader's rule."""
    return application_settings.resume_type(file_name) or "other"


def refused_before_load(reason: str, why: str) -> dict[str, Any]:
    """A refusal taken before the page is loaded: nothing was opened or pressed."""
    return {**_refuse(reason, why, terminal=False), "downloaded": False, "loaded": False}


async def _count(locator: Any) -> int:
    return coerce.as_count(await locator.count())


async def _text(locator: Any) -> str:
    try:
        return collapsed(await locator.inner_text(timeout=READ_TIMEOUT_MS))
    except Exception:  # noqa: BLE001 -- a part that cannot be read reads as nothing
        return ""


async def _attribute(locator: Any, name: str) -> Optional[str]:
    try:
        value = await locator.get_attribute(name, timeout=READ_TIMEOUT_MS)
    except Exception:  # noqa: BLE001 -- a part that cannot be read reads as nothing
        return None
    return value if isinstance(value, str) else None


async def _cards_named(page: Any, file_name: str) -> tuple[list[Any], int]:
    """The cards whose ``h3`` reads ``file_name`` exactly, and how many cards
    were seen. The name is compared HERE and never returned."""
    names = page.locator(CARD_NAMES)
    seen = min(await _count(names), MAX_PARTS)
    matched = []
    for index in range(seen):
        name = names.nth(index)
        read = people_data.sanitise(await _text(name), cap=FILE_NAME_CAP)
        if read == file_name:
            matched.append(name.locator("xpath=..").locator("xpath=.."))
    return matched, seen


#: An ARIA state, to this module's own word for it: the page's value is
#: compared and never kept.
_STATES = {"true": "true", "false": "false"}


def _state(value: Optional[str]) -> Optional[str]:
    """``"true"``, ``"false"`` -- this module's literals -- or ``None``."""
    return _STATES.get(value) if isinstance(value, str) else None


async def _switch_states(page: Any) -> list[str]:
    """Each switch's ``aria-checked``, in page order, as this module's own
    word for it (``unknown`` for anything else): the refuter's reading."""
    inputs = page.locator(SWITCHES)
    return [
        _state(await _attribute(inputs.nth(index), "aria-checked")) or "unknown"
        for index in range(min(await _count(inputs), 5))
    ]


async def _read_page_state(page: Any, file_name: str) -> dict[str, Any]:
    """COUNTS ONLY, before or after a press: the heading, the cards, the named
    card's trigger and items, every trigger reading open, the dialogs and the
    switches. Never raises; ``error`` is an exception TYPE name."""
    out: dict[str, Any] = {
        "headings": 0,
        "cards": 0,
        "named_cards": 0,
        "triggers": 0,
        "expanded": None,
        "items": 0,
        "open_triggers": 0,
        "dialogs": 0,
        "switches": [],
        "error": None,
    }
    try:
        headings = page.locator(MAIN + " h1")
        texts = [await _text(headings.nth(i)) for i in range(min(await _count(headings), 5))]
        out["headings"] = texts.count(PAGE_HEADING)
        cards, out["cards"] = await _cards_named(page, file_name)
        out["named_cards"] = len(cards)
        if len(cards) == 1:
            triggers = cards[0].locator(TRIGGER)
            out["triggers"] = await _count(triggers)
            if out["triggers"] == 1:
                out["expanded"] = _state(await _attribute(triggers, "aria-expanded"))
            out["items"] = min(await _count(cards[0].locator(ITEMS)), MAX_PARTS)
        every = page.locator(ALL_TRIGGERS)
        for index in range(min(await _count(every), MAX_PARTS)):
            if _state(await _attribute(every.nth(index), "aria-expanded")) == "true":
                out["open_triggers"] += 1
        out["dialogs"] = await _count(page.locator(DIALOGS))
        out["switches"] = await _switch_states(page)
    except Exception as exc:  # noqa: BLE001 -- the TYPE is the whole report
        out["error"] = type(exc).__name__
    return out


def facts(reading: Any) -> dict[str, Any]:
    """A reading's counts, coerced: what a result and a refusal carry."""
    reading = reading if isinstance(reading, dict) else {}
    out: dict[str, Any] = {
        key: coerce.as_count(reading.get(key))
        for key in ("headings", "cards", "named_cards", "triggers", "items",
                    "open_triggers", "dialogs")
    }
    out["expanded"] = _state(reading.get("expanded"))
    switches = reading.get("switches")
    out["switches"] = [_state(s) or "unknown"
                       for s in (switches if isinstance(switches, list) else [])]
    return out


def start_verdict(reading: Any) -> dict[str, Any]:
    """Steps 1 to 3, before any press. PURE."""
    observed = facts(reading)
    error = reading.get("error") if isinstance(reading, dict) else "unreadable"
    if error:
        return {**_refuse("unreadable", f"the page could not be counted ({error}); nothing was pressed.",
                          terminal=False), "observed": observed}
    if observed["headings"] != 1:
        return {**_refuse(
            "page_heading",
            f"the page draws its heading {PAGE_HEADING!r} {observed['headings']} time(s), "
            "where exactly once is required; nothing was pressed.",
            terminal=False), "observed": observed}
    if observed["named_cards"] != 1:
        return {**_refuse(
            "named_card_count",
            f"{observed['named_cards']} of the {observed['cards']} resume card(s) read the "
            "name given, where exactly one is required; nothing was pressed. Choosing "
            "between cards of one name would be choosing by position.",
            terminal=False), "observed": observed}
    if observed["triggers"] != 1:
        return {**_refuse(
            "trigger_count",
            f"the named card draws {observed['triggers']} options trigger(s), where exactly "
            "one is required; nothing was pressed.",
            terminal=False), "observed": observed}
    if observed["expanded"] != "false" or observed["items"] or observed["open_triggers"]:
        return {**_refuse(
            "menu_not_closed",
            f"the named card's trigger reads expanded={observed['expanded']!r} with "
            f"{observed['items']} item(s) drawn, and {observed['open_triggers']} trigger(s) "
            "on the page read open, so the page is not in the closed state this press "
            "starts from; nothing was pressed.",
            terminal=False), "observed": observed}
    return {"pressed": False, "start_ok": True, "observed": observed}


def menu_verdict(words: list[str]) -> dict[str, Any]:
    """Step 5, on the items' words as read. PURE; the words never leave --
    only this module's keys for the ones in :data:`MENU_WORDS`, and a count of
    any other."""
    keys = [MENU_WORDS[w] for w in words if w in MENU_WORDS]
    unknown = sum(1 for w in words if w not in MENU_WORDS)
    observed = {"menu_items": len(words), "menu_words": keys, "unknown_words": unknown}
    if unknown:
        return {**_refuse(
            "menu_word_unknown",
            f"the menu draws {unknown} item(s) whose word is not one of "
            f"{sorted(MENU_WORDS)}, so it is not the menu this press was measured on; "
            "nothing in it was pressed.",
            terminal=False), "observed": observed}
    if words.count(DOWNLOAD_WORD) != 1:
        return {**_refuse(
            "download_item_count",
            f"the menu draws {words.count(DOWNLOAD_WORD)} item(s) reading "
            f"{DOWNLOAD_WORD!r}, where exactly one is required; nothing in it was pressed.",
            terminal=False), "observed": observed}
    return {"pressed": False, "menu_ok": True, "observed": observed}


async def _press(target: Any, step: str) -> None:
    """THE ONLY CALLS IN THIS MODULE THAT ACT ON THE PAGE: ``open``, one click
    on the card's trigger; ``download``, one click on its Download item; and
    ``close``, one Escape on the trigger. Any other step is refused before the
    page is touched -- there is no step that types or presses Delete."""
    if step in ("open", "download"):
        await target.click(timeout=CLICK_TIMEOUT_MS)
        return
    if step == "close":
        # THE KEY IS WRITTEN HERE, LITERALLY, AND IT IS THE ONE IN ``STEPS``:
        # the read-path gate (tests/test_messaging_overview.py) reads a press
        # site's own text and admits it only as a dismissal it can see.
        await target.press("Escape", timeout=CLICK_TIMEOUT_MS)
        return
    raise WriteAttemptError(
        f"refusing step {step!r}: a resume card's menu is opened with one click, its "
        "Download item pressed with one click, and the menu closed with one Escape."
    )


async def _settle(page: Any, file_name: str, *, want_open: bool) -> dict[str, Any]:
    """Poll the page, bounded, until the named card's menu reads open (its
    trigger expanded, items drawn) or closed (not expanded, no item). Returns
    the last reading."""
    reading = await _read_page_state(page, file_name)
    for _ in range(POLLS):
        if reading.get("error"):
            break
        expanded = reading.get("expanded")
        items = coerce.as_count(reading.get("items"))
        if want_open and expanded == "true" and items >= 1:
            break
        if not want_open and expanded == "false" and items == 0:
            break
        await page.wait_for_timeout(POLL_MS)
        reading = await _read_page_state(page, file_name)
    return reading


async def _menu_words(card: Any) -> list[str]:
    items = card.locator(ITEMS)
    return [await _text(items.nth(i)) for i in range(min(await _count(items), MAX_PARTS))]


def _tabs(page: Any) -> Optional[int]:
    """How many tabs the page's context holds, or ``None`` if it cannot say.
    A property read; nothing is opened or closed."""
    try:
        return len(page.context.pages)
    except Exception:  # noqa: BLE001 -- a double or a closed context cannot say
        return None


def _changed(before: dict[str, Any], after: dict[str, Any]) -> list[str]:
    """What a download never changes, compared: closed words for each difference."""
    out = []
    if before["cards"] != after["cards"]:
        out.append("card_count")
    if after["named_cards"] != 1:
        out.append("named_card")
    if before["switches"] != after["switches"]:
        out.append("switches")
    if after["dialogs"] > before["dialogs"]:
        out.append("dialog")
    return out


async def download_resume(
    page: Any, landed: str, file_name: str, *, browser: Any
) -> dict[str, Any]:
    """Open the named card's menu, press Download inside the C8 capture, close.

    ``page`` is already on ``landed``, the address the caller's one load
    landed on; this module never navigates. ``file_name`` has passed
    :func:`checked_file_name`; ``browser`` is the attached Playwright browser
    (``cdp_download.attached_browser``) or ``None``. Returns a refusal
    (``refused`` and ``why``) or the reading; never raises for a page problem.
    """
    address = press.check_address(landed)
    if address.get("refused"):
        return {**address, "downloaded": False}
    if not application_settings.landed_on_the_page(landed):
        return {**_refuse("landed_elsewhere",
                          "the load did not keep the application settings page's own path; "
                          "nothing was read or pressed.", terminal=False),
                "downloaded": False}
    name, why = checked_file_name(file_name)
    if name is None:
        return {**_refuse("bad_file_name", why, terminal=False), "downloaded": False}
    # THE TRANSPORT'S OWN REFUSALS, TAKEN BEFORE ANY PRESS: the capture would
    # refuse them too, but only after the menu had been opened for nothing.
    if not cdp_download.downloads_enabled():
        return {**_refuse("downloads_disabled", DOWNLOADS_OFF, terminal=False), "downloaded": False}
    if browser is None:
        return {**_refuse("not_attached", NOT_ATTACHED, terminal=False), "downloaded": False}
    before = await _read_page_state(page, name)
    verdict = start_verdict(before)
    if verdict.get("refused"):
        return {**verdict, "downloaded": False}
    cards, _seen = await _cards_named(page, name)
    card = cards[0]
    trigger = card.locator(TRIGGER)
    address_before = str(page.url)
    tabs_before = _tabs(page)
    pressed = {"opens": 0, "downloads": 0, "escapes": 0}
    kind = kind_of(name)
    common: dict[str, Any] = {
        "downloaded": False,
        "type": kind,
        "pressed_steps": pressed,
        "condition_3_route": "structural_argument",
        "observed": {"before": facts(before)},
    }
    try:
        await _press(trigger, "open")
    except Exception as exc:  # noqa: BLE001 -- a click that cannot be made is a reading
        return {**_refuse("not_pressed",
                          f"the card's options trigger could not be pressed ({type(exc).__name__}); "
                          "nothing opened.", terminal=False),
                **common, "menu_closed": None}
    pressed["opens"] = 1
    opened = await _settle(page, name, want_open=True)
    common["observed"]["open"] = facts(opened)
    if str(page.url) != address_before:
        return {**_refuse("address_moved",
                          "the address moved after the menu's click, which opening a menu "
                          "never does; nothing more was pressed.", terminal=False),
                **common, "menu_closed": None}
    if facts(opened)["dialogs"] > facts(before)["dialogs"]:
        return {**_refuse("dialog_drawn",
                          "a dialog was drawn after the menu's click; nothing more was "
                          "pressed, and nothing in the dialog was touched.", terminal=False),
                **common, "menu_closed": None}
    if facts(opened)["expanded"] != "true" or not facts(opened)["items"]:
        return {**_refuse("did_not_open",
                          "the click drew no menu on the named card, so there was nothing "
                          "to press; nothing is Escaped, since an Escape with nothing of "
                          "ours open could close something else.", terminal=False),
                **common, "menu_closed": None}
    words = await _menu_words(card)
    menu = menu_verdict(words)
    common["observed"]["menu"] = menu["observed"]
    capture: Optional[dict[str, Any]] = None
    if not menu.get("refused"):
        item = card.locator(ITEMS).nth(words.index(DOWNLOAD_WORD))

        async def _trigger() -> None:
            await _press(item, "download")
            pressed["downloads"] = 1

        capture = await cdp_download.capture_download(
            browser,
            _trigger,
            label=LABEL,
            suffix=SUFFIXES[kind],
            expect_magic=MAGIC[kind],
        )
    moved = str(page.url) != address_before
    after = (await _read_page_state(page, name)) if not moved else {"error": "address_moved"}
    if not moved and not (facts(after)["expanded"] == "false" and not facts(after)["items"]):
        after = await _settle(page, name, want_open=False)
    if not moved and facts(after)["expanded"] == "true":
        try:
            await _press(trigger, "close")
            pressed["escapes"] = 1
        except Exception:  # noqa: BLE001 -- reported below as not closed
            pass
        after = await _settle(page, name, want_open=False)
    closed = (not moved) and facts(after)["expanded"] == "false" and not facts(after)["items"]
    common["observed"]["after"] = facts(after)
    common["menu_closed"] = closed
    tabs_after = _tabs(page)
    common["tabs_opened"] = (
        max(tabs_after - tabs_before, 0)
        if isinstance(tabs_before, int) and isinstance(tabs_after, int) else None
    )
    if capture is not None:
        common["transport"] = {
            key: capture.get(key)
            for key in ("why", "file", "bytes", "magic_ok", "downloads_began",
                        "other_downloads", "from_linkedin", "final_state",
                        "behaviour_restored", "restore_error", "error",
                        "context_created", "transport")
        }
    if moved:
        return {**_refuse("address_moved",
                          "the address moved after the Download press, so the page is not "
                          "shown as found and nothing more was pressed. Look at your browser.",
                          terminal=False), **common}
    changed = _changed(facts(before), facts(after))
    if changed:
        common["page_changed"] = changed
    if menu.get("refused"):
        return {**menu, **common, "observed": common["observed"]}
    if not closed:
        return {**_refuse("did_not_close",
                          "the menu did not read closed after the download and one Escape; "
                          "look at the page.", terminal=False), **common}
    assert capture is not None
    saved = bool(capture.get("saved"))
    common["downloaded"] = saved
    common["file"] = capture.get("file") if saved else None
    common["bytes"] = capture.get("bytes") if saved else None
    common["magic_ok"] = capture.get("magic_ok")
    if not saved:
        return {**_refuse(
            "download_not_saved",
            "the Download item was pressed and the transport took no file: "
            f"{capture.get('why')!r} (cdp_download.WHY). Nothing else was pressed.",
            terminal=False), **common}
    return {**common, "pressed": True}


# ---------------------------------------------------------------------------
# The two refusing writes' preview reads (P M3, P M1): counts, never a press
# ---------------------------------------------------------------------------

#: The state each refusing write's preview reads, else :data:`UNKNOWN`.
RESUME_LISTED = "resume_listed"
UPLOAD_OFFERED = "upload_offered"
UNKNOWN = "unknown"

#: The upload control's word and the page's labels, as the shipped reader
#: reads them (session 11; drawn again on session 12's load 9).
UPLOAD_LABEL = application_settings.UPLOAD_LABEL
LABELS = MAIN + " label"
FILE_INPUTS = MAIN + ' input[type="file"]'
PARAGRAPHS = MAIN + " p"


async def read_delete_control(page: Any, file_name: str) -> dict[str, Any]:
    """What the page draws around the named resume's options menu, in counts.

    READ ONLY, and never raises: the same reading the download takes before
    its first press (the heading, the cards, the named card's one trigger and
    whether it reads closed, any menu open, the dialogs), and nothing pressed
    to take it -- the menu that holds ``Delete`` is not opened by a preview.
    ``file_name`` is compared in the page and never returned.
    """
    name, _why = checked_file_name(file_name)
    reading = await _read_page_state(page, name or "")
    return {**facts(reading), "name_ok": name is not None,
            "delete_dialog_read": False, "error": reading.get("error")}


def delete_state_of(reading: Any) -> tuple[str, str]:
    """``(state, why)`` off a :func:`read_delete_control` reading. PURE."""
    reading = reading if isinstance(reading, dict) else {}
    if not reading.get("name_ok"):
        return UNKNOWN, "the name is not one linkedin_application_settings returns."
    verdict = start_verdict(reading)
    if verdict.get("refused"):
        return UNKNOWN, str(verdict.get("why"))
    return RESUME_LISTED, (
        "one card on the page reads the name given, with its one options "
        "trigger closed and no menu open."
    )


async def read_upload_control(page: Any) -> dict[str, Any]:
    """What the page draws around its upload control, in counts and the rule.

    READ ONLY, and never raises: the heading, the labels reading
    :data:`UPLOAD_LABEL` and how many name a file input by ``for``, the file
    inputs, the upload rule (``DOC, DOCX, PDF (5MB)`` measured, parsed into a
    closed list and an integer) and the resume cards. Nothing is pressed and
    no file is handed to anything.
    """
    out: dict[str, Any] = {
        "headings": 0, "upload_labels": 0, "bound_labels": 0, "file_inputs": 0,
        "rule": None, "cards": 0, "error": None,
    }
    try:
        headings = page.locator(MAIN + " h1")
        texts = [await _text(headings.nth(i)) for i in range(min(await _count(headings), 5))]
        out["headings"] = texts.count(PAGE_HEADING)
        inputs = page.locator(FILE_INPUTS)
        ids = [await _attribute(inputs.nth(i), "id") for i in range(min(await _count(inputs), 5))]
        out["file_inputs"] = len(ids)
        labels = page.locator(LABELS)
        for index in range(min(await _count(labels), MAX_PARTS)):
            label = labels.nth(index)
            if await _text(label) != UPLOAD_LABEL:
                continue
            out["upload_labels"] += 1
            target = await _attribute(label, "for")
            if target and target in ids:
                out["bound_labels"] += 1
        paragraphs = page.locator(PARAGRAPHS)
        for index in range(min(await _count(paragraphs), MAX_PARTS)):
            rule = application_settings.upload_rule(await _text(paragraphs.nth(index)))
            if rule is not None:
                out["rule"] = rule
        out["cards"] = min(await _count(page.locator(CARD_NAMES)), MAX_PARTS)
    except Exception as exc:  # noqa: BLE001 -- the TYPE is the whole report
        out["error"] = type(exc).__name__
    return out


def upload_state_of(reading: Any, *, suffix: str = "", size_bytes: int = 0) -> tuple[str, str]:
    """``(state, why)`` off a :func:`read_upload_control` reading, and the
    PAGE'S OWN VETO on the file named: a type its rule does not list, or a
    size over its cap, refuses. PURE; the file's name is never read here."""
    reading = reading if isinstance(reading, dict) else {}
    if reading.get("error"):
        return UNKNOWN, f"the page could not be read ({reading['error']})."
    if coerce.as_count(reading.get("headings")) != 1:
        return UNKNOWN, f"the page does not draw its heading {PAGE_HEADING!r} once."
    if coerce.as_count(reading.get("bound_labels")) != 1 or coerce.as_count(reading.get("file_inputs")) != 1:
        return UNKNOWN, (
            f"the page draws {coerce.as_count(reading.get('bound_labels'))} "
            f"{UPLOAD_LABEL!r} label(s) bound to its "
            f"{coerce.as_count(reading.get('file_inputs'))} file input(s), where "
            "exactly one of each is required."
        )
    rule = reading.get("rule")
    if not isinstance(rule, dict):
        return UNKNOWN, "the page draws no upload rule this reader knows, so no file is checked against it."
    kind = suffix.lower().lstrip(".")
    if kind not in rule.get("types", []):
        return UNKNOWN, (
            f"the page's own rule admits {sorted(rule.get('types', []))}, and the "
            "file named is not one of them."
        )
    if size_bytes > int(rule.get("max_megabytes", 0)) * 1024 * 1024:
        return UNKNOWN, (
            f"the page's own rule caps a resume at {rule.get('max_megabytes')} MB, "
            "and the file named is larger."
        )
    return UPLOAD_OFFERED, (
        "the page draws its one Upload resume control, bound to one file input, "
        "and the file named passes the page's own rule."
    )
