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
message, apply, post and open messaging on his account. It LIFTS
``DO-NOT-OPEN-MESSAGING`` and the read-only rule. The orchestrator relayed it
to the wave that built this file, and this table carried it as RELAYED until
master registered it that evening (``WRITE-CLASS-B`` and
``OPERATOR-NAMES-THE-TARGET``, recorded in
``_audit/2026-09-23-rulings-write-class-and-delegated-calls.md``). The same
registration answered the open notifications question and put his own
inbox reads under (b) with no per-fire go-ahead -- both the orchestrator's
calls under the operator's delegation, and overridable by him. So today ONE
hold is left: every write fires only at a target he names. Both buckets moved
each time by editing this table and the cells that cite it -- nothing else.
And the day the register caught up, :func:`register_problems` said so on its
own: RELAYED here and registered there, PENDING here and answered there.

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
names each ruling, or answered question, that held rows and no longer does. A
cell or a note still citing one as a hold is reported by :func:`hold_of`,
never silently counted. And each entry records WHAT THE REGISTER SAYS about it
(SUPERSEDED, AMENDED, or -- for the answered question, now a permission --
STANDING); :func:`register_problems` checks that too, so a register that puts
a lifted ruling back into force reaches this table as a red.

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


#: The id of the hold every write is held by: the operator's own ruling of
#: 18:15 on 2026-09-23, STANDING in the register since master 53ba1b6. Named
#: once because a rule turns on it: a W row is held by it with no marker.
WRITE_HOLD_ID = "OPERATOR-NAMES-THE-TARGET"

#: Every hold a census row may cite TODAY, keyed by the id it is cited by.
#:
#: ONE ENTRY, AND THE REASON IS THE REGISTER, NOT A SIMPLIFICATION. After the
#: rulings of 2026-09-23 nothing holds a PAGE any more: messaging may be
#: opened (WRITE-CLASS-B), his own inbox reads need no per-fire go-ahead
#: (OWN-INBOX-READS-COVERED-BY-B), and loading /notifications/ is permitted
#: (NOTIFICATIONS-UNREAD-SPEND, now a registered permission). What still holds
#: census rows is the condition on every outward write.
#:
#: **ONE CLASSIFICATION IS THIS TABLE'S, NOT THE REGISTER'S.** The register
#: binds this ruling to "every outward write"; this table holds every census
#: W row with it, as the bucket-1 audit classed the writes. The six
#: profile-field edits (P A8, A11, A13, A17, A19, A21) are the rows where
#: "outward" could be argued: they are his own fields, reversible, and visible
#: to everyone who opens his profile. `OUTWARD-ACTS-NEED-THE-OPERATOR` routes
#: to him only acts toward other people or irreversible ones. Whether a
#: profile field is such an act is the orchestrator's to call, and
#: `_audit/2026-09-23-census-cleanup.md` puts it there; until then the rows
#: stay held, which is the direction that cannot fire anything by mistake.
ROW_HOLDS: dict[str, Hold] = {
    WRITE_HOLD_ID: Hold(
        status="STANDING",
        binds="write",
        gist="a live proof only at a target the operator names",
    ),
}


@dataclasses.dataclass(frozen=True)
class Lifted:
    """A ruling, or an answered question, that held census rows and no longer does."""

    #: What the register must say about this id TODAY. Checked by
    #: :func:`register_problems`, so a register that puts the ruling back into
    #: force reaches this table as a red rather than as a quiet disagreement.
    register_status: str
    #: One line: when, by what, and what a row that cited it should cite now.
    why: str


#: Rulings and questions that held census rows and NO LONGER DO. A row still
#: citing one of these as a hold is reported, never counted: the citation is
#: history, and the row has to be re-read.
LIFTED_ROW_HOLDS: dict[str, Lifted] = {
    "DO-NOT-OPEN-MESSAGING": Lifted(
        register_status="SUPERSEDED",
        why="replaced at 18:15 on 2026-09-23 by WRITE-CLASS-B, the operator's "
            "ruling (b): messaging may be opened"),
    "NO-IRREVERSIBLE-WRITE-IS-FIRED": Lifted(
        register_status="AMENDED",
        why="amended at 18:15 on 2026-09-23 by WRITE-CLASS-B: a write may "
            "fire, at a target the operator names -- the hold a write row "
            "cites is OPERATOR-NAMES-THE-TARGET"),
    #: The question the bucket-1 wave put on 2026-09-23 (may a fire spend his
    #: unread badge?). Answered PERMITTED the same day as the orchestrator's
    #: delegated call -- the operator routed "his own notification state" to
    #: the orchestrator at 18:13 -- and registered under the question's own
    #: id, so the register now reads it as a STANDING permission.
    "NOTIFICATIONS-UNREAD-SPEND": Lifted(
        register_status="STANDING",
        why="answered 2026-09-23: loading /notifications/ is permitted (the "
            "orchestrator's delegated call, overridable by the operator); the "
            "id is now a registered permission, not a hold"),
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
                            f"lifted -- {LIFTED_ROW_HOLDS[i].why}; re-read the "
                            f"row")
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


#: A write hold's register BINDS must still name EVERY write of its class:
#: "every write ...", or "every <kind> write" -- the register's own spelling
#: for this ruling is "every outward write". "one write only" does not match.
_EVERY_WRITE = re.compile(r"every\b(?:\s+\w+)?\s+writes?\b")


def register_problems(root: pathlib.Path = ROOT, register=None,
                      holds: dict[str, Hold] | None = None,
                      lifted: dict[str, Lifted] | None = None) -> list[str]:
    """Every entry of ``holds`` and ``lifted`` resolved against the corpus.

    Empty is green. ``register``, ``holds`` and ``lifted`` default to the
    shipped ones and exist as parameters so a control can hand in a damaged
    copy without touching any of them.
    """
    register = _register() if register is None else register
    holds = ROW_HOLDS if holds is None else holds
    lifted = LIFTED_ROW_HOLDS if lifted is None else lifted
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
            if hold.binds == "write" and not _EVERY_WRITE.match(what):
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
    for hold_id, entry in lifted.items():
        if hold_id in holds:
            problems.append(f"{hold_id}: listed as lifted AND as a live hold")
        ruling = by_id.get(hold_id)
        if ruling is None:
            problems.append(f"{hold_id}: lifted here, and the rulings register "
                            f"has no ruling by that id")
        elif ruling.status != entry.register_status:
            problems.append(f"{hold_id}: lifted here on the register's word "
                            f"{entry.register_status!r}, and the register now "
                            f"says {ruling.status!r} -- re-read every row it "
                            f"once held")
    return problems


def main(argv: list[str] | None = None) -> int:
    del argv
    problems = register_problems()
    for hold_id, hold in ROW_HOLDS.items():
        where = hold.surface if hold.binds == "surface" else "every write"
        print(f"    {hold_id:32s} {hold.status:9s} {where}")
    for hold_id, entry in LIFTED_ROW_HOLDS.items():
        print(f"    {hold_id:32s} LIFTED    register says "
              f"{entry.register_status}: {entry.why}")
    if problems:
        print(f"RED: {len(problems)} problem(s):")
        for p in problems:
            print(f"  {p}")
        return 1
    print(f"GREEN: {len(ROW_HOLDS)} hold(s) and {len(LIFTED_ROW_HOLDS)} lifted "
          f"-- every STANDING hold resolves in the rulings register, every "
          f"RELAYED and PENDING one to its own record, and every lifted one to "
          f"the status the register gives it")
    return 0


if __name__ == "__main__":
    sys.exit(main())
