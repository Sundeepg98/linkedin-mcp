"""The holds table, and bucket 1's derivation from it, must be CHECKED -- and the checks must FAIL.

`scripts/ruling_holds.py` names the rulings, and the one open question, that
hold census rows. `scripts/census_completion.py` counts its bucket 1 -- the
COVERED-UNFIRED rows -- by the hold each row's own cell cites, or by its R/W
cell for a write. Until 2026-09-23 that bucket said a live session was the
entire remaining cost of all of them; `_audit/2026-09-23-bucket1-fires.md`
section 3 measured that it was the whole cost of none. Two ways this can rot,
and both are planted here:

  * **THE TABLE DRIFTS FROM THE REGISTER.** A ruling retired, re-scoped or
    re-worded in `build_rulings_index.REGISTER`, or the pending question
    answered, while rows go on citing it. `register_problems` is handed a
    DAMAGED COPY of the register or of the table -- never the real ones -- and
    must name the damage.
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

_MESSAGING = "DO-NOT-OPEN-MESSAGING"
_PENDING = "NOTIFICATIONS-UNREAD-SPEND"


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


def test_a_retired_standing_ruling_turns_it_red() -> None:
    problems = rh.register_problems(register=_register_with(**{_MESSAGING: None}))
    assert any(p.startswith(f"{_MESSAGING}: STANDING here, and the rulings "
                            f"register has no ruling by that id") for p in problems)


def test_a_rescoped_standing_ruling_turns_it_red() -> None:
    narrowed = dataclasses.replace(
        _ruling(_MESSAGING), binds="address family -- /messaging/thread/")
    problems = rh.register_problems(register=_register_with(**{_MESSAGING: narrowed}))
    assert any(p.startswith(f"{_MESSAGING}: holds the surface /messaging/ here")
               for p in problems), problems


def test_a_standing_ruling_no_longer_standing_turns_it_red() -> None:
    lifted = dataclasses.replace(_ruling(_MESSAGING), status="LIFTED")
    problems = rh.register_problems(register=_register_with(**{_MESSAGING: lifted}))
    assert f"{_MESSAGING}: the register now says 'LIFTED', not STANDING" in problems


def test_the_write_ruling_rebound_to_something_else_turns_it_red() -> None:
    rebound = dataclasses.replace(_ruling(rh.WRITE_RULING_ID),
                                  binds="capability class -- one write only")
    problems = rh.register_problems(
        register=_register_with(**{rh.WRITE_RULING_ID: rebound}))
    assert any(p.startswith(f"{rh.WRITE_RULING_ID}: binds every write here")
               for p in problems), problems


def test_an_answered_pending_question_turns_it_red() -> None:
    """A registered ruling binding the question's surface means it was answered."""
    answer = dataclasses.replace(_ruling(_MESSAGING), id="PLANTED-ANSWER",
                                 binds="address family -- /notifications/")
    problems = rh.register_problems(register=_register_with(**{"PLANTED-ANSWER": answer}))
    assert any(p.startswith(f"{_PENDING}: PENDING here, and the register now "
                            f"holds ['PLANTED-ANSWER']") for p in problems), problems


def test_a_pending_question_whose_words_moved_turns_it_red() -> None:
    holds = dict(rh.ROW_HOLDS)
    holds[_PENDING] = dataclasses.replace(holds[_PENDING],
                                          anchor="words nobody ever wrote")
    problems = rh.register_problems(holds=holds)
    assert any(p.startswith(f"{_PENDING}: the question's words occur 0 time(s)")
               for p in problems), problems


# -------------------------------------------------------------- hold_of's rules


@pytest.mark.parametrize("direction, text, want", [
    ("W", "no marker at all", rh.WRITE_RULING_ID),
    ("W", "**HELD BY `DO-NOT-OPEN-MESSAGING`**", rh.WRITE_RULING_ID),
    ("R", "**HELD BY `DO-NOT-OPEN-MESSAGING`**", _MESSAGING),
    ("R", "**HELD BY `NOTIFICATIONS-UNREAD-SPEND`**", _PENDING),
    ("unknown", "**HELD BY `NO-IRREVERSIBLE-WRITE-IS-FIRED`**", rh.WRITE_RULING_ID),
    ("unknown", "**HELD BY `DO-NOT-OPEN-MESSAGING`** and **HELD BY "
                "`NO-IRREVERSIBLE-WRITE-IS-FIRED`**", rh.WRITE_RULING_ID),
    ("R", "**HELD BY `NOTIFICATIONS-UNREAD-SPEND`** **HELD BY "
          "`DO-NOT-OPEN-MESSAGING`**", _MESSAGING),
    ("R", "the row mentions `DO-NOT-OPEN-MESSAGING` without the marker", None),
    ("unknown", "nothing cited", None),
], ids=["W-needs-no-marker", "W-outranks-a-surface", "R-cites-a-standing",
        "R-cites-a-pending", "jobs-row-cites-the-write-ruling",
        "the-write-ruling-outranks", "standing-outranks-pending",
        "a-mention-is-not-a-marker", "no-citation-is-no-ruling"])
def test_hold_of_reads_the_census_and_nothing_else(direction, text, want) -> None:
    hold, problems = rh.hold_of(direction, text)
    assert (hold, problems) == (want, [])


@pytest.mark.parametrize("direction, text, needle", [
    ("R", "**HELD BY `NO-IRREVERSIBLE-WRITE-IS-FIRED`**", "a READ row cites"),
    ("R", "**HELD BY `NO-SUCH-RULING`**", "not a hold this census knows"),
    ("R+W", "**HELD BY `DO-NOT-OPEN-MESSAGING`**", "which half of the row"),
    ("ambiguous", "", "which half of the row"),
], ids=["a-read-row-citing-the-write-ruling", "an-unknown-id", "an-R+W-row",
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
    for key in ("b1_write_ruling", "b1_other_standing", "b1_pending",
                "b1_no_ruling"):
        assert figures[key] == cc.PINNED[key], key
    assert sum(figures[k] for k in ("b1_write_ruling", "b1_other_standing",
                                    "b1_pending", "b1_no_ruling")) == unfired
    text = "\n".join(out)
    assert "a session is the entire remaining cost" not in text.lower()
    assert f"CHECK: {figures['b1_write_ruling']} + " in text


def test_the_pinned_rows_are_exactly_the_unfired_rows() -> None:
    """The row pin covers the population once each -- no row twice, none left out."""
    pinned = [row for members in cc.PINNED_B1_ROWS.values() for row in members]
    assert len(pinned) == len(set(pinned)) == cc.PINNED["unfired"]


# ------------------------------------------------------- bucket 1, shown failing


def _first(holds, want):
    for row, hold in sorted(holds.items()):
        if hold == want:
            return row
    raise AssertionError(f"no COVERED-UNFIRED row is held by {want!r} today; "
                         f"this control has nothing to plant on")


def _key(row):
    letter, _sep, rid = row.partition(" ")
    return letter, rid


def test_a_removed_marker_moves_the_row_and_names_it() -> None:
    holds, _ = _holds()
    victim = _first(holds, _MESSAGING)
    texts = _texts()
    texts[_key(victim)] = texts[_key(victim)].replace("HELD BY", "held, once, by")
    planted, problems = _holds(texts=texts)
    assert not problems
    assert (f"{victim}: pinned as held by {_MESSAGING}, now held by "
            f"{cc.NO_RULING}") in cc.bucket1_moves(planted)


def test_a_swap_that_moves_no_count_is_still_named() -> None:
    """THE PLANT A COUNT PIN CANNOT SEE: two rows exchange holds, totals unchanged."""
    holds, _ = _holds()
    a, b = _first(holds, _MESSAGING), _first(holds, _PENDING)
    texts = _texts()
    texts[_key(a)] = texts[_key(a)].replace(_MESSAGING, _PENDING)
    texts[_key(b)] = texts[_key(b)].replace(_PENDING, _MESSAGING)
    planted, problems = _holds(texts=texts)
    assert not problems
    assert sorted(planted.values(), key=str) == sorted(holds.values(), key=str), \
        "the swap changed a count; it no longer tests what it claims to"
    moves = cc.bucket1_moves(planted)
    assert f"{a}: pinned as held by {_MESSAGING}, now held by {_PENDING}" in moves
    assert f"{b}: pinned as held by {_PENDING}, now held by {_MESSAGING}" in moves


def test_a_write_row_whose_direction_flips_is_named() -> None:
    rows = list(cc.walk())
    victim = next(f"{l} {r}" for l, r, st, d in rows
                  if st == "COVERED-UNFIRED" and d == "W")
    flipped = [(l, r, st, "R" if f"{l} {r}" == victim else d)
               for l, r, st, d in rows]
    planted, problems = _holds(flipped)
    assert not problems
    assert (f"{victim}: pinned as held by {rh.WRITE_RULING_ID}, now held by "
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


def test_an_unreadable_hold_withholds_the_whole_split() -> None:
    """Withheld, never guessed: no `b1_` figure at all, so every pin has nothing to check."""
    rows = list(cc.walk())
    holds, _ = _holds(rows)
    victim = _first(holds, _PENDING)
    texts = _texts()
    texts[_key(victim)] += " **HELD BY `NO-SUCH-RULING`**"
    planted, problems = _holds(rows, texts=texts)
    assert planted is None
    assert any(p.startswith(f"{victim}: cites `NO-SUCH-RULING`") for p in problems)


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
