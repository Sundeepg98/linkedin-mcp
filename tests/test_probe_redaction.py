"""The messaging probe's redactor must fire, and must not fire on structure.

WHY THIS TEST EXISTS. ``scripts/_probe_messaging.py`` prints what it finds on
a live inbox. Its first version printed every aria-label and a slice of the
page text, which published real people's names and a live member urn into a
transcript, and wrote full-page captures of the inbox to disk. The redactor
that replaced all that is the only thing standing between a future run and the
same leak -- and a redactor is exactly the kind of code that looks fine while
doing nothing.

IT IS TESTED IN BOTH DIRECTIONS ON PURPOSE. A redactor that collapses every
input to ``<NAME>`` would pass a leak-only test perfectly while destroying the
structure the probe exists to report. Three real defects were found by running
these two directions against each other while writing it: base64 thread ids
passed through untouched, ``Conversation List`` was flattened to ``<NAME>``,
and a one-letter middle initial broke the name run so ``Jane Q Public``
survived intact.

NO REAL IDENTITY APPEARS IN THIS FILE, AND THAT SENTENCE WAS FALSE WHEN IT WAS
FIRST WRITTEN. The version of this file added by ``206ca3d`` carried the actual
member urn the probe had printed, and a thread id truncated from the real one
rather than invented -- so the test written to prove the redactor removes real
identifiers contained two of them. That is the same defect as the probe it
guards, one level up.

**A SELF-TEST NEEDS A SHAPE-VALID LITERAL, NEVER A TRUE ONE.** An invented
nine-digit id exercises exactly the same regex and proves exactly the same
property. Truncating a real value is not inventing one: the surviving prefix is
still real, which is how the thread id got through a guard that caught the urn.

Every literal below is now invented and chosen only for its SHAPE -- two plain
tokens, a middle initial, non-ASCII letters, a nine-digit id, an opaque base64
blob. The non-ASCII case is written as escape sequences so this file itself
stays ASCII while still handing the redactor a non-ASCII string at runtime.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_PROBE = Path(__file__).resolve().parents[1] / "scripts" / "_probe_messaging.py"


def _probe_module():
    spec = importlib.util.spec_from_file_location("_probe_messaging", _PROBE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


#: Inputs that MUST be changed. Every one is a shape that leaked, or that the
#: redactor was measured failing on while it was being written.
MUST_REDACT = [
    ("Select conversation with Dara Whitfield", "conversation template"),
    ("Message from Ivo Karlsson", "other template"),
    # Invented, not truncated. 123456789 is nine digits like a real member id
    # and is not anybody's; the thread blob is base64-shaped and shares no
    # prefix with any real conversation.
    ("urn:li:member:123456789", "member urn"),
    ("https://www.linkedin.com/messaging/thread/2-QUJDREVGSElKS0xNTk9Q==/", "thread id"),
    ("Jane Q Public", "bare name with a one-letter initial"),
    ("Ingr\u00edd \u00d6sterberg", "non-ascii name"),
]

#: Inputs that MUST SURVIVE. These are the probe's actual output vocabulary;
#: if the redactor eats them it reports nothing while appearing to work.
MUST_SURVIVE = [
    "Star conversation",
    "Conversation List",
    "Global Navigation",
    "Open messenger dropdown menu",
    "you are on the messaging overlay",
    "Date posted",
]


@pytest.mark.parametrize("value,why", MUST_REDACT, ids=[w for _, w in MUST_REDACT])
def test_identity_is_redacted(value: str, why: str) -> None:
    redacted = _probe_module()._redact(value)
    assert redacted != value, f"{why}: passed through unredacted"


@pytest.mark.parametrize("value", MUST_SURVIVE)
def test_structure_survives(value: str) -> None:
    assert _probe_module()._redact(value) == value


def test_the_probe_writes_no_capture() -> None:
    """The other half of the leak was files, not prints.

    Checked as a property of the SOURCE rather than by running it: the probe
    drives a live browser, so the only cheap way to assert it never writes a
    capture is that it contains no write call at all.
    """
    source = _PROBE.read_text(encoding="utf-8")
    for forbidden in ("write_text(", "write_bytes(", "open("):
        assert forbidden not in source, (
            f"{_PROBE.name} contains {forbidden!r}: this probe reads a live "
            "inbox and must never persist one"
        )


def test_probe_does_not_print_page_text() -> None:
    """A 900-character slice of the inbox is how the member urn escaped."""
    source = _PROBE.read_text(encoding="utf-8")
    assert "text head" not in source
