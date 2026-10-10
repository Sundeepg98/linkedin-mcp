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

NOTHING HERE TOUCHES A BROWSER. It opens one file for reading. That is why it
can be tested without one, and why every refusal is ``uploads``'s own,
re-raised unchanged: one guard, one vocabulary.
"""

from __future__ import annotations

import hashlib
import io
import zipfile
from dataclasses import dataclass
from typing import Any

from linkedin_server import config, uploads
from linkedin_server.errors import WriteAttemptError

__all__ = [
    "UNRECOGNISED_TYPE",
    "VerifiedBytes",
    "facts_of",
    "read_once",
    "sniff",
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
