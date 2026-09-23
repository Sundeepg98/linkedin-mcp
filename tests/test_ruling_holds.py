"""The holds table, and bucket 1's derivation from it, must be CHECKED -- and the checks must FAIL.

`scripts/ruling_holds.py` names what holds census rows: a ruling in force, a
ruling the operator has made that the register does not carry yet, or a
question still open. `scripts/census_completion.py` counts its bucket 1 -- the
COVERED-UNFIRED rows -- by the hold each row's own cell cites, or by its R/W
cell for a write. Until 2026-09-23 that bucket said a live session was the
entire remaining cost of all of them; `_audit/2026-09-23-bucket1-fires.md`
section 3 measured that it was the whole cost of none. And the same day the
rulings themselves moved: at 18:15 the operator lifted the messaging ruling and
the read-only rule (his ruling (b), relayed), which this table absorbed in one
edit. Three ways this can rot, all planted here:

  * **THE TABLE DRIFTS FROM THE REGISTER.** A ruling retired, re-scoped or
    re-worded in `build_rulings_index.REGISTER`, the pending question answered,
    or the relayed ruling registered while the table still calls it relayed.
    `register_problems` is handed a DAMAGED COPY of the register or of the
    table -- never the real ones -- and must name the damage.
  * **A ROW STILL CITES A LIFTED RULING.** The citation is history; counting it
    would publish a hold that no longer exists. It must withhold the split.
  * **A ROW MOVES AND A COUNT CANNOT SAY WHICH.** The plant that matters most
    is the SWAP: two rows exchange holds, every count stays where it was, and
    only the row-by-row control can see it. Every census plant goes into a copy
    of the cells handed to `bucket1_holds(texts=...)`; no census file is
    written.

**GREEN ALONE IS AMBIGUOUS** -- a table checked against nothing, or a
derivation that cannot see a marker, is green too. So the real tree is asserted
green AND every control is shown convicting a plant.
"""
from __future__ import annotations

import dataclasses
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import build_rulings_index as bri  # noqa: E402
import census_completion as cc  # noqa: E402
import ruling_holds as rh  # noqa: E402

# NO MODULE-LEVEL CONSTANT BEYOND THE CONVENTIONAL ``ROOT``: the impact gate
# couples every test file that names an upper-case constant this file defines.

_TARGET = rh.WRITE_HOLD_ID
_PENDING = "NOTIFICATIONS-UNREAD-SPEND"
_LIFTED = "DO-NOT-OPEN-MESSAGING"
#: A registered STANDING ruling whose BINDS is a path, and which is NOT lifted.
#: Its polarity does not matter here: only register resolution is under test.
_STANDING = "ONE-NAMED-SETTINGS-PAGE-AT-A-TIME"


def _standing_hold(hold_id=_STANDING, surface="/mypreferences/d/"):
    """A STANDING surface hold, handed in as a parameter.

    No STANDING hold is in use today, so the STANDING branch of
    `register_problems` is exercised by handing one in. It is a real registered
    STANDING ruling, so it resolves green before any damage. (The FIRST draft
    handed in the messaging ruling and went red on its own control: that
    ruling is on the lifted list, and "lifted AND live" is a problem this file
    wants reported -- which is the last test below.)
    """
    return {hold_id: rh.Hold(status="STANDING", binds="surface",
                             surface=surface)}


def _register_with(**changes):
    """A copy of the register with one ruling replaced, removed, or added."""
    out = []
    for ruling in bri.REGISTER:
        if ruling.id in changes:
            new = changes[ruling.id]
            if new is not None:
                out.append(new)
        else:
            out.append(ruling)
    for rid, new in changes.items():
        if new is not None and all(r.id != rid for r in bri.REGISTER):
            out.append(new)
    return tuple(out)


def _ruling(rid):
    return next(r for r in bri.REGISTER if r.id == rid)


def _texts():
    return {(letter, rid): " | ".join(c)
            for letter, rid, st, _d, c in cc.walk_cells()
            if st == "COVERED-UNFIRED"}


def _holds(rows=None, texts=None):
    rows = list(cc.walk()) if rows is None else rows
    holds, problems = cc.bucket1_holds(rows, texts=texts)
    return holds, problems


# ---------------------------------------------------- the table vs the register


def test_the_real_table_resolves_against_the_real_register() -> None:
    assert rh.register_problems() == []


def test_every_hold_holds_at_least_one_row_today() -> None:
    """A hold that holds nothing is a vocabulary entry nobody can check."""
    holds, problems = _holds()
    assert not problems
    assert set(rh.ROW_HOLDS) <= set(holds.values())


def test_a_standing_hold_resolves_before_it_is_damaged() -> None:
    """The control for the three damage tests below: green on the real register."""
    assert rh.register_problems(holds=_standing_hold()) == []


def test_a_retired_standing_ruling_turns_it_red() -> None:
    problems = rh.register_problems(holds=_standing_hold(),
                                    register=_register_with(**{_STANDING: None}))
    assert any(p.startswith(f"{_STANDING}: STANDING here, and the rulings "
                            f"register has no ruling by that id") for p in problems)


def test_a_rescoped_standing_ruling_turns_it_red() -> None:
    narrowed = dataclasses.replace(
        _ruling(_STANDING), binds="address family -- /mypreferences/d/one/")
    problems = rh.register_problems(holds=_standing_hold(),
                                    register=_register_with(**{_STANDING: narrowed}))
    assert any(p.startswith(f"{_STANDING}: holds the surface /mypreferences/d/ "
                            f"here") for p in problems), problems


def test_a_standing_ruling_no_longer_standing_turns_it_red() -> None:
    lifted = dataclasses.replace(_ruling(_STANDING), status="LIFTED")
    problems = rh.register_problems(holds=_standing_hold(),
                                    register=_register_with(**{_STANDING: lifted}))
    assert f"{_STANDING}: the register now says 'LIFTED', not STANDING" in problems


def test_a_relayed_ruling_the_register_now_carries_turns_it_red() -> None:
    """The register caught up: the entry must become STANDING, BINDS checked."""
    caught_up = dataclasses.replace(_ruling(_LIFTED), id=_TARGET,
                                    binds="capability class -- every write")
    problems = rh.register_problems(register=_register_with(**{_TARGET: caught_up}))
    assert any(p.startswith(f"{_TARGET}: RELAYED here, and the register now "
                            f"carries it") for p in problems), problems


def test_a_relayed_ruling_whose_record_moved_turns_it_red() -> None:
    holds = dict(rh.ROW_HOLDS)
    holds[_TARGET] = dataclasses.replace(holds[_TARGET],
                                         anchor="words nobody ever wrote")
    problems = rh.register_problems(holds=holds)
    assert any(p.startswith(f"{_TARGET}: its words occur 0 time(s)")
               for p in problems), problems


def test_an_answered_pending_question_turns_it_red() -> None:
    """A registered ruling binding the question's surface means it was answered."""
    answer = dataclasses.replace(_ruling(_LIFTED), id="PLANTED-ANSWER",
                                 binds="address family -- /notifications/")
    problems = rh.register_problems(register=_register_with(**{"PLANTED-ANSWER": answer}))
    assert any(p.startswith(f"{_PENDING}: PENDING here, and the register now "
                            f"holds ['PLANTED-ANSWER']") for p in problems), problems


def test_a_pending_question_whose_words_moved_turns_it_red() -> None:
    holds = dict(rh.ROW_HOLDS)
    holds[_PENDING] = dataclasses.replace(holds[_PENDING],
                                          anchor="words nobody ever wrote")
    problems = rh.register_problems(holds=holds)
    assert any(p.startswith(f"{_PENDING}: its words occur 0 time(s)")
               for p in problems), problems


def test_a_ruling_both_lifted_and_live_turns_it_red() -> None:
    """Putting a lifted ruling back into force without taking it off the list."""
    holds = dict(rh.ROW_HOLDS)
    holds.update(_standing_hold(_LIFTED, "/messaging/"))
    problems = rh.register_problems(holds=holds)
    assert f"{_LIFTED}: listed as lifted AND as a live hold" in problems


# -------------------------------------------------------------- hold_of's rules


@pytest.mark.parametrize("direction, text, want", [
    ("W", "no marker at all", _TARGET),
    ("W", f"**HELD BY `{_PENDING}`**", _PENDING),
    ("R", f"**HELD BY `{_TARGET}`**", _TARGET),
    ("R", f"**HELD BY `{_PENDING}`**", _PENDING),
    ("unknown", f"**HELD BY `{_TARGET}`**", _TARGET),
    ("R", f"**HELD BY `{_TARGET}`** **HELD BY `{_PENDING}`**", _PENDING),
    ("R", f"the row mentions `{_TARGET}` without the marker", None),
    ("R", f"this row was held by `{_LIFTED}` until 18:15", None),
    ("unknown", "nothing cited", None),
], ids=["W-needs-no-marker", "an-open-question-outranks-the-write-hold",
        "R-cites-the-relayed-condition", "R-cites-a-pending",
        "jobs-row-cites-the-write-hold", "pending-outranks-relayed",
        "a-mention-is-not-a-marker", "lowercase-history-is-not-a-marker",
        "no-citation-is-no-ruling"])
def test_hold_of_reads_the_census_and_nothing_else(direction, text, want) -> None:
    hold, problems = rh.hold_of(direction, text)
    assert (hold, problems) == (want, [])


def test_a_standing_hold_outranks_everything(monkeypatch) -> None:
    monkeypatch.setitem(rh.ROW_HOLDS, "PLANTED-STANDING",
                        rh.Hold(status="STANDING", binds="surface",
                                surface="/planted/"))
    hold, problems = rh.hold_of(
        "W", f"**HELD BY `{_PENDING}`** **HELD BY `PLANTED-STANDING`**")
    assert (hold, problems) == ("PLANTED-STANDING", [])


@pytest.mark.parametrize("direction, text, needle", [
    ("R", f"**HELD BY `{_LIFTED}`**", "that ruling is lifted"),
    ("R", "**HELD BY `NO-SUCH-RULING`**", "not a hold this census knows"),
    ("R+W", f"**HELD BY `{_TARGET}`**", "which half of the row"),
    ("ambiguous", "", "which half of the row"),
], ids=["a-lifted-ruling-cited-as-a-hold", "an-unknown-id", "an-R+W-row",
        "an-ambiguous-row"])
def test_hold_of_refuses_what_it_cannot_read(direction, text, needle) -> None:
    _hold, problems = rh.hold_of(direction, text)
    assert any(needle in p for p in problems), problems


# ------------------------------------------------ bucket 1 on the real census


def test_bucket_one_is_derived_and_sits_on_its_pins() -> None:
    rows = list(cc.walk())
    holds, problems = _holds(rows)
    assert not problems, problems
    assert cc.bucket1_moves(holds) == []
    unfired = sum(1 for _l, _r, st, _d in rows if st == "COVERED-UNFIRED")
    assert unfired == len(holds) == cc.PINNED["unfired"]
    out: list[str] = []
    figures = cc.report(rows, out)
    keys = ("b1_standing", "b1_named_target", "b1_pending", "b1_no_ruling")
    for key in keys:
        assert figures[key] == cc.PINNED[key], key
    assert sum(figures[k] for k in keys) == unfired
    text = "\n".join(out)
    assert "a session is the entire remaining cost" not in text.lower()
    assert f"CHECK: {figures['b1_standing']} + " in text


def test_no_census_cell_still_cites_a_lifted_ruling_as_a_hold() -> None:
    """The lift reached every cell: no COVERED-UNFIRED row cites one."""
    for key, text in _texts().items():
        stale = [c for c in rh.cited(text) if c in rh.LIFTED_ROW_HOLDS]
        assert not stale, (key, stale)


def test_the_pinned_rows_are_exactly_the_unfired_rows() -> None:
    """The row pin covers the population once each -- no row twice, none left out."""
    pinned = [row for members in cc.PINNED_B1_ROWS.values() for row in members]
    assert len(pinned) == len(set(pinned)) == cc.PINNED["unfired"]


# ------------------------------------------------------- bucket 1, shown failing


def _first_cited(holds, want):
    """The first row held by ``want`` through its CITATION, not its R/W cell."""
    direction = {f"{l} {r}": d for l, r, _st, d in cc.walk()}
    for row, hold in sorted(holds.items()):
        if hold == want and direction.get(row) != "W":
            return row
    raise AssertionError(f"no COVERED-UNFIRED row cites {want!r} today; this "
                         f"control has nothing to plant on")


def _key(row):
    letter, _sep, rid = row.partition(" ")
    return letter, rid


def test_a_removed_marker_moves_the_row_and_names_it() -> None:
    holds, _ = _holds()
    victim = _first_cited(holds, _TARGET)
    texts = _texts()
    texts[_key(victim)] = texts[_key(victim)].replace("HELD BY", "held, once, by")
    planted, problems = _holds(texts=texts)
    assert not problems
    assert (f"{victim}: pinned as held by {_TARGET}, now held by "
            f"{cc.NO_RULING}") in cc.bucket1_moves(planted)


def test_a_swap_that_moves_no_count_is_still_named() -> None:
    """THE PLANT A COUNT PIN CANNOT SEE: two rows exchange holds, totals unchanged."""
    holds, _ = _holds()
    a, b = _first_cited(holds, _TARGET), _first_cited(holds, _PENDING)
    texts = _texts()
    texts[_key(a)] = texts[_key(a)].replace(_TARGET, _PENDING)
    texts[_key(b)] = texts[_key(b)].replace(_PENDING, _TARGET)
    planted, problems = _holds(texts=texts)
    assert not problems
    assert sorted(planted.values(), key=str) == sorted(holds.values(), key=str), \
        "the swap changed a count; it no longer tests what it claims to"
    moves = cc.bucket1_moves(planted)
    assert f"{a}: pinned as held by {_TARGET}, now held by {_PENDING}" in moves
    assert f"{b}: pinned as held by {_PENDING}, now held by {_TARGET}" in moves


def test_a_write_row_whose_direction_flips_is_named() -> None:
    rows = list(cc.walk())
    victim = next(f"{l} {r}" for l, r, st, d in rows
                  if st == "COVERED-UNFIRED" and d == "W")
    flipped = [(l, r, st, "R" if f"{l} {r}" == victim else d)
               for l, r, st, d in rows]
    planted, problems = _holds(flipped)
    assert not problems
    assert (f"{victim}: pinned as held by {_TARGET}, now held by "
            f"{cc.NO_RULING}") in cc.bucket1_moves(planted)


def test_a_row_that_leaves_the_state_is_named() -> None:
    rows = list(cc.walk())
    victim = next(f"{l} {r}" for l, r, st, _d in rows if st == "COVERED-UNFIRED")
    banked = [(l, r, "COVERED-PROVEN" if f"{l} {r}" == victim else st, d)
              for l, r, st, d in rows]
    planted, problems = _holds(banked)
    assert not problems
    assert any(m.startswith(f"{victim}: LEFT COVERED-UNFIRED")
               for m in cc.bucket1_moves(planted))


@pytest.mark.parametrize("planted_id, needle", [
    ("NO-SUCH-RULING", "cites `NO-SUCH-RULING`, which is not a hold"),
    (_LIFTED, f"cites `{_LIFTED}` as its hold, and that ruling is lifted"),
], ids=["an-unknown-id", "a-lifted-ruling"])
def test_an_unreadable_hold_withholds_the_whole_split(planted_id, needle) -> None:
    """Withheld, never guessed: a stale or unknown citation yields no split."""
    rows = list(cc.walk())
    holds, _ = _holds(rows)
    victim = _first_cited(holds, _PENDING)
    texts = _texts()
    texts[_key(victim)] += f" **HELD BY `{planted_id}`**"
    planted, problems = _holds(rows, texts=texts)
    assert planted is None
    assert any(p.startswith(f"{victim}: {needle}") for p in problems), problems


def test_the_report_withholds_every_b1_figure_when_a_hold_is_unreadable(
        monkeypatch) -> None:
    """What `--check` reads: an unreadable hold yields NO `b1_` figure, not a zero."""
    monkeypatch.setattr(cc, "bucket1_holds",
                        lambda rows, texts=None: (None, ["X 0: planted"]))
    out: list[str] = []
    figures = cc.report(list(cc.walk()), out)
    assert "BUCKET 1 SPLIT WITHHELD" in "\n".join(out)
    assert not any(k.startswith("b1_") for k in figures)
    assert {k for k in cc.PINNED if k.startswith("b1_")}, \
        "no b1_ pin exists, so withholding would have nothing to report"
