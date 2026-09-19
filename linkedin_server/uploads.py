"""The file a caller may hand to a browser, and the eight things it may not be.

THIS MODULE EXISTS BECAUSE UPLOADING IS A DIFFERENT CAPABILITY FROM TYPING.
``tests/test_readonly.py`` carried that sentence as a refusal for two days:

    A fill puts his words in a box; a file input puts a FILE from this machine
    into somebody else's inbox, chosen by a path string.

The operator has since opened the capability -- profile photo, post media and
message attachments, all three -- so the sentence stops being a refusal and
becomes a SPECIFICATION. Everything below is what "chosen by a path string"
has to be narrowed to before that is safe.

WHAT IS ACTUALLY NEW HERE, stated plainly so it is not lost among the checks.
Every other act this package performs operates on something ALREADY ON THE
PAGE: a control the reader found, a string sliced out of the grant the
operator approved. The browser is pointed at LinkedIn and reads back what
LinkedIn drew. An upload is the first act that reaches the OTHER WAY -- it
takes a path naming a file on this machine and hands its bytes to a remote
party. Nothing in the read-only boundary is about that direction, because
until now nothing went that way.

So the protection is not the url allowlist and not the mutation scanner. It is
this module, and it is made of five separate properties:

1.  **A DECLARED ROOT.** ``config.UPLOAD_ROOT`` and nothing outside it. An
    unbounded path names a private key as easily as a photograph, and the two
    are indistinguishable to a string comparison. Putting a file in the root
    is an act the operator performs with his own hands; it is the only part of
    this whole mechanism that cannot be faked by a caller.

2.  **NO SYMLINK, ANYWHERE ALONG THE CHAIN.** A symlink is a path that names
    one file and reads another, which defeats every other check here by
    construction: the name is inside the root, the bytes are not. Checked
    per-component AND, separately, by comparing the real path against the root
    -- see :func:`_refuse_a_link_in_the_chain` for why one check is not enough
    on Windows.

3.  **A REGULAR FILE THAT EXISTS AND CAN BE READ.** A directory, a device, a
    named pipe and a dangling link each fail differently and confusingly at
    the browser; they fail here instead, by name.

4.  **FACTS THE OPERATOR CAN CHECK.** Size, extension and name go into the
    preview, because he is approving an UPLOAD and "a file" is not something a
    person can consent to. A filename is itself often identifying.

5.  **A DIGEST, SO THE BYTES ARE THE BYTES HE SAW.** The grant binds the
    PATH. A path is not a file: between the preview and the confirmation
    -- ``GRANT_TTL_SECONDS`` apart -- whatever sits at that path can change,
    and the token would still match. :func:`digest_of` is read at preview
    time, printed in the block, and re-read at the drain point; a mismatch is
    a refusal. Without it, "the bytes uploaded are provably the bytes the
    preview showed him" is a hope rather than a property.

WHAT THIS MODULE DELIBERATELY DOES NOT DO: restrict the extension. The
operator opened photo, video, document and attachment paths; an allowlist of
suffixes here would be this server re-deciding a question he already answered,
and narrower than his ruling rather than safer than it. The extension is
REPORTED so he can see it, and a file with no extension at all is reported as
having none rather than refused for it.

NOTHING HERE TOUCHES A BROWSER. This module opens files for reading and
nothing else: no page, no navigator, no network. That is why it can be tested
exhaustively without one, and why every refusal below is shown failing in
``tests/test_uploads.py`` rather than argued for in a comment.

EVERY REFUSAL NAMES WHAT IT SAW. A guard that says "refused" teaches nothing
and gets worked around by guessing; one that says "that is a directory" or
"that resolves to somewhere outside the root" is a guard the operator can
act on. Paths in those messages are rendered through :func:`config.display`,
because an absolute path on this machine carries a username.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from linkedin_server import config
from linkedin_server.errors import WriteAttemptError

__all__ = [
    "DIGEST_CHARS",
    "MAX_UPLOAD_BYTES",
    "READ_CHUNK_BYTES",
    "UploadFile",
    "digest_of",
    "resolve_upload_file",
    "upload_root",
]


#: THE CAP IS THIS SERVER'S, NOT LINKEDIN'S -- and it is written that way for
#: the same reason ``writes.MAX_TARGET_CHARS`` is: nobody here has measured
#: what LinkedIn accepts, and a number presented as LinkedIn's when it is ours
#: is an unmeasured claim wearing somebody else's authority.
#:
#: WHAT IT IS ACTUALLY FOR. Two things, neither of them "LinkedIn will reject
#: it". A file this server hashes twice -- once at preview, once at the drain
#: point -- is a file it reads twice, and the second read happens with a
#: composer open and a confirm token live. And a cap is the difference between
#: a mistyped path costing a refusal and costing a minute of disk.
MAX_UPLOAD_BYTES = 25 * 1024 * 1024

#: Read size for hashing. Chosen to keep a large file off the heap; it has no
#: bearing on what is accepted.
READ_CHUNK_BYTES = 1024 * 1024

#: How much of the sha256 is printed and compared. Sixteen hex characters is
#: 64 bits, which is not a security claim and is not being asked to be one --
#: this compares a file against ITSELF minutes later, so the adversary is a
#: mistake, not a collision search. The full digest in a preview block is
#: noise a reader cannot check either way.
DIGEST_CHARS = 16


def upload_root() -> Path:
    """The declared root, read fresh rather than frozen into a constant.

    Fresh for the same reason :func:`config.known_paths` is: the directory is
    overridable by environment variable, and a test that points it at a temp
    directory must get the guard pointed there too. A module-level constant
    captured at import would make every check in this file answer about the
    directory that existed when the process started.
    """
    return Path(config.UPLOAD_ROOT)


@dataclass(frozen=True)
class UploadFile:
    """One file, resolved and checked, with the facts a human needs to consent.

    FROZEN, so that nothing between the check and the upload can edit the path
    that was approved. The bytes can still change on disk -- that is what
    :func:`digest_of` is for -- but the object cannot.
    """

    #: The absolute, real path. What a browser would actually be handed.
    path: Path
    #: The file's own name, without any directory. Printed for him.
    name: str
    #: The extension including the dot, or ``""`` when the file has none.
    suffix: str
    #: Size in bytes, as ``stat`` reported it at check time.
    size_bytes: int

    @property
    def size_note(self) -> str:
        """The size in a unit a person reads, WITH the exact byte count.

        Both, never one: a rounded number is what he can judge and an exact
        one is what he can check, and a block that carries only the rounded
        form cannot be reconciled with anything.
        """
        if self.size_bytes >= 1024 * 1024:
            rounded = f"{self.size_bytes / (1024 * 1024):.2f} MB"
        elif self.size_bytes >= 1024:
            rounded = f"{self.size_bytes / 1024:.1f} KB"
        else:
            rounded = f"{self.size_bytes} bytes"
        return f"{rounded} ({self.size_bytes} bytes exactly)"

    def as_block(self, *, digest: Optional[str] = None) -> dict[str, Any]:
        """The FILE section of a confirm block.

        WHAT IT SAYS AND WHY EACH LINE IS THERE:

        * the NAME, because a filename is frequently identifying and he is
          about to hand it to LinkedIn along with the bytes;
        * the SIZE and the EXTENSION, because "a file" is not something a
          person can approve;
        * the ROOT it was measured against, because the check is only as good
          as the directory it checked against and he should see which one;
        * the DIGEST, so the same file can be recognised at the drain point;
        * and TWO SENTENCES that are the whole point of the block. Attaching
          is not sending, and an upload cannot be recalled once the thing it
          is attached to is submitted.

        THE PATH IS RENDERED, NOT PRINTED. ``config.display`` gives the
        anchor-relative or home-anchored form; the absolute one carries this
        machine's layout and, very often, a person's name.
        """
        block: dict[str, Any] = {
            "file_name": self.name,
            "extension": self.suffix or "NONE -- this file has no extension",
            "size": self.size_note,
            "path": config.display(self.path),
            "checked_against_root": config.display(upload_root()),
            "attaching_is_not_sending": (
                "Confirming this puts the file into the composer. It does not "
                "submit the post or send the message; the act that reaches "
                "LinkedIn is the submit that follows, and it is gated "
                "separately."
            ),
            "cannot_be_unsent": (
                "AN UPLOAD CANNOT BE UN-SENT. Once the post or message "
                "carrying this file is submitted, the file has left this "
                "machine and this server has no way to withdraw it. Removing "
                "the post afterwards does not unsend what was delivered, and "
                "nothing here will claim otherwise."
            ),
        }
        if digest is not None:
            block["sha256_prefix"] = digest
            block["what_the_digest_is_for"] = (
                "read now, and read again immediately before the file is "
                "handed to the browser. If the bytes at this path change in "
                "between, the upload is refused rather than performed on a "
                "file you did not see."
            )
        return block


def _refuse(message: str) -> "WriteAttemptError":
    """Every refusal in this module, scrubbed on the way out.

    ``config.scrub`` substitutes this server's own known absolute paths for
    their displayed form wherever they sit INSIDE prose -- which is the case
    that a rendered field cannot cover, because several messages here are
    built as f-strings and an ``OSError`` stringifies with the filename it
    failed on.
    """
    return WriteAttemptError(str(config.scrub(message)))


def _refuse_an_unusable_string(raw: Any) -> str:
    """The string itself, before the filesystem is consulted at all.

    A blank target and a target with a newline in it are both refused HERE
    rather than by a later check, because both would otherwise reach ``Path``
    and produce a message about a file rather than about the string that was
    given -- and the newline case is the one that matters: a target ends up
    inside a block a human reads, and a newline in it is how a reader is shown
    one thing while another is bound. ``writes._clean_target_part`` makes the
    same refusal for the same reason; this module repeats it rather than
    relying on it, because this module is callable on its own.
    """
    text = str(raw if raw is not None else "").strip()
    if not text:
        raise _refuse(
            "no file was named. An upload needs a path to a file inside "
            f"{config.display(upload_root())}, and an empty string names "
            "nothing."
        )
    for character in "\r\n\t":
        if character in text:
            raise _refuse(
                "the file path contains a control character "
                f"({character!r}). A path ends up inside a confirm block a "
                "human reads; a newline or a tab in one is how a reader is "
                "shown one path while another is opened."
            )
    if "\x00" in text:
        raise _refuse(
            "the file path contains a NUL byte. That is not a path this "
            "server will pass to anything."
        )
    return text


def _absolute_candidate(text: str) -> Path:
    """Where the given string points, before any check has been made.

    A RELATIVE PATH IS JOINED ONTO THE ROOT rather than onto the working
    directory, and that is a safety property rather than a convenience. This
    process's working directory is whatever launched it; resolving against it
    would make the same string mean different files in different sessions, and
    ``uploads/photo.png`` would silently escape the root the moment somebody
    started the server from one directory up. Joined onto the root, a relative
    path CANNOT name anything outside it except through ``..``, which the
    containment check below catches after resolution.

    An absolute path is taken as given and checked for containment like any
    other. It is not refused for being absolute: that is the spelling a caller
    reading a directory listing will naturally produce.
    """
    candidate = Path(text)
    if not candidate.is_absolute():
        candidate = upload_root() / candidate
    return candidate


def _refuse_a_link_in_the_chain(candidate: Path, root: Path) -> None:
    """No symlink on the path itself or on any directory above it, to the root.

    A SYMLINK IS A PATH THAT NAMES ONE FILE AND READS ANOTHER, which is
    precisely the shape every other check here is blind to: the name sits
    inside the root, the bytes do not. It is checked BEFORE existence, because
    a dangling link does not exist and would otherwise be reported as a
    missing file -- the least informative of the two true statements.

    TWO INDEPENDENT CHECKS, AND THE SECOND IS NOT BELT AND BRACES. Windows has
    a second kind of reparse point -- a directory junction -- that
    ``Path.is_symlink`` does not report as a link, and a junction inside the
    root pointing outside it would pass a per-component scan cleanly. So the
    real path is compared against the real root as well: a chain that
    redirects out of the root fails containment even where nothing on it
    reports itself as a link.

    THE PARENT WALK STOPS AT THE ROOT. Above it are directories the operator
    did not choose for this and this server has no business auditing; a link
    in ``C:\\Users`` is not a fact about this upload. Below it, every
    component is inside the boundary and every one of them can redirect.
    """
    chain: list[Path] = [candidate]
    for parent in candidate.parents:
        chain.append(parent)
        if parent == root:
            break
    for component in chain:
        try:
            is_link = component.is_symlink()
        except OSError:
            # A component that cannot even be lstat'd is not something to
            # proceed past on the assumption that it is fine.
            is_link = True
        if is_link:
            raise _refuse(
                f"{config.display(component)} is a symbolic link, so this "
                "path names one file and would read another. An upload is "
                "refused on any link along the chain, including a link to a "
                "file that is perfectly fine: the point is that what was "
                "approved and what would be sent are decided in two "
                "different places."
            )


def _real(path: Path) -> Path:
    """The path with every link and junction on it followed, or the path.

    ``os.path.realpath`` rather than ``Path.resolve`` so that a component
    which does not exist is not an error here: existence is a separate
    refusal with a better message, and a resolver that raised would take it
    away.
    """
    try:
        return Path(os.path.realpath(str(path)))
    except OSError:
        return path


def _refuse_outside_the_root(candidate: Path, root: Path) -> None:
    """Containment, measured on the REAL path against the REAL root.

    ON THE REAL PATH, because a check on the given spelling is a check on a
    string: ``<root>/../secrets/key`` is textually inside the root and is not
    inside it at all. On the real ROOT too, because the root itself can sit
    behind a link -- on macOS ``/tmp`` does, which is exactly the shape a test
    running in a temp directory produces, and a comparison of a resolved path
    against an unresolved root would refuse every legitimate file in it.

    ``Path.is_relative_to`` rather than a string prefix: ``<root>-backup`` has
    the root's spelling as a prefix and is a different directory.
    """
    real_candidate = _real(candidate)
    real_root = _real(root)
    if real_candidate == real_root or not real_candidate.is_relative_to(real_root):
        raise _refuse(
            f"{config.display(candidate)} is outside the directory this "
            "server may upload from. It resolves to "
            f"{config.display(real_candidate)}, and the declared root is "
            f"{config.display(real_root)}. Put the file inside that "
            "directory: the root is not a formality, it is the whole of the "
            "protection -- an unbounded path names a private key as readily "
            "as a photograph, and this server cannot tell them apart."
        )


def _refuse_a_thing_that_is_not_a_readable_file(candidate: Path) -> os.stat_result:
    """Exists, is a regular file, and can be read. Three answers, not one.

    Collapsed into a single "cannot use that file" these would be a message
    that fits every case and helps in none. A directory, a device, a named
    pipe and a file whose permissions exclude this process fail for four
    different reasons, and the reason is the only actionable part.
    """
    if not candidate.exists():
        raise _refuse(
            f"there is no file at {config.display(candidate)}. Nothing was "
            "uploaded and nothing was opened."
        )
    try:
        stat_result = candidate.stat()
    except OSError as exc:
        raise _refuse(
            f"{config.display(candidate)} could not be examined: {exc}"
        ) from exc
    if not candidate.is_file():
        what = "a directory" if candidate.is_dir() else "not a regular file"
        raise _refuse(
            f"{config.display(candidate)} is {what}. An upload takes one "
            "regular file; a directory, a device or a pipe would each fail "
            "somewhere inside the browser with a message about neither."
        )
    if not os.access(str(candidate), os.R_OK):
        raise _refuse(
            f"{config.display(candidate)} exists and this process cannot "
            "read it. That is a permissions answer, not a missing-file one, "
            "and it is worth telling apart."
        )
    return stat_result


def _refuse_a_size_that_will_not_do(candidate: Path, size_bytes: int) -> None:
    """Neither empty nor over the cap, and the two say different things."""
    if size_bytes == 0:
        raise _refuse(
            f"{config.display(candidate)} is empty (0 bytes). An empty file "
            "is almost always a half-written one, and uploading it would "
            "look exactly like uploading the file that was meant."
        )
    if size_bytes > MAX_UPLOAD_BYTES:
        raise _refuse(
            f"{config.display(candidate)} is {size_bytes} bytes and this "
            f"server's cap is {MAX_UPLOAD_BYTES}. THE CAP IS THIS SERVER'S "
            "AND NOT LINKEDIN'S -- nobody here has measured what LinkedIn "
            "accepts, so this is not a claim that LinkedIn would refuse it."
        )


def resolve_upload_file(raw: Any) -> UploadFile:
    """One path in, one checked :class:`UploadFile` out, or a refusal.

    THE ORDER OF THE CHECKS IS PART OF THE DESIGN, because each one earns the
    right to run the next and each produces the most informative true
    statement available at its point:

    1. the STRING, before the filesystem is consulted;
    2. the LINK CHAIN, before existence -- a dangling link does not exist, and
       "that is a link" beats "that is missing";
    3. CONTAINMENT, before the file is opened -- a path outside the root is
       refused without this server ever having touched it;
    4. EXISTS, IS A FILE, IS READABLE;
    5. SIZE.

    NOTHING IS OPENED UNTIL STEP 4 HAS PASSED, which is the property worth
    naming: a path outside the declared root is refused by a comparison, not
    by an ``open`` that failed. This server does not read a file to find out
    whether it was allowed to.
    """
    text = _refuse_an_unusable_string(raw)
    root = upload_root()
    if not root.is_dir():
        raise _refuse(
            "the upload directory does not exist. This server uploads only "
            f"from {config.display(root)}, and there is no such directory. "
            "Create it and put the file there -- that is the act that makes "
            "a file uploadable, and it is deliberately one this server will "
            "not perform for you."
        )
    candidate = _absolute_candidate(text)
    _refuse_a_link_in_the_chain(candidate, root)
    _refuse_outside_the_root(candidate, root)
    stat_result = _refuse_a_thing_that_is_not_a_readable_file(candidate)
    size_bytes = int(stat_result.st_size)
    _refuse_a_size_that_will_not_do(candidate, size_bytes)
    return UploadFile(
        path=_real(candidate),
        name=candidate.name,
        suffix=candidate.suffix,
        size_bytes=size_bytes,
    )


def digest_of(upload: UploadFile) -> str:
    """A short sha256 prefix of the file's CURRENT bytes.

    READ TWICE, AND THAT IS THE WHOLE REASON THIS EXISTS. The grant binds the
    PATH -- ``consume`` refuses a token whose target does not match -- and a
    path is not a file. Between the preview and the confirmation, whatever
    sits at that path can be replaced and the token still matches. This is
    read when the preview is built, printed in the block, and read again
    immediately before the browser is handed the file; a difference is a
    refusal.

    NOT A SECURITY CLAIM AND NOT ASKED TO BE ONE. It compares a file against
    ITSELF minutes later, so what it catches is a swap, an edit or a
    half-written file finishing -- a mistake, not a collision search.

    IT RE-CHECKS THE FILE RATHER THAN TRUSTING ITS ARGUMENT. An
    :class:`UploadFile` is frozen, so its path cannot have changed; the file
    at that path can have vanished or turned into a directory since, and
    reading it here without saying so would raise an OSError from inside the
    drain point instead of a refusal that names the cause.
    """
    path = upload.path
    if not path.is_file():
        raise _refuse(
            f"{config.display(path)} was a readable file when it was checked "
            "and is not one now. Nothing was uploaded."
        )
    hasher = hashlib.sha256()
    try:
        with open(path, "rb") as handle:
            while True:
                chunk = handle.read(READ_CHUNK_BYTES)
                if not chunk:
                    break
                hasher.update(chunk)
    except OSError as exc:
        raise _refuse(
            f"{config.display(path)} could not be read: {exc}. Nothing was "
            "uploaded."
        ) from exc
    return hasher.hexdigest()[:DIGEST_CHARS]
