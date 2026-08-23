"""A credential leak detector that does not depend on the credential arriving
in the shape it left in.

WHY THIS MODULE EXISTS
----------------------
Every leak assertion in this package used to be one line::

    assert PLANTED_SECRET not in json.dumps(result)

Three things are wrong with that, and all three were MEASURED on this repo's
own suite (``scripts/leak_matrix.py``, first run, 2026-08-23: **34 of 54
cells green under a build that was deliberately leaking the operator's session
cookie**):

1. It is an EXACT SUBSTRING hunt. A result that base64s, hex-encodes or
   url-quotes the credential carries every bit of it and passes clean. This is
   the exact shape a sibling server in this family was caught by -- a
   plaintext marker hunted inside a base64url credential -- and it is why this
   module exists at all.
2. It is ALL-OR-NOTHING. A "safe fingerprint" that prints the first twelve
   characters, or a value split across two display fields, is a leak that the
   whole-string hunt cannot see.
3. It reads ONLY the return value, rendered through ``json.dumps``. A
   credential in a log record, in an exception's ``args``, in a ``bytes``
   leaf, or under a key rather than a value is invisible to it.

So the detector here does three different things instead:

* it hunts every RENDERING of the secret, not just the secret;
* it hunts RUNS of the secret, so a partial echo counts;
* it walks the WHOLE object -- keys, bytes, exceptions, unknown types via
  ``repr`` -- rather than one json string.

And separately from any of that, :func:`find_credential_shaped` hunts the
SHAPE of a LinkedIn session credential with no marker at all, so a leak of the
real ``li_at`` is caught on a path no test ever planted anything into. That is
the lesson the fixture privacy guard in ``tests/test_sdui_surfaces_fixture.py``
learned twice: a guard that is a list of known-bad strings cannot see the
class of thing it guards against.

Every function here is driven in BOTH directions by ``tests/test_leakwalk.py``
-- once at input it must reject, once at input it must pass -- and the whole
grid is re-driven at the real auth results by ``scripts/leak_matrix.py``.
"""

from __future__ import annotations

import base64
import json
import re
from typing import Any, Iterator, Optional, Sequence
from urllib.parse import quote

# ---------------------------------------------------------------------------
# The two numbers
# ---------------------------------------------------------------------------

#: The shortest run of a credential that counts as a leak. Twelve characters
#: of a 200-character base64url token is a 12 * 6 = 72-bit disclosure, and it
#: is also the size of the "safe fingerprint" that real programs print. Short
#: enough to catch a truncating redaction, long enough that no run this length
#: turns up in ordinary prose by accident.
MIN_RUN = 12

#: A marker shorter than this may not be hunted. A four-character marker like
#: ``"live"`` cannot be told from the English word, and a run-based detector
#: pointed at one would fire on ``live_check``. Forcing every planted secret to
#: be credential-LENGTH is half of forcing it to be credential-SHAPED, and the
#: measured consequence of not doing so is in this module's own docstring.
MIN_SECRET = 24


# ---------------------------------------------------------------------------
# The plant
# ---------------------------------------------------------------------------

#: The one fake credential every test in this package plants, defined ONCE so
#: no test can quietly weaken it back into a four-letter word.
#:
#: It is deliberately the LENGTH and CHARSET of a real ``li_at`` -- 190
#: base64url characters behind an ``AQEDAT`` prefix -- because the markers this
#: replaced (``"live"``, ``"x"``, ``"secret-token-value"``) were none of those
#: things, and a redaction bug that only fires on long high-entropy values
#: cannot be caught with a short readable one. ``test_leakwalk.py`` asserts it
#: matches :data:`LI_AT_SHAPE`, so it cannot drift back.
#:
#: It also reads as an obvious plant at a glance, which matters the one time
#: it shows up somewhere it should not.
PLANTED_LI_AT = (
    "AQEDATEST0THIS1IS2A3PLANTED4FAKE5SESSION6TOKEN7AND8MUST9NEVER0LEAK1"
    "AbCdEfGhIjKlMnOpQrStUvWxYz0123456789-_AbCdEfGhIjKlMnOpQrStUvWxYz01"
    "23456789-_AbCdEfGhIjKlMnOpQrStUvWxYz0123456789-_ZZ"
)

#: The csrf cookie's shape, quoted the way Chrome stores it. Short by nature,
#: so it is guarded by SHAPE rather than hunted as a run.
PLANTED_JSESSIONID = '"ajax:1234567890123456789"'


# ---------------------------------------------------------------------------
# 1. Renderings -- the same credential, spelled every way it escapes
# ---------------------------------------------------------------------------


def renderings(secret: str) -> dict[str, str]:
    """One credential in, every spelling it is known to leak in out.

    Keyed by name so a complaint can say WHICH encoding carried it, which is
    the difference between "something leaked" and a fix.
    """
    raw = secret.encode("utf-8")
    b64 = base64.b64encode(raw).decode("ascii")
    b64url = base64.urlsafe_b64encode(raw).decode("ascii")
    out = {
        "verbatim": secret,
        "b64": b64,
        "b64_nopad": b64.rstrip("="),
        "b64url": b64url,
        "b64url_nopad": b64url.rstrip("="),
        "hex": raw.hex(),
        "percent": quote(secret, safe=""),
        # repr() doubles backslashes and escapes control characters. An
        # OSError renders its filename this way, which already defeated an
        # exact-substring PATH check in this repo -- see config.known_paths.
        "repr": repr(secret)[1:-1],
        "backslash_doubled": secret.replace("\\", "\\\\"),
        # json.dumps escapes quotes, backslashes and (by default) every
        # non-ascii character. A marker carrying any of those does not survive
        # its own assertion, which is a way for a guard to be silently inert.
        "json_escaped": json.dumps(secret)[1:-1],
        "unicode_escape": raw.decode("utf-8").encode("unicode_escape").decode("ascii"),
        "lower": secret.lower(),
        "upper": secret.upper(),
    }
    # Collapse duplicates so a complaint names the encoding that is actually
    # distinct. For an ascii base64url credential several of these coincide,
    # and saying so is more honest than listing the same hit five times.
    seen: dict[str, str] = {}
    for name, text in out.items():
        if text not in seen.values() or name == "verbatim":
            seen[name] = text
    return seen


# ---------------------------------------------------------------------------
# 2. The walk -- every string this object can produce, however it is buried
# ---------------------------------------------------------------------------


def walk(obj: Any, path: str = "$") -> Iterator[tuple[str, str]]:
    """Yield ``(path, text)`` for every readable leaf under ``obj``.

    Deliberately total. Dict KEYS are walked as well as values (a credential
    used as a key is a credential); ``bytes`` are yielded both decoded and as
    ``repr``; exceptions are yielded as ``str``, ``repr`` AND per-argument; and
    anything this function does not recognise falls through to ``repr``, so an
    unknown type cannot be a hiding place. Silence about a leaf is the one
    failure mode a leak walker may not have.
    """
    if obj is None or isinstance(obj, bool):
        return
    if isinstance(obj, str):
        yield path, obj
    elif isinstance(obj, bytes) or isinstance(obj, bytearray):
        data = bytes(obj)
        yield path + "(bytes)", data.decode("latin-1")
        yield path + "(bytes-repr)", repr(data)
    elif isinstance(obj, (int, float)):
        yield path, str(obj)
    elif isinstance(obj, dict):
        for key, val in obj.items():
            here = f"{path}.{key}"
            if isinstance(key, str):
                yield here + "(key)", key
            yield from walk(val, here)
    elif isinstance(obj, (list, tuple, set, frozenset)):
        for i, item in enumerate(obj):
            yield from walk(item, f"{path}[{i}]")
    elif isinstance(obj, BaseException):
        yield path + "(str)", str(obj)
        yield path + "(repr)", repr(obj)
        for i, arg in enumerate(obj.args):
            yield from walk(arg, f"{path}.args[{i}]")
    else:
        yield path + "(repr)", repr(obj)


# ---------------------------------------------------------------------------
# 3. The hunt
# ---------------------------------------------------------------------------


def _runs(text: str, size: int) -> set[str]:
    if len(text) <= size:
        return {text}
    return {text[i : i + size] for i in range(len(text) - size + 1)}


def find_leaks(
    payload: Any,
    secret: str,
    *,
    min_run: int = MIN_RUN,
    extra: Sequence[str] = (),
) -> list[str]:
    """Return one complaint per way ``payload`` carries any of ``secret``.

    ``extra`` takes further haystacks that are not part of the payload -- a
    ``caplog.text``, a captured stdout -- so one call covers every channel a
    single tool call can leak down.

    Empty means clean. It is only allowed to mean that because
    ``tests/test_leakwalk.py`` drives this same function at a payload carrying
    each rendering and requires every one to come back non-empty.
    """
    assert len(secret) >= MIN_SECRET, (
        f"a {len(secret)}-character marker is too short to hunt for: a "
        f"run-based detector pointed at one fires on ordinary prose. Plant a "
        f"credential-shaped value of at least {MIN_SECRET} characters."
    )
    spellings = renderings(secret)
    haystacks: list[tuple[str, str]] = list(walk(payload))
    haystacks += [(f"extra[{i}]", str(text)) for i, text in enumerate(extra)]

    leaks: list[str] = []
    for name, rendered in spellings.items():
        size = min(min_run, len(rendered))
        wanted = _runs(rendered, size)
        for where, text in haystacks:
            hit = next((run for run in wanted if run in text), None)
            if hit is not None:
                whole = " (whole)" if rendered in text else f" ({size}-char run)"
                leaks.append(f"{where} carries the secret as {name}{whole}")
                break
    return leaks


# ---------------------------------------------------------------------------
# 4. The shape hunt -- for the credential nobody planted
# ---------------------------------------------------------------------------

#: LinkedIn's session cookie. Every ``li_at`` observed on this account begins
#: ``AQED`` and runs past 150 base64url characters; the pattern is loosened to
#: ``AQ`` + 40 so a shorter or differently-prefixed one is still caught.
LI_AT_SHAPE = re.compile(r"AQ[A-Za-z0-9_-]{40,}")

#: The csrf cookie LinkedIn issues, quoted exactly as Chrome stores it.
JSESSIONID_SHAPE = re.compile(r"ajax:\d{10,}")

#: Anything else that reads as an opaque high-entropy token. Tool results here
#: are short prose, urls and integers; a 40-character unbroken base64url run in
#: one is a credential until proven otherwise.
OPAQUE_RUN_SHAPE = re.compile(r"(?<![A-Za-z0-9_-])[A-Za-z0-9_-]{40,}")

CREDENTIAL_SHAPES = (
    ("li_at", LI_AT_SHAPE),
    ("JSESSIONID", JSESSIONID_SHAPE),
    ("opaque high-entropy run", OPAQUE_RUN_SHAPE),
)


def find_credential_shaped(
    payload: Any, *, allowed: Sequence[str] = (), extra: Sequence[str] = ()
) -> list[str]:
    """Return one complaint per credential-SHAPED token anywhere in ``payload``.

    No marker involved. This is the half of the guard that can catch a leak of
    the REAL ``li_at`` on a path no test planted anything into -- the failure
    a marker hunt is structurally incapable of seeing, because a marker hunt
    only knows the values it was told about.

    ``allowed`` is an EXACT list, never a shape: a loose exemption is how a
    real credential hides behind the guard, which is the failure this exists
    to close.
    """
    permitted = set(allowed)
    haystacks: list[tuple[str, str]] = list(walk(payload))
    haystacks += [(f"extra[{i}]", str(text)) for i, text in enumerate(extra)]

    out: list[str] = []
    for where, text in haystacks:
        for label, pattern in CREDENTIAL_SHAPES:
            for match in pattern.finditer(text):
                if match.group(0) in permitted:
                    continue
                out.append(f"{where} carries a {label}-shaped token")
                break
    return out


# ---------------------------------------------------------------------------
# 5. The assertion the tests actually call
# ---------------------------------------------------------------------------


def assert_no_leak(
    payload: Any,
    secret: str,
    *,
    caplog: Any = None,
    allowed: Sequence[str] = (),
    also: Sequence[str] = (),
) -> None:
    """Both halves of the guard, over the result AND the log, in one call.

    ``caplog`` is not optional in spirit: a credential that reaches a log file
    has left the process, and a leak test that reads only the return value was
    measured green against exactly that build.
    """
    extra: list[str] = list(also)
    if caplog is not None:
        extra.append(caplog.text)
        for record in caplog.records:
            extra.append(record.getMessage())
            extra.append(repr(record.args))

    leaks = find_leaks(payload, secret, extra=extra)
    assert not leaks, "credential leaked: " + "; ".join(leaks)

    shaped = find_credential_shaped(payload, allowed=allowed, extra=extra)
    assert not shaped, "credential-shaped token in output: " + "; ".join(shaped)
