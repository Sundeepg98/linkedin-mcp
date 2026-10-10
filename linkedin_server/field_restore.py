"""THE CLEAR: an EMPTY original put back, and the one place an empty value is admitted.

THE PROBLEM, MEASURED LIVE (2026-10-10, census row P A8). The live proof of a
profile field is "test, then restore": set a harmless value with
``linkedin_update_profile_field``, verify it, then put the original back and
verify that. "Additional name" read EMPTY on his own profile, so its original
is the empty string -- and the restore could not be expressed.
``writes._clean_target_part`` refuses an empty component, because an empty
component lets two different targets canonicalise to one string and the whole
canonical string is what binds a confirm token. So
``linkedin_update_profile_field(field="Additional name", value="")`` was
refused, while the first write's receipt printed exactly that call under
``to_put_it_back``: a restore path that pointed at a refusal.

THE DESIGN, IN ONE SENTENCE. An empty value is admitted in exactly one place --
``update_profile_field``, for one named field -- and only while a RESTORE
RECORD says this server's own write to that field read its prior value as
exactly ``""`` before typing; the admitted target is spelled ``<field> :: ``
and is bound to a confirm token like any other target; and it is admitted ONCE.

THE RECORD (:class:`RestoreRecord`):

* WRITTEN BY ONE CALL SITE. :func:`record_empty_prior` is the only function
  that assigns into :data:`_RECORDS`, and ``writes.perform`` is its only
  caller -- on the FILL path, after a write whose verdict was VERIFIED and
  whose prior value was read as the empty STRING. ``None`` means the prior was
  not read, and an unread prior admits nothing: "I could not read it" and "it
  was empty" are the two answers this package refuses to conflate.
* SINGLE USE. :func:`spend` marks it used once the clear's fresh render reads
  the field empty, and a used record admits nothing.
* BOUNDED. :data:`RESTORE_TTL_SECONDS`, measured from the write that recorded
  it; an expired record admits nothing and is swept at the next record.
* PROCESS-LOCAL. Never on disk and never logged. A restart forgets every
  record, and a forgotten record admits nothing -- the field is then restored
  by hand in the editor, which is what he had before this module existed.
* IT HOLDS WHAT THE WRITE TYPED, kept out of every repr, because the clear
  checks that the field still holds exactly that before anything is typed:
  THIS SERVER ONLY CLEARS WHAT IT WROTE. A field he edited since is refused,
  not cleared.

WHAT THIS MODULE DOES NOT DO. It never parses a target and never touches a
page. The separator and the canonical spelling stay in ``writes``, which asks
this module two questions -- is a clear of this named field admissible, and
what should the gate and the receipt say about it -- and does the rest itself.
Nothing here composes a value: the only value a clear types is the empty
string, and that is the empty slice of the canonical target ``writes`` built.
"""
from __future__ import annotations

import dataclasses
import time
from typing import Any, Optional

#: HOW LONG A RECORD ADMITS ITS ONE CLEAR: thirty minutes from the write that
#: recorded it. Long enough for the "test, then restore" proof -- read the
#: first write back, preview the clear, read that block, confirm it -- and
#: short enough that a record cannot quietly outlive the session it was made
#: for. This server's choice, not LinkedIn's; nothing on LinkedIn's side was
#: measured to pick it.
RESTORE_TTL_SECONDS: int = 30 * 60

#: The tool a clear is called through: the same one whose write recorded it.
TOOL_NAME: str = "linkedin_update_profile_field"

#: The sentence a clear's preview carries, verbatim, beside ``clear: True``.
CLEAR_SENTENCE: str = (
    "THIS IS A CLEAR: it restores the empty value this server read before its "
    "own write to this field; the field will end empty."
)


def _now() -> float:
    """The clock every age here is measured on: ``time.monotonic``.

    A function rather than a bare reference so a test can move the clock for
    this module alone, without moving it for the grants beside it.
    """
    return time.monotonic()


def _minutes() -> int:
    return int(RESTORE_TTL_SECONDS // 60)


@dataclasses.dataclass(eq=False)
class RestoreRecord:
    """One admissible clear: which field, what this server typed, and when."""

    #: The CANONICAL field name -- the first half of the write's canonical
    #: target, exactly as ``writes`` canonicalised it.
    field: str
    #: What the recorded write TYPED. Out of the repr, so a record printed by
    #: accident never prints his value.
    typed: str = dataclasses.field(repr=False)
    #: ``time.monotonic()`` when the record was written.
    recorded_at: float
    used: bool = False

    def age(self) -> float:
        return _now() - self.recorded_at

    def expired(self) -> bool:
        return self.age() > RESTORE_TTL_SECONDS

    def seconds_left(self) -> int:
        return max(0, int(RESTORE_TTL_SECONDS - self.age()))


#: Restore records by CANONICAL FIELD NAME. Process-local, never written to
#: disk, and ASSIGNED INTO BY EXACTLY ONE FUNCTION, :func:`record_empty_prior`
#: -- ``tests/test_an_empty_original_is_restored_by_a_clear.py`` asserts that
#: off this module's own syntax tree, and that ``writes.perform`` is the one
#: place in the package that calls it.
_RECORDS: dict[str, RestoreRecord] = {}


def _sweep() -> None:
    """Drop every record past its life, so none holds a typed value longer
    than it can admit anything. Called on every record, never on a timer: a
    timer is a background task, and this module keeps no schedule of its own."""
    for name in [name for name, record in _RECORDS.items() if record.expired()]:
        _RECORDS.pop(name, None)


def record_empty_prior(field: str, typed: str) -> Optional[RestoreRecord]:
    """Record ONE admissible clear of ``field``: this server's verified write
    typed ``typed`` there over a prior value read as exactly ``""``.

    THE ONE WRITER OF :data:`_RECORDS`, and ``writes.perform`` is its one
    caller. A new record for a field replaces the old one: the newest write
    over an empty original is the one a clear would undo.

    IT NEVER RAISES, because its caller runs after the click: an input that
    cannot be a record -- no field, or nothing typed -- records nothing and
    returns None, and the receipt says no clear was recorded.
    """
    if not isinstance(field, str) or not field.strip():
        return None
    if not isinstance(typed, str) or not typed:
        return None
    record = RestoreRecord(field=field, typed=typed, recorded_at=_now())
    _RECORDS[field] = record
    _sweep()
    return record


def live_record(field: str) -> Optional[RestoreRecord]:
    """The record for EXACTLY this field if it is unused and unexpired, else None."""
    record = _RECORDS.get(field)
    if record is None or record.used or record.expired():
        return None
    return record


def why_no_clear(field: str) -> Optional[str]:
    """None when a live record admits ONE clear of exactly ``field``; else why
    not, in words. The words name the field and never a value."""
    record = _RECORDS.get(field)
    if record is None:
        return (
            "An empty value is admitted ONLY as a CLEAR: the restore of an "
            "empty original this server read, before its own verified write to "
            f"{field!r}, in this process. No such write is recorded for "
            f"{field!r}, so there is nothing an empty value would restore."
        )
    if record.used:
        return (
            f"The one clear this server recorded for {field!r} has already "
            "been used. A record admits ONE clear, and an empty value is "
            "admitted only as that clear."
        )
    if record.expired():
        return (
            f"The clear this server recorded for {field!r} has expired: it is "
            f"admitted only within {_minutes()} minutes of the write that "
            "recorded it. Clear the field by hand in the editor."
        )
    return None


def clear_verdict(field: str, current: Optional[str], kind: str) -> tuple[bool, str]:
    """May the clear of ``field`` type now? ``(proceed, why)``.

    Asked at the click, on the page about to be typed into, never at the
    preview: ``current`` is the field's value read live just before the fill
    (None when it could not be read) and ``kind`` the mutation the live control
    takes. Four refusals, each before anything is typed:

    1. the control is not a text field -- a clear TYPES the empty string;
    2. no live record admits it (none, used, or expired);
    3. the current value could not be read;
    4. the field no longer holds EXACTLY what this server's write typed -- he
       edited it since, and THIS SERVER ONLY CLEARS WHAT IT WROTE.

    No value appears in either answer.
    """
    if kind != "fill":
        return False, (
            f"{field!r} is drawn as a {kind!r} control, and a clear is the empty "
            "string TYPED into a text field; nothing else is cleared this way. "
            "Nothing was typed."
        )
    refusal = why_no_clear(field)
    if refusal is not None:
        return False, refusal + " Nothing was typed."
    record = _RECORDS[field]
    if current is None:
        return False, (
            f"{field!r}'s current value could not be read before the clear, so "
            "this server cannot show the field still holds what its own write "
            "typed. THIS SERVER ONLY CLEARS WHAT IT WROTE. Nothing was typed."
        )
    if current != record.typed:
        return False, (
            f"{field!r} no longer holds the value this server's own write typed "
            "into it -- it has been changed since. THIS SERVER ONLY CLEARS WHAT "
            "IT WROTE, so the clear is refused and nothing was typed; put the "
            "field back as you want it by hand in the editor."
        )
    return True, (
        f"{field!r} still holds exactly the value this server's own write typed "
        f"{int(record.age())} s ago, so the clear may restore the empty "
        "original that write read before typing."
    )


def spend(field: str) -> bool:
    """Mark the record for ``field`` USED: its one clear is done. Returns
    whether there was a record to mark. Never raises (its caller runs after
    the click), and marking can only ever admit less."""
    record = _RECORDS.get(field)
    if record is None:
        return False
    record.used = True
    return True


def clear_preview(field: str) -> dict[str, Any]:
    """What a clear's confirm block adds: that it IS a clear, said twice -- a
    field and a sentence -- and on what terms it is admitted."""
    record = live_record(field)
    return {
        "clear": True,
        "this_is_a_clear": CLEAR_SENTENCE,
        "clear_admissible": {
            "once": True,
            "seconds_left": 0 if record is None else record.seconds_left(),
            "in_this_process_only": True,
            "and_only_if": (
                "the field still holds exactly the value this server's own "
                "write typed -- read again, live, before anything is typed. A "
                "field changed since is refused, not cleared."
            ),
        },
    }


def clear_call(field: str) -> str:
    """The exact call that restores an empty original, for a receipt's
    ``to_put_it_back``: the call first, the terms after the ``#``."""
    return (
        TOOL_NAME + "(field=" + repr(field) + ", value='')  # A CLEAR: admissible "
        f"ONCE, within {_minutes()} minutes of this write, in this process only "
        "-- then confirm the token it returns"
    )


def recorded_note(
    record: Optional[RestoreRecord], performed: Any, kind: str
) -> dict[str, Any]:
    """The first write's receipt, when the value it overwrote was read EMPTY:
    whether a clear was recorded, and on what terms -- or why not. ``kind`` is
    the mutation the write's control took ('fill', 'select_option', ...)."""
    if record is None and kind != "fill":
        return {
            "recorded": False,
            "why": (
                f"the previous value was read as the empty string, but this "
                f"field's control took a {kind!r}, not typing, and only a TYPED "
                "field's empty original is restored by a clear. No clear is "
                "recorded; put the field back by hand in the editor."
            ),
        }
    if record is not None:
        return {
            "recorded": True,
            "admissible": "ONCE",
            "within_seconds": RESTORE_TTL_SECONDS,
            "in_this_process_only": True,
            "only_while": (
                "the field holds exactly the value this write typed; a field "
                "changed since is refused, not cleared"
            ),
            "why": (
                "the previous value was read as EXACTLY the empty string -- a "
                "string, not an unread null -- before this write typed, and "
                "this write was verified stored. So ONE empty value is admitted "
                "for this field, as a CLEAR, and nowhere else."
            ),
        }
    return {
        "recorded": False,
        "why": (
            "the previous value was read as the empty string, but this write "
            f"was not verified stored (performed: {performed!r}), so no clear "
            "is recorded: this server clears only what it can show it wrote. "
            "If the field holds anything now, clear it by hand in the editor."
        ),
    }


def spent_note(spent: bool, performed: Any) -> dict[str, Any]:
    """The clear's own receipt: it WAS a clear, and whether its record is spent."""
    return {
        "this_write_was_a_clear": True,
        "record_spent": bool(spent),
        "why": (
            "the field read exactly the empty string on a fresh render, so the "
            "one clear recorded for it is spent; another empty value for this "
            "field is refused."
            if spent
            else (
                f"the clear was not verified (performed: {performed!r}), so its "
                "record is NOT spent: while it lives, a further clear is still "
                "admitted, and still only if the field holds exactly what this "
                "server's write typed."
            )
        ),
    }


def discard_all() -> None:
    """Drop every record. ``writes.discard_all`` calls this, so the reset that
    drops every grant and every reading drops every admissible clear too."""
    _RECORDS.clear()
