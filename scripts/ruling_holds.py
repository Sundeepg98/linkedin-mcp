"""The rulings, and the open questions, that HOLD census rows -- one table, read by two buckets.

THE DEFECT THIS EXISTS FOR, measured 2026-09-23, twice in one day and in two
different instruments.

  * ``scripts/census_completion.py`` described its bucket 1, the
    COVERED-UNFIRED rows, as *"BLOCKED ON A LIVE BROWSER SESSION ... no ruling,
    no design, no build"*. ``_audit/2026-09-23-bucket1-fires.md`` section 3
    classified the 21 rows left and a session was the whole cost for none of
    them: 15 are writes, 2 open messaging, 2 would spend his unread
    notifications, 2 need a press or a reader change.
  * ``_audit/_census/read-addresses.tsv`` classed ``M M49`` as blocked on
    nothing, because the shipped boundary admits ``/messaging/thread/<id>/``.
    The boundary was asked; the rulings were not. ``DO-NOT-OPEN-MESSAGING``
    forbids opening messaging at all.

**ONE MISTAKE, TWICE: A COUNT OF WHAT THE CODE PERMITS, READ AS A COUNT OF WHAT
MAY BE DONE.** Both instruments asked a mechanism (the census state, the read
boundary) a question only a ruling answers. This module is the one place that
names the rulings and questions that hold rows, so both buckets ask it rather
than each re-deciding.

WHAT A ROW OF ``ROW_HOLDS`` SAYS
--------------------------------
``status``   ``STANDING`` -- a ruling in ``_audit/RULINGS.md``, made, and in
             force. ``PENDING`` -- a question put to the operator and NOT yet
             answered; it holds a row exactly as firmly until he answers, and
             it is never to be read as a ruling.
``binds``    ``write`` -- the hold binds an ACT, every write this server can
             fire, whatever page it is on. ``surface`` -- the hold binds a PAGE:
             any address under ``surface`` is held, whatever the act.
``surface``  a path prefix, for ``binds == "surface"``.

**THE STANDING SURFACE IS NOT TYPED HERE, IT IS CHECKED HERE.**
:func:`register_problems` re-reads every STANDING entry out of the rulings
register (``scripts/build_rulings_index.py::REGISTER``) and fails when the id
is gone, is no longer STANDING, or its BINDS no longer names the surface
written below. So an edit to the register reaches both buckets as a red, never
as a silent disagreement.

**A PENDING ENTRY IS RE-RESOLVED AGAINST THE DOCUMENT THAT PUT THE QUESTION**,
its ``anchor`` required EXACTLY ONCE, and it FAILS THE MOMENT A REGISTERED
RULING BINDS THE SAME SURFACE: the question has then been answered, and every
row citing it must be re-read against the answer rather than left citing a
question nobody is asking any more.

HOW A ROW CITES ITS HOLD
------------------------
A census cell, or a note in ``read-addresses.tsv``, cites what holds its row
with the marker::

    **HELD BY `<ID>`**

``HELD_BY_MARKER`` reads the id and nothing else. It is a MARKER rather than a
mention on purpose -- ``_audit/RULINGS.md`` records that cells cite rulings for
many reasons, and a parser that took every mentioned id as a hold would count
a row's ARGUMENT as its state. The same discipline as ``CORRECTS:``.

A write-direction row needs NO marker: its census R/W cell is the stronger
statement, and ``NO-IRREVERSIBLE-WRITE-IS-FIRED`` binds every write. The marker
is for rows whose hold the direction cell cannot express -- a read held by a
ruling on its page, and a write in ``jobs.md``, which has no R/W column
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
    """What holds a row: a ruling made (STANDING) or a question open (PENDING)."""

    status: str
    binds: str
    surface: str = ""
    #: PENDING only: the document that put the question, and its exact words.
    document: str = ""
    anchor: str = ""
    #: One line a reader of the census output needs; printed beside the count.
    gist: str = ""


#: The id of the ruling every write is held by. Named once because two rules
#: turn on it: a W row is held by it with no marker, and a READ row citing it
#: is a contradiction.
WRITE_RULING_ID = "NO-IRREVERSIBLE-WRITE-IS-FIRED"

#: Every hold a census row may cite, keyed by the id it is cited by.
ROW_HOLDS: dict[str, Hold] = {
    WRITE_RULING_ID: Hold(
        status="STANDING",
        binds="write",
        gist="no irreversible write is fired at a real target without him",
    ),
    "DO-NOT-OPEN-MESSAGING": Hold(
        status="STANDING",
        binds="surface",
        surface="/messaging/",
        gist="opening messaging lands in a thread LinkedIn chooses and can "
             "mark a real person's message read",
    ),
    #: NOT A RULING. The question put to him on 2026-09-23 after the SECOND
    #: wave reached the two notification rows and declined them on the same
    #: ground. Loading the page clears his unread badge and it does not come
    #: back, so a fire spends his state; the id is the question's, and it
    #: stops being cited the day he answers either way.
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

#: ``**HELD BY `<ID>`**`` -- the bold is optional, the backticked id is not.
HELD_BY_MARKER = re.compile(r"HELD BY `([A-Z0-9][A-Z0-9-]*[A-Z0-9])`")

#: The order holds are counted in when a row cites more than one: a write is
#: held by the write ruling whatever else also holds it, a ruling made outranks
#: a question open, and among equals the first cited wins.
_PRECEDENCE = {"write": 0, "STANDING": 1, "PENDING": 2}


def cited(text: str) -> list[str]:
    """Every id ``text`` cites with the marker, first-cited first, once each."""
    seen: list[str] = []
    for hit in HELD_BY_MARKER.findall(text):
        if hit not in seen:
            seen.append(hit)
    return seen


def _rank(hold_id: str) -> int:
    hold = ROW_HOLDS[hold_id]
    return _PRECEDENCE["write"] if hold.binds == "write" else _PRECEDENCE[hold.status]


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

      * ``W``: held by the write ruling. The R/W cell says so; no marker is
        needed and another cited hold does not displace it.
      * ``R``: held by what its cell cites. Citing the WRITE ruling is a
        contradiction and is reported, never counted.
      * ``unknown`` (``jobs.md`` has no R/W column): held by what its cell
        cites, and citing the write ruling is how such a row says it is a write.
      * ``R+W`` and ``ambiguous`` are REFUSED: which half holds the fire is a
        judgement for a person, and a counter that picked one would publish it.
      * an id that is not in ``ROW_HOLDS`` is reported, never guessed at.

    No citation and not a write is ``None`` -- held by NO ruling. That is a
    finding about the rulings, not a default: the row's own cell says what
    remains.
    """
    ids = cited(text)
    problems = [f"cites `{i}`, which is not a hold this census knows "
                f"(scripts/ruling_holds.py::ROW_HOLDS)"
                for i in ids if i not in ROW_HOLDS]
    ids = [i for i in ids if i in ROW_HOLDS]
    if direction == "W":
        return WRITE_RULING_ID, problems
    if direction not in ("R", "unknown"):
        problems.append(f"direction {direction!r}: which half of the row holds "
                        f"its fire is a judgement, not a count -- split it or "
                        f"state it by hand")
        return None, problems
    if direction == "R" and WRITE_RULING_ID in ids:
        problems.append(f"a READ row cites `{WRITE_RULING_ID}`, which binds "
                        f"writes only")
        return None, problems
    if not ids:
        return None, problems
    return min(ids, key=lambda i: (_rank(i), ids.index(i))), problems


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
        elif hold.status == "PENDING":
            doc = root / hold.document
            if not doc.is_file():
                problems.append(f"{hold_id}: the question's document "
                                f"{hold.document} does not exist")
            else:
                n = _flat(doc.read_text(encoding="utf-8",
                                        errors="replace")).count(_flat(hold.anchor))
                if n != 1:
                    problems.append(f"{hold_id}: the question's words occur {n} "
                                    f"time(s) in {hold.document}, want exactly 1")
            answered = sorted(r.id for r in register
                              if r.binds.partition(" -- ")[2].startswith(hold.surface))
            if answered:
                problems.append(f"{hold_id}: PENDING here, and the register now "
                                f"holds {answered} binding {hold.surface} -- the "
                                f"question looks answered; re-read every row "
                                f"that cites it")
        else:
            problems.append(f"{hold_id}: status {hold.status!r} is neither "
                            f"STANDING nor PENDING")
        if hold.binds not in ("write", "surface"):
            problems.append(f"{hold_id}: binds {hold.binds!r} is neither write "
                            f"nor surface")
        if hold.binds == "surface" and not (hold.surface.startswith("/")
                                            and hold.surface.endswith("/")):
            problems.append(f"{hold_id}: surface {hold.surface!r} is not a "
                            f"/path/ prefix")
    return problems


def main(argv: list[str] | None = None) -> int:
    del argv
    problems = register_problems()
    for hold_id, hold in ROW_HOLDS.items():
        where = hold.surface if hold.binds == "surface" else "every write"
        print(f"    {hold_id:32s} {hold.status:9s} {where}")
    if problems:
        print(f"RED: {len(problems)} problem(s):")
        for p in problems:
            print(f"  {p}")
        return 1
    print(f"GREEN: {len(ROW_HOLDS)} holds, every STANDING one resolves in the "
          f"rulings register and every PENDING one to its own question")
    return 0


if __name__ == "__main__":
    sys.exit(main())
