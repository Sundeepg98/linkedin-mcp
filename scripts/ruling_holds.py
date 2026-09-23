"""The rulings, and the open questions, that HOLD census rows -- one table, read by two buckets.

THE DEFECT THIS EXISTS FOR, measured 2026-09-23, twice in one day and in two
different instruments.

  * ``scripts/census_completion.py`` described its bucket 1, the
    COVERED-UNFIRED rows, as *"BLOCKED ON A LIVE BROWSER SESSION ... no ruling,
    no design, no build"*. ``_audit/2026-09-23-bucket1-fires.md`` section 3
    classified the 21 rows left and a session was the whole cost for none of
    them: 15 were writes, 2 opened messaging, 2 would spend his unread
    notifications, 2 needed a press or a reader change.
  * ``_audit/_census/read-addresses.tsv`` classed ``M M49`` as blocked on
    nothing, because the shipped boundary admits ``/messaging/thread/<id>/``.
    The boundary was asked; the rulings were not -- and ``DO-NOT-OPEN-MESSAGING``
    then forbade opening messaging at all.

**ONE MISTAKE, TWICE: A COUNT OF WHAT THE CODE PERMITS, READ AS A COUNT OF WHAT
MAY BE DONE.** Both instruments asked a mechanism (the census state, the read
boundary) a question only a ruling answers. This module is the one place that
names the rulings and questions that hold rows, so both buckets ask it rather
than each re-deciding.

AND THE RULINGS MOVED THE SAME DAY, WHICH IS THE ARGUMENT FOR ONE TABLE
-----------------------------------------------------------------------
At 18:15 on 2026-09-23 the operator ruled "(b)": this server may connect,
message, apply, post and open messaging on his account. The orchestrator
relayed it to the wave that built this file, in writing, and registers it at
merge. It LIFTS ``DO-NOT-OPEN-MESSAGING`` and the read-only rule, and the
writes no longer wait on a no-write ruling: every one of them, and the two
messaging reads, wait on a live proof against a target HE names. Both buckets
changed by editing this table and the cells that cite it -- nothing else.

WHAT A ROW OF ``ROW_HOLDS`` SAYS
--------------------------------
``status``   ``STANDING`` -- a ruling in ``_audit/RULINGS.md``, made, and in
             force. ``RELAYED`` -- a ruling the operator has made and the
             orchestrator has relayed in writing, NOT YET IN THE REGISTER.
             ``PENDING`` -- a question put to the operator and NOT yet
             answered; it holds a row exactly as firmly until he answers, and
             it is never to be read as a ruling.
``binds``    ``write`` -- the hold binds an ACT: every write this server can
             fire is held by it with no marker needed, and a READ may cite it.
             ``surface`` -- the hold binds a PAGE: any address under
             ``surface`` is held, whatever the act.
``surface``  a path prefix, for ``binds == "surface"``.

**A STANDING SURFACE IS NOT TYPED HERE, IT IS CHECKED HERE.**
:func:`register_problems` re-reads every STANDING entry out of the rulings
register (``scripts/build_rulings_index.py::REGISTER``) and fails when the id
is gone, is no longer STANDING, or its BINDS no longer names the surface
written below.

**A RELAYED OR PENDING ENTRY IS RE-RESOLVED AGAINST ITS DOCUMENT**, its
``anchor`` required EXACTLY ONCE. A RELAYED entry fails the moment the register
carries its id -- the register has caught up, and the entry must become
STANDING with its BINDS checked. A PENDING entry fails the moment a registered
ruling binds its surface -- the question has been answered, and every row
citing it must be re-read against the answer.

**A LIFTED RULING IS KEPT, SO A STALE CITATION GOES RED.** ``LIFTED_ROW_HOLDS``
names each ruling that held rows and no longer does. A cell or a note still
citing one as a hold is reported by :func:`hold_of`, never silently counted.

HOW A ROW CITES ITS HOLD
------------------------
A census cell, or a note in ``read-addresses.tsv``, cites what holds its row
with the marker::

    **HELD BY `<ID>`**

``HELD_BY_MARKER`` reads the id and nothing else, and it is case-sensitive: the
prose "was held by" is a history, not a citation. It is a MARKER rather than a
mention on purpose -- cells cite rulings for many reasons, and a parser that
took every mentioned id as a hold would count a row's ARGUMENT as its state.
The same discipline as ``CORRECTS:``.

A write-direction row needs NO marker: its census R/W cell is the stronger
statement, and the hold whose ``binds`` is ``write`` binds every write. The
marker is for rows whose hold the direction cell cannot express -- a read, and
a write in ``jobs.md``, which has no R/W column
(``_audit/2026-09-21-the-jobs-direction.md`` argues it should not get one; a
hold citation is not that column).

PURE AT IMPORT, AND THAT IS A CONSTRAINT RATHER THAN A STYLE
------------------------------------------------------------
``census_completion.py`` imports this module, and
``scripts/_check_census_completion_can_fail.py`` runs it inside a copy of the
tree that holds only ``scripts/``, ``_audit/_census/`` and the row pin. The
rulings register imports a module under ``tests/`` at import time, so it is
imported inside :func:`register_problems` and nowhere else. The completion
figure COUNTS citations; resolving them is this module's ``main`` and the
tests'.

    python scripts/ruling_holds.py        # resolve every entry, exit 1 on drift

SHOWN FAILING: ``tests/test_ruling_holds.py``.
"""
from __future__ import annotations

import dataclasses
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


@dataclasses.dataclass(frozen=True)
class Hold:
    """What holds a row: a ruling in force, a ruling relayed, or a question open."""

    status: str
    binds: str
    surface: str = ""
    #: RELAYED and PENDING only: the document that records it, and its exact
    #: words there.
    document: str = ""
    anchor: str = ""
    #: One line a reader of the census output needs; printed beside the count.
    gist: str = ""


#: The id of the hold every write is held by, since the operator's 18:15
#: ruling of 2026-09-23. Named once because a rule turns on it: a W row is held
#: by it with no marker.
WRITE_HOLD_ID = "OPERATOR-NAMES-THE-TARGET"

#: Every hold a census row may cite TODAY, keyed by the id it is cited by.
ROW_HOLDS: dict[str, Hold] = {
    WRITE_HOLD_ID: Hold(
        status="RELAYED",
        binds="write",
        document="_audit/2026-09-23-census-cleanup.md",
        anchor="the linkedin MCP may connect, message, apply, post AND OPEN "
               "MESSAGING on his account",
        gist="a live proof against a target the operator names",
    ),
    #: NOT A RULING. The question put to him on 2026-09-23 after the SECOND
    #: wave reached the two notification rows and declined them on the same
    #: ground. Loading the page clears his unread badge and it does not come
    #: back, so a fire spends his state. The 18:15 ruling, as relayed, does
    #: not name notifications, so the question stands; the id is the
    #: question's, and it stops being cited the day he answers either way.
    "NOTIFICATIONS-UNREAD-SPEND": Hold(
        status="PENDING",
        binds="surface",
        surface="/notifications/",
        document="_audit/2026-09-23-bucket1-fires.md",
        anchor="may one `linkedin_notifications` call spend his unread "
               "notification state?",
        gist="may a fire spend his unread badge? It does not come back.",
    ),
}

#: Rulings that held census rows and NO LONGER DO, with when and by what. A
#: row still citing one of these as a hold is reported, never counted: the
#: citation is history, and the row has to be re-read.
LIFTED_ROW_HOLDS: dict[str, str] = {
    "DO-NOT-OPEN-MESSAGING": "lifted by the operator at 18:15 on 2026-09-23 "
                             "(his ruling (b), relayed by the orchestrator)",
    "NO-IRREVERSIBLE-WRITE-IS-FIRED": "holds no write of this server since "
                                      "the operator's ruling (b) at 18:15 on "
                                      "2026-09-23, relayed: a write waits on "
                                      "a target he names",
}

#: ``**HELD BY `<ID>`**`` -- the bold is optional, the backticked id is not.
HELD_BY_MARKER = re.compile(r"HELD BY `([A-Z0-9][A-Z0-9-]*[A-Z0-9])`")

#: The order holds are counted in when a row has more than one: a ruling in
#: force first, then a question open, then a ruling relayed whose condition
#: is still to be met. Among equals the first cited wins.
_PRECEDENCE = {"STANDING": 0, "PENDING": 1, "RELAYED": 2}


def cited(text: str) -> list[str]:
    """Every id ``text`` cites with the marker, first-cited first, once each."""
    seen: list[str] = []
    for hit in HELD_BY_MARKER.findall(text):
        if hit not in seen:
            seen.append(hit)
    return seen


def surface_hold(path: str) -> str | None:
    """The id of the hold whose surface ``path`` sits on, or None."""
    for hold_id, hold in ROW_HOLDS.items():
        if hold.binds == "surface" and path.startswith(hold.surface):
            return hold_id
    return None


def hold_of(direction: str, text: str) -> tuple[str | None, list[str]]:
    """(the id that holds a COVERED-UNFIRED row, or None; problems).

    ``direction`` is the census R/W cell as ``reader_closable_blockers
    .direction_of`` reads it; ``text`` is the row's cells. The rules, each of
    which is a statement the census makes and not one this function invents:

      * the row's own ``HELD BY`` citations are its holds;
      * a ``W`` row is also held by the hold whose ``binds`` is ``write``,
        with no marker -- the R/W cell says so;
      * ``R+W`` and ``ambiguous`` are REFUSED: which half holds the fire is a
        judgement for a person, and a counter that picked one would publish it;
      * an id that is not a hold this census knows is reported, and an id in
        ``LIFTED_ROW_HOLDS`` is reported as lifted -- neither is counted.

    Several holds: the first by ``_PRECEDENCE``. No hold at all is ``None`` --
    held by NO ruling. That is a finding about the rulings, not a default: the
    row's own cell says what remains.
    """
    problems: list[str] = []
    ids: list[str] = []
    for i in cited(text):
        if i in ROW_HOLDS:
            ids.append(i)
        elif i in LIFTED_ROW_HOLDS:
            problems.append(f"cites `{i}` as its hold, and that ruling is "
                            f"lifted -- {LIFTED_ROW_HOLDS[i]}; re-read the row")
        else:
            problems.append(f"cites `{i}`, which is not a hold this census "
                            f"knows (scripts/ruling_holds.py::ROW_HOLDS)")
    if direction not in ("R", "W", "unknown"):
        problems.append(f"direction {direction!r}: which half of the row holds "
                        f"its fire is a judgement, not a count -- split it or "
                        f"state it by hand")
        return None, problems
    if direction == "W" and WRITE_HOLD_ID not in ids:
        ids.append(WRITE_HOLD_ID)
    if not ids:
        return None, problems
    return min(ids, key=lambda i: (_PRECEDENCE[ROW_HOLDS[i].status],
                                   ids.index(i))), problems


# --------------------------------------------------------------------------
# Resolution against the corpus. IMPURE: never called by census_completion.
# --------------------------------------------------------------------------


def _register():
    """The rulings register, imported on first use -- see the docstring."""
    here = str(pathlib.Path(__file__).resolve().parent)
    if here not in sys.path:
        sys.path.insert(0, here)
    import build_rulings_index as bri

    return bri.REGISTER


def _flat(text: str) -> str:
    """Whitespace collapsed, so an anchor may span a wrapped line."""
    return " ".join(text.split())


def _anchor_problems(hold_id: str, hold: Hold, root: pathlib.Path) -> list[str]:
    doc = root / hold.document
    if not doc.is_file():
        return [f"{hold_id}: its document {hold.document} does not exist"]
    n = _flat(doc.read_text(encoding="utf-8",
                            errors="replace")).count(_flat(hold.anchor))
    if n != 1:
        return [f"{hold_id}: its words occur {n} time(s) in {hold.document}, "
                f"want exactly 1"]
    return []


def register_problems(root: pathlib.Path = ROOT, register=None,
                      holds: dict[str, Hold] | None = None) -> list[str]:
    """Every entry of ``holds`` resolved against the corpus. Empty is green.

    ``register`` and ``holds`` default to the shipped ones and exist as
    parameters so a control can hand in a damaged copy without touching either.
    """
    register = _register() if register is None else register
    holds = ROW_HOLDS if holds is None else holds
    by_id = {r.id: r for r in register}
    problems: list[str] = []
    for hold_id, hold in holds.items():
        if hold.status == "STANDING":
            ruling = by_id.get(hold_id)
            if ruling is None:
                problems.append(f"{hold_id}: STANDING here, and the rulings "
                                f"register has no ruling by that id")
                continue
            if ruling.status != "STANDING":
                problems.append(f"{hold_id}: the register now says "
                                f"{ruling.status!r}, not STANDING")
            kind, _sep, what = ruling.binds.partition(" -- ")
            if hold.binds == "surface" and (kind != "address family"
                                            or what != hold.surface):
                problems.append(f"{hold_id}: holds the surface {hold.surface} "
                                f"here, and the register's BINDS reads "
                                f"{ruling.binds!r}")
            if hold.binds == "write" and not what.startswith("every write"):
                problems.append(f"{hold_id}: binds every write here, and the "
                                f"register's BINDS reads {ruling.binds!r}")
        elif hold.status == "RELAYED":
            problems += _anchor_problems(hold_id, hold, root)
            if hold_id in by_id:
                problems.append(f"{hold_id}: RELAYED here, and the register "
                                f"now carries it -- mark it STANDING, so its "
                                f"BINDS is checked from now on")
        elif hold.status == "PENDING":
            problems += _anchor_problems(hold_id, hold, root)
            answered = sorted(r.id for r in register
                              if r.binds.partition(" -- ")[2].startswith(hold.surface))
            if answered:
                problems.append(f"{hold_id}: PENDING here, and the register now "
                                f"holds {answered} binding {hold.surface} -- the "
                                f"question looks answered; re-read every row "
                                f"that cites it")
        else:
            problems.append(f"{hold_id}: status {hold.status!r} is none of "
                            f"STANDING, RELAYED, PENDING")
        if hold.binds not in ("write", "surface"):
            problems.append(f"{hold_id}: binds {hold.binds!r} is neither write "
                            f"nor surface")
        if hold.binds == "surface" and not (hold.surface.startswith("/")
                                            and hold.surface.endswith("/")):
            problems.append(f"{hold_id}: surface {hold.surface!r} is not a "
                            f"/path/ prefix")
    for hold_id in LIFTED_ROW_HOLDS:
        if hold_id in holds:
            problems.append(f"{hold_id}: listed as lifted AND as a live hold")
    return problems


def main(argv: list[str] | None = None) -> int:
    del argv
    problems = register_problems()
    for hold_id, hold in ROW_HOLDS.items():
        where = hold.surface if hold.binds == "surface" else "every write"
        print(f"    {hold_id:32s} {hold.status:9s} {where}")
    for hold_id, why in LIFTED_ROW_HOLDS.items():
        print(f"    {hold_id:32s} LIFTED    {why}")
    if problems:
        print(f"RED: {len(problems)} problem(s):")
        for p in problems:
            print(f"  {p}")
        return 1
    print(f"GREEN: {len(ROW_HOLDS)} holds -- every STANDING one resolves in the "
          f"rulings register, every RELAYED and PENDING one to its own record")
    return 0


if __name__ == "__main__":
    sys.exit(main())
