"""What a file IS, read from its bytes -- and the one read a browser is handed.

Lane U, 2026-10-10. ``uploads.py`` decides WHICH file may be handed to a
browser and refuses everything else by name. This module adds what happens
between that decision and the hand-off, and it adds nothing to the decision.

1.  **THE TYPE, READ FROM THE BYTES.** A preview printed the file's name, its
    size and its extension -- and an extension is a claim the file's NAME
    makes. The bytes make their own claim, in their first few bytes, and the
    two can disagree (a PNG saved as ``notes.txt``). :func:`sniff` reads the
    signature and returns a closed vocabulary; the preview prints it beside
    the extension, and the hand-off declares it to the browser. It REFUSES
    NOTHING: an extension or type allowlist would narrow the operator's
    decision of 2026-09-04 (ruling FILE-UPLOAD-OPENED), and ``uploads.py``
    says why at length. An unrecognised signature is reported as one.

2.  **THE VERIFIED READ.** The preview prints a digest; the drain point used
    to re-read the digest, compare it, and then hand the browser the PATH. A
    browser reads a path when it is handed one -- or later -- so a file
    swapped after the comparison uploaded bytes nobody compared.
    :func:`read_once` reads the file ONCE, re-running every property the path
    guard enforces, and returns the bytes WITH the digest of exactly those
    bytes. The caller compares that digest and hands over those bytes as a
    payload; a swap on disk after the read changes nothing the browser holds.
    ``tests/test_upload_hands_over_verified_bytes.py`` shows the old hand-off
    uploading the swapped bytes and this one uploading the compared ones.

SECTIONS 1 AND 2 TOUCH NO BROWSER. They open one file for reading, which is
why they can be tested without one, and every refusal there is ``uploads``'s
own: one guard, one vocabulary.

3.  **THE CONVERSATION'S TWO FILE INPUTS, AIMED.** Measured on a real
    capture -- the live lane's session 3 drew a conversation's reply form
    (``tests/fixtures/live3/presence.html``): each of its two
    ``input[type=file]`` sits in its own ``div.msg-form__upload-attachment``
    beside ONE button, and the two buttons carry two different labels. An
    input is addressed by the label of the button it shares that wrapper
    with -- never by position, never by an id -- and its own ``accept``
    declaration, read as a closed token, must agree with the label.

4.  **THE READ-BACK BEFORE SEND.** After the file is handed over, the form
    must draw the file's name EXACTLY ONCE, hold no words, carry no recipient
    box, and show Send enabled -- or Send is not pressed. Read with the
    locator engine's exact text match inside the form; only counts and
    booleans leave.

5.  **THE VERIFICATION AFTER SEND.** A fresh load of the same conversation:
    did the count of messages drawing the file's name rise by exactly one,
    and is the last message his and one of them?

**SECTIONS 4 AND 5 ARE AIMED AT A PROPERTY, NOT AT CAPTURED MARKUP.** No
capture shows a composer holding an attachment, or a sent attachment message
(lane L5's capture C3 part b was never taken). So neither reads a class
name: each reads whether the file's NAME is drawn. If LinkedIn draws an
attachment without its name -- an image preview may -- the read-back refuses
and nothing is sent. That is the measurement the live proof takes first
(``_audit/2026-09-28-lane-u-uploads.md`` section 7).
"""

from __future__ import annotations

import hashlib
import io
import os
import pathlib
import time
import zipfile
from dataclasses import dataclass
from typing import Any, Optional

from linkedin_server import coerce, config, threads, uploads
from linkedin_server.errors import WriteAttemptError

__all__ = [
    "ATTACHMENT_HELD",
    "ATTACHMENT_SENT",
    "ATTACH_FILE_LABEL",
    "ATTACH_IMAGE_LABEL",
    "UNRECOGNISED_TYPE",
    "VerifiedBytes",
    "aim_verdict",
    "attachment_send_gate",
    "canonical_file",
    "facts_of",
    "input_for",
    "input_selector",
    "read_once",
    "read_reply_inputs",
    "read_sent_attachment",
    "sent_verdict",
    "sniff",
    "wait_for_attachment_drawn",
]

#: The type declared for bytes whose signature this module does not know. It
#: is the honest declaration for "unrecognised", and it refuses nothing.
UNRECOGNISED_TYPE = "application/octet-stream"

#: How much of the file the type is read from, where the whole file is not
#: needed. Every signature below sits inside it.
_HEAD_BYTES = 64

#: The OOXML parts that say which Office document a ZIP container is. Read
#: from the container's own directory, never from the file's name.
_OOXML_PARTS: tuple[tuple[str, str, str], ...] = (
    ("word/", "application/vnd.openxmlformats-officedocument."
              "wordprocessingml.document", "Word document (OOXML)"),
    ("xl/", "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet", "Excel workbook (OOXML)"),
    ("ppt/", "application/vnd.openxmlformats-officedocument."
             "presentationml.presentation", "PowerPoint presentation (OOXML)"),
)


def _zip_kind(data: bytes) -> tuple[str, str, str]:
    """A ZIP container's kind, from its directory, or a plain ZIP."""
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            names = archive.namelist()
    except (zipfile.BadZipFile, OSError, ValueError):
        return ("application/zip", "ZIP container (its directory did not read)",
                "document")
    if "[Content_Types].xml" in names:
        for prefix, mime, label in _OOXML_PARTS:
            if any(name.startswith(prefix) for name in names):
                return (mime, label, "document")
    return ("application/zip", "ZIP container", "document")


def sniff(data: bytes) -> tuple[str, str, str]:
    """``(mime_type, what_it_is, family)`` read from the file's own bytes.

    ``family`` is one of ``image``, ``video``, ``document`` or ``other`` -- a
    closed vocabulary the message composer's two file inputs are aimed by
    (an image goes to the input LinkedIn labels for images, anything else to
    the one it labels for files). Nothing is refused for its family.

    THE SIGNATURES ARE THE FORMATS' OWN, not LinkedIn's: PNG, JPEG, GIF and
    WebP images; ISO base-media video (MP4 and QuickTime share the ``ftyp``
    box); PDF; ZIP containers, read one level further for OOXML documents;
    the OLE2 container of legacy Office files; and text that decodes as UTF-8
    with no NUL byte. Anything else is ``application/octet-stream``, reported
    as unrecognised.
    """
    head = bytes(data[:_HEAD_BYTES])
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return ("image/png", "PNG image", "image")
    if head.startswith(b"\xff\xd8\xff"):
        return ("image/jpeg", "JPEG image", "image")
    if head.startswith((b"GIF87a", b"GIF89a")):
        return ("image/gif", "GIF image", "image")
    if head.startswith(b"RIFF") and head[8:12] == b"WEBP":
        return ("image/webp", "WebP image", "image")
    if head[4:8] == b"ftyp":
        brand = head[8:12]
        if brand == b"qt  ":
            return ("video/quicktime", "QuickTime video", "video")
        return ("video/mp4", "MP4 video (ISO base media)", "video")
    if head.startswith(b"%PDF-"):
        return ("application/pdf", "PDF document", "document")
    if head.startswith(b"PK\x03\x04"):
        return _zip_kind(bytes(data))
    if head.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"):
        return (UNRECOGNISED_TYPE,
                "legacy Office (OLE2) container -- which application's is not read",
                "document")
    if head and b"\x00" not in head:
        try:
            bytes(data[:4096]).decode("utf-8")
        except UnicodeDecodeError:
            pass
        else:
            return ("text/plain", "plain text (UTF-8)", "document")
    return (UNRECOGNISED_TYPE,
            "unrecognised -- no signature this server knows in its first bytes",
            "other")


@dataclass(frozen=True)
class VerifiedBytes:
    """One read of one file: the bytes, and the facts of EXACTLY those bytes.

    FROZEN, and the bytes are the point. The digest is of ``data`` and of
    nothing else, so comparing it against the preview's and then handing over
    ``data`` is one reading used twice -- never a check of one read and a
    hand-off of another.
    """

    name: str
    size_bytes: int
    digest: str
    mime_type: str
    what_it_is: str
    family: str
    data: bytes

    def as_payload(self) -> dict[str, Any]:
        """The hand-off: Playwright's ``{name, mimeType, buffer}`` form."""
        return {"name": self.name, "mimeType": self.mime_type, "buffer": self.data}

    def as_block(self) -> dict[str, Any]:
        """What the receipt says was handed over. Never the bytes."""
        return {
            "handed_over": "the verified bytes, not the path",
            "type_handed_over": self.mime_type,
            "bytes_handed_over": self.size_bytes,
        }


def _refuse(message: str) -> WriteAttemptError:
    return WriteAttemptError(str(config.scrub(message)))


def read_once(upload: uploads.UploadFile) -> VerifiedBytes:
    """Re-run the path guard, read the file ONCE, and digest what was read.

    EVERY PROPERTY ``uploads.py`` ENFORCES IS RE-RUN HERE, at the drain point,
    because the file was checked at preview time and the preview is up to
    ``GRANT_TTL_SECONDS`` old: the declared root, no link on the chain, a
    regular readable file, the size cap. A file that has since become a
    directory, a link or something outside the root is refused here by the
    guard's own message, not read.

    AND THE PATH MUST STILL RESOLVE TO THE ONE APPROVED. The re-run resolves
    the approved real path afresh; if it now resolves elsewhere, that is a
    different file under the same name, and it is refused.

    THE READ IS BOUNDED BY THE CAP. One byte past it is read so that a file
    that grew past the cap is refused rather than silently truncated -- a
    truncated upload would carry a digest of bytes he was never shown.
    """
    checked = uploads.resolve_upload_file(str(upload.path))
    if checked.path != upload.path:
        raise _refuse(
            f"{config.display(upload.path)} no longer resolves to the file "
            "that was approved: it now reads as "
            f"{config.display(checked.path)}. Nothing was uploaded."
        )
    try:
        with open(checked.path, "rb") as handle:
            data = handle.read(uploads.MAX_UPLOAD_BYTES + 1)
    except OSError as exc:
        raise _refuse(
            f"{config.display(checked.path)} could not be read: {exc}. "
            "Nothing was uploaded."
        ) from exc
    if not data:
        raise _refuse(
            f"{config.display(checked.path)} is empty now. Nothing was uploaded."
        )
    if len(data) > uploads.MAX_UPLOAD_BYTES:
        raise _refuse(
            f"{config.display(checked.path)} is now larger than this server's "
            f"cap of {uploads.MAX_UPLOAD_BYTES} bytes. Nothing was uploaded."
        )
    mime_type, what_it_is, family = sniff(data)
    return VerifiedBytes(
        name=upload.name,
        size_bytes=len(data),
        digest=hashlib.sha256(data).hexdigest()[: uploads.DIGEST_CHARS],
        mime_type=mime_type,
        what_it_is=what_it_is,
        family=family,
        data=data,
    )


def facts_of(
    upload: uploads.UploadFile, verified: "VerifiedBytes | None" = None
) -> dict[str, Any]:
    """The preview's lines about what the file IS, read from its bytes.

    From the caller's own :func:`read_once` when it has one, so the digest a
    block prints and the type it prints come from the same bytes; otherwise
    read here, through the same function. The name's own extension is
    printed beside it, and a disagreement is SAID, never refused.
    """
    if verified is None:
        verified = read_once(upload)
    suffix = upload.suffix.lower()
    return {
        "type_from_bytes": f"{verified.mime_type} -- {verified.what_it_is}",
        "family_from_bytes": verified.family,
        "the_name_and_the_bytes": _agreement(suffix, verified.mime_type),
    }


#: Which extensions each sniffed type is ordinarily saved under. Used ONLY to
#: say whether a name and its bytes agree; it refuses nothing.
_USUAL_SUFFIXES: dict[str, frozenset[str]] = {
    "image/png": frozenset({".png"}),
    "image/jpeg": frozenset({".jpg", ".jpeg", ".jfif"}),
    "image/gif": frozenset({".gif"}),
    "image/webp": frozenset({".webp"}),
    "video/mp4": frozenset({".mp4", ".m4v"}),
    "video/quicktime": frozenset({".mov"}),
    "application/pdf": frozenset({".pdf"}),
    "text/plain": frozenset({".txt", ".text", ".md", ".csv", ".log"}),
}


def _agreement(suffix: str, mime_type: str) -> str:
    usual = _USUAL_SUFFIXES.get(mime_type)
    if usual is None:
        return "not compared: this type has no single usual extension here"
    if not suffix:
        return "the name has no extension; the bytes say " + mime_type
    if suffix in usual:
        return "they agree"
    return (
        f"THEY DISAGREE: the name ends {suffix!r} and the bytes say "
        f"{mime_type}. The file is still uploadable -- nothing is refused for "
        "its type -- and the browser is told what the bytes say."
    )


def canonical_file(raw: Any) -> str:
    """A file component in canonical form: its path RELATIVE to the root.

    A target is printed in the preview, bound into a token and kept in a
    receipt, and an absolute path on this machine carries a username. The
    root-relative spelling names the same file -- ``uploads`` joins a relative
    path onto the root -- so re-normalising a canonical target is idempotent,
    and every property of the path guard has been enforced before a token
    exists for it.
    """
    upload = uploads.resolve_upload_file(raw)
    real_root = pathlib.Path(os.path.realpath(str(uploads.upload_root())))
    return upload.path.relative_to(real_root).as_posix()


# ---------------------------------------------------------------------------
# 3. The conversation's two file inputs, aimed
# ---------------------------------------------------------------------------

#: The wrapper each file input shares with ONE labelled button. Measured on a
#: real capture: ``tests/fixtures/live3/presence.html`` (the live lane's
#: session 3), lines 2413-2440 -- two wrappers, each holding two hidden
#: inputs, one ``input[type=file]`` and one button.
UPLOAD_WRAPPER = "div.msg-form__upload-attachment"

#: The two labels, exactly as that capture draws them on the buttons. The
#: inputs themselves carry no name (measured 2026-09-05, and the capture
#: agrees); the button beside each one is what LinkedIn labels.
ATTACH_IMAGE_LABEL = "Attach an image for your draft conversation"
ATTACH_FILE_LABEL = "Attach a file for your draft conversation"

#: Which input a file goes to, by the family read from its bytes, and the
#: ``accept`` declaration that input must carry, as ``threads``' closed token.
#: The declarations were read live on 2026-09-05 (``image/*`` on one input;
#: ``image/*`` plus documents, ``.mov`` and ``.mp4`` on the other); the
#: capture's skeleton keeps no attribute values, so the label is the aim and
#: the declaration is its cross-check, re-read live at the moment of aiming.
_IMAGE_INPUT = (ATTACH_IMAGE_LABEL, "images")
_FILE_INPUT = (ATTACH_FILE_LABEL, "images_and_documents")


def input_for(family: str) -> tuple[str, str]:
    """``(label, declaration)`` of the input a file of this family goes to.

    An image goes to the input LinkedIn labels for images; every other
    family -- video, documents, text, the unrecognised -- to the one it
    labels for files. Nothing is refused for its family here.
    """
    return _IMAGE_INPUT if family == "image" else _FILE_INPUT


def _wrapper_selector(label: str) -> str:
    return (
        f'{threads.REPLY_FORM_SELECTOR} {UPLOAD_WRAPPER}'
        f':has(> button[aria-label="{label}"])'
    )


def input_selector(label: str) -> str:
    """The file input inside the reply form's wrapper labelled ``label``."""
    return f'{_wrapper_selector(label)} > input[type="file"]'


async def read_reply_inputs(page: Any, family: str) -> dict[str, Any]:
    """Counts and one closed token: may a file of ``family`` be aimed here?"""
    label, wanted = input_for(family)
    out: dict[str, Any] = {
        "input_label": label,
        "declaration_wanted": wanted,
        "forms": 0,
        "wrappers": 0,
        "labelled_wrappers": 0,
        "inputs": 0,
        "declaration": None,
        "error": None,
    }
    try:
        out["forms"] = await threads._count(page.locator(threads.REPLY_FORM_SELECTOR))
        out["wrappers"] = await threads._count(
            page.locator(f"{threads.REPLY_FORM_SELECTOR} {UPLOAD_WRAPPER}")
        )
        out["labelled_wrappers"] = await threads._count(
            page.locator(_wrapper_selector(label))
        )
        inputs = page.locator(input_selector(label))
        out["inputs"] = await threads._count(inputs)
        if out["inputs"] == 1:
            out["declaration"] = threads._accept_shape(
                await inputs.first.get_attribute("accept")
            )
    except Exception as exc:  # noqa: BLE001 - reported as a type
        out["error"] = type(exc).__name__
    return out


def aim_verdict(reading: dict[str, Any]) -> tuple[bool, str]:
    """Is there exactly ONE input to hand this file to? ``(aimed, why)``.

    Every reason is built from counts and the closed token, never from page
    text: a refusal here reaches a receipt.
    """
    if reading.get("error"):
        return False, f"the reply form's inputs could not be read ({reading['error']})."
    forms = coerce.as_count(reading.get("forms"))
    labelled = coerce.as_count(reading.get("labelled_wrappers"))
    inputs = coerce.as_count(reading.get("inputs"))
    if forms != 1:
        return False, (
            f"the conversation drew {forms} reply form(s); exactly one is the "
            "measured shape. No file is handed to a form this server cannot "
            "tell apart from another."
        )
    if labelled != 1 or inputs != 1:
        return False, (
            f"the reply form drew {labelled} wrapper(s) beside a button "
            f"labelled {reading.get('input_label')!r}, holding {inputs} file "
            "input(s); exactly one of each is the measured shape. Nothing was "
            "aimed by position."
        )
    if reading.get("declaration") != reading.get("declaration_wanted"):
        return False, (
            f"the input beside that label declares {reading.get('declaration')!r} "
            f"and this server measured {reading.get('declaration_wanted')!r} "
            "there. The label and the declaration disagree, so which input "
            "this is cannot be said; nothing is handed to it."
        )
    return True, (
        "exactly one reply form, and in it exactly one file input sharing its "
        f"wrapper with the button labelled {reading.get('input_label')!r}, "
        f"declaring {reading.get('declaration')!r}."
    )


# ---------------------------------------------------------------------------
# 4. The read-back before Send
# ---------------------------------------------------------------------------

#: How long, after the file is handed over, its name is given to appear in
#: the form. A LIVENESS BOUND, NOT A SAFETY ONE: the wait decides nothing,
#: and :func:`attachment_send_gate` refuses on what it then finds. Not
#: measured on LinkedIn; an upload is slower than typing, so it is longer
#: than the reply's measured 5 s.
ATTACHMENT_DRAWN_WAIT_MS = 20_000


async def wait_for_attachment_drawn(
    page: Any, file_name: str, *, timeout_ms: Optional[int] = None
) -> dict[str, Any]:
    """Wait, BOUNDED, for the form to draw the file's name and Send to turn on.

    DECIDES NOTHING; ``failure`` is an exception's TYPE only.
    """
    bound = ATTACHMENT_DRAWN_WAIT_MS if timeout_ms is None else int(timeout_ms)
    out: dict[str, Any] = {"drawn": False, "waited_ms": 0, "failure": None}
    started = time.monotonic()
    try:
        form = page.locator(threads.REPLY_FORM_SELECTOR)
        await form.get_by_text(file_name, exact=True).first.wait_for(
            state="attached", timeout=bound
        )
        remaining = max(1, bound - int((time.monotonic() - started) * 1000))
        await page.locator(
            threads.REPLY_SEND_SELECTOR + ":not([disabled])"
        ).first.wait_for(state="attached", timeout=remaining)
        out["drawn"] = True
    except Exception as exc:  # noqa: BLE001 - a timeout is a reading, not a fault
        out["failure"] = type(exc).__name__
    out["waited_ms"] = int((time.monotonic() - started) * 1000)
    return out


async def attachment_send_gate(page: Any, *, file_name: str) -> dict[str, Any]:
    """May Send be pressed? Read AFTER the file was handed over.

    EXACTLY ONE ATTACHMENT, NAMING THE FILE: the form draws the file's name
    once -- not zero (the attachment did not appear, or appeared without its
    name, which no capture has measured), not two (a second attachment with
    the same name). AND NOTHING ELSE GOES WITH IT: the box holds no words, no
    recipient box is drawn, and Send is enabled -- it is measured DISABLED
    on an empty form, and the preview required it disabled, so its turning
    on is the attachment landing. The name is compared inside the page; only
    counts and booleans leave.
    """
    out: dict[str, Any] = {
        "proceed": False,
        "selector": threads.REPLY_SEND_SELECTOR,
        "observed": {},
        "why": "",
        "refused_condition": None,
    }
    try:
        form = page.locator(threads.REPLY_FORM_SELECTOR)
        editors = page.locator(threads.REPLY_EDITOR_SELECTOR)
        sends = page.locator(threads.REPLY_SEND_SELECTOR)
        observed = {
            "forms": await threads._count(form),
            "names_drawn": await threads._count(form.get_by_text(file_name, exact=True)),
            "editors": await threads._count(editors),
            "editor_empty": None,
            "recipient_boxes": await threads._count(
                page.locator(threads.RECIPIENT_BOX_SELECTOR)
            ),
            "send_controls": await threads._count(sends),
            "send_enabled": None,
        }
        if observed["editors"] == 1:
            observed["editor_empty"] = (
                threads._normalise(await editors.first.inner_text()) == ""
            )
        if observed["send_controls"] == 1:
            observed["send_enabled"] = bool(await sends.first.is_enabled())
    except Exception as exc:  # noqa: BLE001 - reported as a type
        out["refused_condition"] = "0_read_failed"
        out["why"] = (
            f"the reply form could not be read after the hand-off "
            f"({type(exc).__name__}). Send was not pressed."
        )
        return out
    out["observed"] = observed
    checks = (
        ("1_one_form", observed["forms"] == 1,
         f"{observed['forms']} reply form(s), not exactly one"),
        ("2_one_attachment_naming_the_file", observed["names_drawn"] == 1,
         f"the form draws the file's name {observed['names_drawn']} time(s), not "
         "exactly once -- the attachment did not appear, or appeared without "
         "its name (no capture has measured how LinkedIn draws one), or "
         "appeared twice"),
        ("3_no_words", observed["editor_empty"] is True,
         "the box is not empty, and only the file was confirmed"),
        ("4_no_recipient_box", observed["recipient_boxes"] == 0,
         f"{observed['recipient_boxes']} recipient box(es) drawn, so this is "
         "not the conversation's own form"),
        ("5_send_enabled", observed["send_controls"] == 1 and observed["send_enabled"] is True,
         f"{observed['send_controls']} Send control(s), enabled "
         f"{observed['send_enabled']!r}"),
    )
    for condition, holds, failed in checks:
        if not holds:
            out["refused_condition"] = condition
            out["why"] = f"{failed}. Send was not pressed; the file sits unsent in the composer."
            return out
    out["proceed"] = True
    out["why"] = (
        "exactly one reply form, drawing the file's name exactly once, holding "
        "no words, with no recipient box and Send enabled."
    )
    return out


# ---------------------------------------------------------------------------
# 5. The verification after Send
# ---------------------------------------------------------------------------

#: The verdicts. SENT needs a fresh load; HELD is read in place.
ATTACHMENT_SENT = "attachment_sent"
ATTACHMENT_HELD = "attachment_held_in_composer"


async def read_sent_attachment(page: Any, file_name: str) -> dict[str, Any]:
    """How many messages draw the file's name, and is the last one his and one of them."""
    out: dict[str, Any] = {
        "events": 0,
        "events_with_the_name": None,
        "last_has_the_name": None,
        "last_from": "unknown",
        "error": None,
    }
    try:
        events = page.locator(threads.EVENT_SELECTOR)
        count = await threads._count(events)
        out["events"] = count
        matcher = page.get_by_text(file_name, exact=True)
        out["events_with_the_name"] = await threads._count(events.filter(has=matcher))
        if count:
            last = events.nth(count - 1)
            items = await threads._count(last.locator(threads.ITEM_SELECTOR))
            others = await threads._count(last.locator(threads.OTHER_ITEM_SELECTOR))
            if items == 1 and others == 1:
                out["last_from"] = "other"
            elif items == 1 and others == 0:
                out["last_from"] = "him"
            out["last_has_the_name"] = await threads._count(last.filter(has=matcher)) == 1
        else:
            out["last_has_the_name"] = False
    except Exception as exc:  # noqa: BLE001 - reported as a type
        out["error"] = type(exc).__name__
    return out


def sent_verdict(
    before: dict[str, Any],
    after: dict[str, Any],
    *,
    held_in_place: Optional[bool],
    send_attempted: Optional[bool],
) -> tuple[str, str]:
    """``(state, why)``: SENT, HELD, or unknown -- from counts only."""
    if send_attempted is False:
        return ATTACHMENT_HELD, (
            "Send was never pressed, so nothing can have left. The file may "
            "still sit in the conversation's composer."
        )
    if held_in_place is True:
        return ATTACHMENT_HELD, (
            "after the press the form still drew the file's name with Send "
            "enabled: the attachment did not leave."
        )
    if after.get("error"):
        return "unknown", f"the conversation could not be re-read ({after['error']})."
    was = coerce.as_count(before.get("events_with_the_name"))
    now = coerce.as_count(after.get("events_with_the_name"))
    if (
        after.get("last_has_the_name") is True
        and after.get("last_from") == "him"
        and now == was + 1
    ):
        return ATTACHMENT_SENT, (
            f"a fresh load of the conversation draws the file's name in {now} "
            f"message(s), {was} before, and the last message is yours and is "
            "one of them."
        )
    return "unknown", (
        f"a fresh load draws the file's name in {now} message(s) against {was} "
        f"before; the last message is from {after.get('last_from')!r}. A sent "
        "attachment may be drawn without its name -- no capture has measured "
        "one -- so this is not read as NOT SENT. Open the conversation and look."
    )


async def held_in_place(page: Any, file_name: str) -> Optional[bool]:
    """In place, before any reload: does the form still draw the file, Send on?"""
    try:
        form = page.locator(threads.REPLY_FORM_SELECTOR)
        names = await threads._count(form.get_by_text(file_name, exact=True))
        sends = page.locator(threads.REPLY_SEND_SELECTOR)
        if await threads._count(sends) != 1:
            return None
        return names >= 1 and bool(await sends.first.is_enabled())
    except Exception:  # noqa: BLE001 - absent means "cannot tell"
        return None
