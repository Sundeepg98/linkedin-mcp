"""Show every check this wave added going RED, then green.

A CHECK THAT CANNOT FAIL CERTIFIES NOTHING, and the checks added on
2026-09-21 are unusually easy to write in a form that certifies nothing:
"this grant refuses" is trivially true in a process where writes are disabled,
so a control that only ever runs behind the closed door proves the DOOR and
says nothing about the OBJECT.

Four sections, each printing its own red and its own green:

1. **THE FOUR REFUSALS.** ``refusinggrant.refusal_failures`` must convict an
   object that lacks each one, or it is a function that always returns ``[]``.
2. **THE DOORS.** ``consume`` and ``perform`` must refuse the object FOR ITS
   OWN REASONS, which cannot be shown while the process-wide flag refuses
   everything first. This section replaces ``writes.writes_enabled`` IN MEMORY
   -- never the environment variable, never on disk -- runs the two doors, and
   asserts the flag reads False again afterwards. **Nothing in this section
   can act:** the page it hands ``perform`` is ``tests.plantedpage.PlantedPage``,
   whose ``goto``, ``click`` and ``fill`` raise, so every refusal downstream of
   the ones being measured is still a hard stop.
3. **THE LEAK.** The family guard must convict ``writes._recipient_gate`` the
   moment the coercion that shipped until this wave is put back. The plant is
   not an invented mutation: it is ``int(value or 0)``, restored by rebinding
   ``coerce.as_count``, which ``writes.py`` reaches through the module and so
   sees at once.
4. **THE DERIVED ANCHOR.** Supplying ``_live_control`` a generic synthetic
   string instead of ``anchor_label_for``'s answer must measurably shrink what
   the reader reaches, or the derivation in ``refusinggrant.anchor_for`` is
   ceremony.
5. **THE READ URL.** ``writes._load`` recorded ``raises WriteAttemptError``
   while never running a line of its own: the generic synthetic string is
   refused by ``readonly.assert_read_url`` first. The two reasons must differ,
   or supplying the server's own address is ceremony too.

    venv/Scripts/python scripts/_check_the_refusing_grant_can_fail.py

Exit: 0 every section behaved, 1 a check could not fail, 2 it could not run.
"""

from __future__ import annotations

import asyncio
import os
import sys
import time
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from linkedin_server import coerce, writes  # noqa: E402
from linkedin_server.errors import WriteAttemptError  # noqa: E402
from tests import refusinggrant  # noqa: E402
from tests.plantedpage import NavigationAttempted, PlantedPage  # noqa: E402
from tests.test_readers_emit_no_page_string import (  # noqa: E402
    LEAKS,
    RETURNS_TEXT,
    discover_readers,
    drive,
)

#: The action every section uses when it needs one. ``send_message`` because
#: it is the spec whose target carries a subject component, which is what
#: reaches ``_recipient_gate``'s coercions at all.
SPEC = writes.SANCTIONED_WRITES["linkedin_send_message"]


def _print_failures(label: str, failures: list[str]) -> None:
    print(f"  {label}")
    if not failures:
        print("      (none -- this object carries all four refusals)")
    for line in failures:
        print(f"      CONVICTED: {line}")


def section_one_the_four_refusals() -> int:
    """Each refusal, shown convicting an object that lacks it."""
    print("1. THE FOUR REFUSALS")
    print()

    good = refusinggrant.grant_for(SPEC)
    _print_failures("the refusing grant:", refusinggrant.refusal_failures(good))
    if refusinggrant.refusal_failures(good):
        print("  FAIL: the object this wave supplies does not itself refuse.")
        return 1
    print()

    # FOUR OBJECTS, EACH MISSING EXACTLY ONE REFUSAL. A single all-permissive
    # object would prove the function can return something, not that it checks
    # four separate things -- and four separate things is the claim.
    lacking: list[tuple[str, Any]] = []

    live_token = writes.WriteGrant(
        action=SPEC.action, target=good.target,
        token="a-token-shaped-string", minted_at=time.monotonic(),
    )
    lacking.append(("a grant holding a non-empty token", live_token))

    registered = refusinggrant.grant_for(SPEC)
    registered.token = "registered-token-shaped-string"
    writes._GRANTS[registered.token] = registered
    lacking.append(("a grant present in writes._GRANTS", registered))

    unexpired = writes.WriteGrant(
        action=SPEC.action, target=good.target, token="",
        minted_at=time.monotonic(),
    )
    lacking.append(("a grant whose TTL has not run out", unexpired))

    consumed = refusinggrant.grant_for(SPEC)
    consumed.consumed = True
    lacking.append(("a grant already marked consumed", consumed))

    missed = []
    for label, obj in lacking:
        failures = refusinggrant.refusal_failures(obj)
        _print_failures(label, failures)
        if not failures:
            missed.append(label)
    writes._GRANTS.pop(registered.token, None)
    print()

    if missed:
        print("  FAIL: refusal_failures() convicted nothing on:")
        for label in missed:
            print(f"    {label}")
        print("        It cannot fail, so its empty list certifies nothing.")
        return 1
    print("  PASS: all four refusals convict an object that lacks them, and")
    print("        the supplied grant carries every one.")
    return 0


def section_two_the_doors() -> int:
    """``consume`` and ``perform``, with the process flag neutralised."""
    print()
    print("2. THE DOORS, WITH THE PROCESS FLAG NEUTRALISED IN MEMORY")
    print()

    if writes.writes_enabled():
        print("  FAIL: writes are ENABLED in this process. This script refuses")
        print("        to run its doors section against a live write boundary.")
        return 1
    env_before = os.environ.get(writes.WRITES_FLAG)

    grant = refusinggrant.grant_for(SPEC)
    page = PlantedPage()
    shipped = writes.writes_enabled
    admitted: list[str] = []
    refused: list[str] = []
    try:
        writes.writes_enabled = lambda: True  # type: ignore[assignment]

        # THE CONTROL FIRST. If consume() refuses EVERYTHING once the flag is
        # neutralised, then its refusal of our grant says nothing about our
        # grant. A registered, fresh, unconsumed grant must get through.
        control = writes.WriteGrant(
            action=SPEC.action, target=grant.target,
            token="control-token-shaped-string", minted_at=time.monotonic(),
        )
        writes._GRANTS[control.token] = control
        try:
            writes.consume(
                control.token,
                action=SPEC.action,
                target=refusinggrant.SYNTHETIC_RAW_TARGETS[SPEC.target_kind],
            )
            print("  CONTROL: consume() ADMITTED a registered, fresh grant --")
            print("           so a refusal below is about the object, not the door.")
        except WriteAttemptError as exc:
            print(f"  FAIL: consume() refused even the control grant: {exc}")
            return 1
        finally:
            writes._GRANTS.pop(control.token, None)
        print()

        try:
            writes.consume(
                grant.token,
                action=SPEC.action,
                target=refusinggrant.SYNTHETIC_RAW_TARGETS[SPEC.target_kind],
            )
            admitted.append("consume()")
        except WriteAttemptError as exc:
            refused.append(f"consume() -- {exc}")

        try:
            asyncio.run(writes.perform(page, page, grant))
            admitted.append("perform()")
        except NavigationAttempted as exc:
            # The page double stopped it. That is a REFUSAL BY THE HARNESS,
            # not by the grant, and reporting it as a pass would be the
            # loudest possible false green.
            admitted.append(f"perform() reached the browser ({exc})")
        except WriteAttemptError as exc:
            refused.append(f"perform() -- {exc}")
    finally:
        writes.writes_enabled = shipped  # type: ignore[assignment]

    for line in refused:
        print(f"  REFUSED: {line}")
    print()
    if admitted:
        print("  FAIL: these doors did NOT refuse the grant:")
        for line in admitted:
            print(f"    {line}")
        return 1
    if os.environ.get(writes.WRITES_FLAG) != env_before:
        print("  FAIL: this script changed the environment variable. It may not.")
        return 1
    if writes.writes_enabled():
        print("  FAIL: writes_enabled() is still True. The patch did not lift.")
        return 1
    print("  PASS: both doors refused the grant for ITS OWN reasons, with the")
    print(f"        process flag neutralised; {writes.WRITES_FLAG} was never set,")
    print("        and writes_enabled() reads False again.")
    return 0


def _shipped_int(value: Any, default: int = 0) -> int:
    """``int(value or 0)`` -- the line that shipped until 2026-09-21."""
    return int(value or default)


def section_three_the_leak() -> int:
    """The family guard, red on the coercion that shipped and green on its repair."""
    print()
    print("3. THE LEAK, PLANTED BY RESTORING THE COERCION THAT SHIPPED")
    print()

    readers = dict(discover_readers())
    subject = "writes:_recipient_gate"
    before = drive(readers[subject])[0]
    print(f"  before the plant: {subject} -> {before}")

    shipped = coerce.as_count
    try:
        coerce.as_count = _shipped_int  # type: ignore[assignment]
        planted = drive(readers[subject])[0]
        others = sorted(
            name for name, fn in readers.items()
            if name != subject and drive(fn)[0] == LEAKS
        )
    finally:
        coerce.as_count = shipped  # type: ignore[assignment]
    restored = drive(readers[subject])[0]

    print(f"  under the plant : {subject} -> {planted}")
    print(f"  after restoring : {subject} -> {restored}")
    print()
    if others:
        print("  ALSO RED UNDER THE PLANT, and that is expected rather than a")
        print("  gap -- the plant rebinds the helper package-wide, so every")
        print("  site repaired onto it comes back:")
        for name in others:
            print(f"    {name}")
        print()

    if planted != LEAKS:
        print("  FAIL: the guard did NOT convict the coercion that shipped.")
        print("        Its green on the repaired line therefore certifies nothing.")
        return 1
    if restored != RETURNS_TEXT:
        print(f"  FAIL: the subject did not return to {RETURNS_TEXT!r} once the")
        print(f"        plant was lifted (it reads {restored!r}), so the red above")
        print("        is not attributable to the plant.")
        return 1
    print("  PASS: the guard goes RED on the exact line this wave replaced and")
    print("        clears on its repair.")
    return 0


def section_four_the_derived_anchor() -> int:
    """A generic string for ``anchor`` must measurably shrink the drive."""
    print()
    print("4. THE DERIVED ANCHOR")
    print()

    from tests.plantedpage import SYNTHETIC_ARGUMENT

    async def verdict(spec: writes.WriteSpec, anchor: str) -> str:
        grant = refusinggrant.grant_for(spec)
        try:
            await asyncio.wait_for(
                writes._live_control(PlantedPage(), spec, grant, anchor), timeout=5.0
            )
        except BaseException as exc:  # noqa: BLE001 -- the class is the reading
            return f"raises {type(exc).__name__}"
        return "read the page"

    async def run() -> list[str]:
        lost = []
        for key in sorted(writes.SANCTIONED_WRITES):
            spec = writes.SANCTIONED_WRITES[key]
            derived = await verdict(spec, refusinggrant.anchor_for(spec))
            generic = await verdict(spec, SYNTHETIC_ARGUMENT)
            if derived != generic:
                lost.append(f"{spec.action}: derived={derived}  generic={generic}")
        return lost

    lost = asyncio.run(run())
    for line in lost:
        print(f"  DIFFERS  {line}")
    print()
    if not lost:
        print("  FAIL: the derived anchor changes nothing this harness can")
        print("        measure, so deriving it is ceremony. Delete anchor_for")
        print("        and pass the synthetic string.")
        return 1
    print(f"  PASS: {len(lost)} of {len(writes.SANCTIONED_WRITES)} actions reach")
    print("        their readings only with the anchor the server derives.")
    return 0


def section_five_the_read_url() -> int:
    """The generic synthetic string must produce a WRONG reason for ``_load``."""
    print()
    print("5. THE READ URL")
    print()

    from tests.plantedpage import SYNTHETIC_ARGUMENT

    async def reason(url: str) -> str:
        page = PlantedPage()
        try:
            await asyncio.wait_for(
                writes._load(page, page, url, surface="feed"), timeout=5.0
            )
        except NavigationAttempted as exc:
            return f"navigates ({exc})"
        except BaseException as exc:  # noqa: BLE001 -- the class is the reading
            return f"raises {type(exc).__name__}"
        return "returned"

    generic = asyncio.run(reason(SYNTHETIC_ARGUMENT))
    shipped = asyncio.run(reason(writes.FEED_URL))
    print(f"  with the generic synthetic string : {generic}")
    print(f"  with the server's own FEED_URL    : {shipped}")
    print()
    if generic == shipped:
        print("  FAIL: the url makes no difference, so supplying a shipped one")
        print("        is ceremony. Drop the rule in _argument_for.")
        return 1
    if "navigates" not in shipped:
        print("  FAIL: with a real read address this reader still does not")
        print(f"        reach its navigation ({shipped}); the recorded reason")
        print("        would be wrong in a new way.")
        return 1
    print("  PASS: the generic string was refused by the READ DOOR before the")
    print("        reader ran, which the baseline recorded as the write module")
    print("        refusing. The shipped address reaches the real ceiling.")
    return 0


def main() -> int:
    print(__doc__.strip().splitlines()[0])
    print("=" * 70)
    print()
    codes = [
        section_one_the_four_refusals(),
        section_two_the_doors(),
        section_three_the_leak(),
        section_four_the_derived_anchor(),
        section_five_the_read_url(),
    ]
    print()
    print("=" * 70)
    failed = [i + 1 for i, code in enumerate(codes) if code]
    if failed:
        print(f"FAIL: section(s) {failed} did not behave in both directions.")
        return 1
    print(f"PASS: all {len(codes)} sections went red on a defect and green on its absence.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
