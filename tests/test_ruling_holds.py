"""The holds table, and bucket 1's derivation from it, must be CHECKED -- and the checks must FAIL.

`scripts/ruling_holds.py` names what holds census rows: a ruling in force, a
ruling relayed but not yet registered, or a question still open -- and keeps
the rulings and questions that USED to hold rows, each with what the register
says about it now. `scripts/census_completion.py` counts its bucket 1 -- the
COVERED-UNFIRED rows -- by the hold each row's own cell cites, or by its R/W
cell for a write.

The table moved three times on 2026-09-23 (first build; the operator's ruling
(b) relayed at 18:15; the register catching up that evening), and every move
was an edit to this table and to the cells that cite it. So the tests below
hold the MECHANISM, not the day: where a plant needs a kind of hold the real
table no longer has -- a pending question, a hold on a page -- the test
installs one of its own. Three ways this can rot, all planted:

  * **THE TABLE DRIFTS FROM THE REGISTER.** A hold's ruling retired, re-scoped
    or no longer standing; a relayed ruling registered, or a pending question
    answered, while this table still says otherwise; a LIFTED ruling put back
    into force. `register_problems` is handed a DAMAGED COPY -- of the
    register, the holds or the lifted list, never the real ones -- and must
    name the damage. Two of these are the real events of the merge with
    master 53ba1b6, replayed against the real register.
  * **A ROW STILL CITES A LIFTED RULING.** The citation is history; counting
    it would publish a hold that no longer exists. It must withhold the split.
  * **A ROW MOVES AND A COUNT CANNOT SAY WHICH.** The plant that matters most
    is the SWAP: two rows exchange holds, every count stays where it was, and
    only the row-by-row control can see it. Every census plant goes into a
    copy of the cells handed to `bucket1_holds(texts=...)`; no census file is
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
_LIFTED = "DO-NOT-OPEN-MESSAGING"
_AMENDED = "NO-IRREVERSIBLE-WRITE-IS-FIRED"
_ANSWERED = "NOTIFICATIONS-UNREAD-SPEND"
#: A registered STANDING ruling whose BINDS is a path and which is not lifted.
#: Its polarity does not matter here: only register resolution is under test.
_STANDING = "ONE-NAMED-SETTINGS-PAGE-AT-A-TIME"


def _standing_hold(hold_id=_STANDING, surface="/mypreferences/d/"):
    """A STANDING surface hold, handed in as a parameter.

    It is a real registered STANDING ruling, so it resolves green before any
    damage. (A first draft handed in the messaging ruling and went red on its
    own control: that ruling is on the lifted list, and "lifted AND live" is a
    problem this file wants reported -- the test for it is below.)
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


def test_the_write_hold_rebound_to_one_write_turns_it_red() -> None:
    """The register spells it "every outward write"; "one write only" is not every write."""
    rebound = dataclasses.replace(_ruling(_TARGET), binds="live proofs -- one write only")
    problems = rh.register_problems(register=_register_with(**{_TARGET: rebound}))
    assert any(p.startswith(f"{_TARGET}: binds every write here") for p in problems), \
        problems


def test_the_merge_replayed_a_relayed_hold_the_register_carries_turns_it_red() -> None:
    """THE REAL EVENT: at the merge with master this entry was RELAYED here and registered there."""
    relayed = {_TARGET: rh.Hold(
        status="RELAYED", binds="write",
        document="_audit/2026-09-23-census-cleanup.md",
        anchor="the linkedin MCP may connect, message, apply, post AND OPEN "
               "MESSAGING on his account")}
    problems = rh.register_problems(holds=relayed)
    assert any(p.startswith(f"{_TARGET}: RELAYED here, and the register now "
                            f"carries it") for p in problems), problems


def test_a_relayed_ruling_whose_record_moved_turns_it_red() -> None:
    relayed = {"PLANTED-RELAYED": rh.Hold(
        status="RELAYED", binds="write",
        document="_audit/2026-09-23-census-cleanup.md",
        anchor="words nobody ever wrote")}
    problems = rh.register_problems(holds=relayed)
    assert any(p.startswith("PLANTED-RELAYED: its words occur 0 time(s)")
               for p in problems), problems


def test_the_merge_replayed_a_pending_question_the_register_answered_turns_it_red() -> None:
    """THE REAL EVENT: the notifications question, pending here, answered in the register."""
    pending = {_ANSWERED: rh.Hold(
        status="PENDING", binds="surface", surface="/notifications/",
        document="_audit/2026-09-23-bucket1-fires.md",
        anchor="may one `linkedin_notifications` call spend his unread "
               "notification state?")}
    problems = rh.register_problems(holds=pending)
    assert any(p.startswith(f"{_ANSWERED}: PENDING here, and the register now "
                            f"holds ['{_ANSWERED}'] binding /notifications/")
               for p in problems), problems


def test_a_pending_question_whose_words_moved_turns_it_red() -> None:
    pending = {"PLANTED-QUESTION": rh.Hold(
        status="PENDING", binds="surface", surface="/planted-question/",
        document="_audit/2026-09-23-bucket1-fires.md",
        anchor="words nobody ever wrote")}
    problems = rh.register_problems(holds=pending)
    assert any(p.startswith("PLANTED-QUESTION: its words occur 0 time(s)")
               for p in problems), problems


def test_a_ruling_both_lifted_and_live_turns_it_red() -> None:
    """Putting a lifted ruling back into force without taking it off the list."""
    holds = dict(rh.ROW_HOLDS)
    holds.update(_standing_hold(_LIFTED, "/messaging/"))
    problems = rh.register_problems(holds=holds)
    assert f"{_LIFTED}: listed as lifted AND as a live hold" in problems


def test_a_lifted_ruling_the_register_puts_back_in_force_turns_it_red() -> None:
    """The lifted list is read against the register too: SUPERSEDED must still say so."""
    reinstated = dataclasses.replace(_ruling(_LIFTED), status="STANDING")
    problems = rh.register_problems(register=_register_with(**{_LIFTED: reinstated}))
    assert any(p.startswith(f"{_LIFTED}: lifted here on the register's word "
                            f"'SUPERSEDED', and the register now says 'STANDING'")
               for p in problems), problems


def test_a_lifted_ruling_gone_from_the_register_turns_it_red() -> None:
    problems = rh.register_problems(register=_register_with(**{_AMENDED: None}))
    assert f"{_AMENDED}: lifted here, and the rulings register has no ruling " \
           f"by that id" in problems


# -------------------------------------------------------------- hold_of's rules


@pytest.fixture
def planted_holds(monkeypatch):
    """One hold of each status on a page, so the rules are tested whatever today's table holds."""
    for hold_id, status in (("PLANTED-STANDING", "STANDING"),
                            ("PLANTED-QUESTION", "PENDING"),
                            ("PLANTED-RELAYED", "RELAYED")):
        monkeypatch.setitem(rh.ROW_HOLDS, hold_id, rh.Hold(
            status=status, binds="surface", surface=f"/{hold_id.lower()}/"))


@pytest.mark.parametrize("direction, text, want", [
    ("W", "no marker at all", _TARGET),
    ("W", "**HELD BY `PLANTED-QUESTION`**", _TARGET),
    ("R", f"**HELD BY `{_TARGET}`**", _TARGET),
    ("R", "**HELD BY `PLANTED-QUESTION`**", "PLANTED-QUESTION"),
    ("unknown", f"**HELD BY `{_TARGET}`**", _TARGET),
    ("R", "**HELD BY `PLANTED-RELAYED`** **HELD BY `PLANTED-QUESTION`**",
     "PLANTED-QUESTION"),
    ("R", "**HELD BY `PLANTED-QUESTION`** **HELD BY `PLANTED-STANDING`**",
     "PLANTED-STANDING"),
    ("R", f"the row mentions `{_TARGET}` without the marker", None),
    ("R", f"this row was held by `{_LIFTED}` until 18:15", None),
    ("unknown", "nothing cited", None),
], ids=["W-needs-no-marker", "a-standing-write-hold-outranks-a-question",
        "R-cites-the-target-hold", "R-cites-a-pending", "jobs-row-cites-the-target-hold",
        "pending-outranks-relayed", "standing-outranks-pending",
        "a-mention-is-not-a-marker", "lowercase-history-is-not-a-marker",
        "no-citation-is-no-ruling"])
def test_hold_of_reads_the_census_and_nothing_else(
        planted_holds, direction, text, want) -> None:
    hold, problems = rh.hold_of(direction, text)
    assert (hold, problems) == (want, [])


@pytest.mark.parametrize("direction, text, needle", [
    ("R", f"**HELD BY `{_LIFTED}`**", "that ruling is lifted"),
    ("R", f"**HELD BY `{_ANSWERED}`**", "that ruling is lifted"),
    ("R", "**HELD BY `NO-SUCH-RULING`**", "not a hold this census knows"),
    ("R+W", f"**HELD BY `{_TARGET}`**", "which half of the row"),
    ("ambiguous", "", "which half of the row"),
], ids=["a-lifted-ruling-cited-as-a-hold", "an-answered-question-cited-as-a-hold",
        "an-unknown-id", "an-R+W-row", "an-ambiguous-row"])
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
    keys = ("b1_standing", "b1_relayed", "b1_pending", "b1_no_ruling")
    for key in keys:
        assert figures[key] == cc.PINNED[key], key
    assert sum(figures[k] for k in keys) == unfired
    text = "\n".join(out)
    assert "a session is the entire remaining cost" not in text.lower()
    assert f"CHECK: {figures['b1_standing']} + " in text


def test_no_census_cell_still_cites_a_lifted_ruling_as_a_hold() -> None:
    """The lifts reached every cell: no COVERED-UNFIRED row cites one."""
    for key, text in _texts().items():
        stale = [c for c in rh.cited(text) if c in rh.LIFTED_ROW_HOLDS]
        assert not stale, (key, stale)


def test_the_pinned_rows_are_exactly_the_unfired_rows() -> None:
    """The row pin covers the population once each -- no row twice, none left out."""
    pinned = [row for members in cc.PINNED_B1_ROWS.values() for row in members]
    assert len(pinned) == len(set(pinned)) == cc.PINNED["unfired"]


# ------------------------------------------------------- bucket 1, shown failing


def _direction():
    return {f"{l} {r}": d for l, r, _st, d in cc.walk()}


def _first_cited(holds, want):
    """The first row held by ``want`` through its CITATION, not its R/W cell."""
    direction = _direction()
    for row, hold in sorted(holds.items()):
        if hold == want and direction.get(row) != "W":
            return row
    raise AssertionError(f"no COVERED-UNFIRED row cites {want!r} today; this "
                         f"control has nothing to plant on")


def _first_free(holds, want_direction):
    """The first row held by NO ruling with the given direction."""
    direction = _direction()
    for row, hold in sorted(holds.items()):
        if hold is None and direction.get(row) == want_direction:
            return row
    raise AssertionError(f"no COVERED-UNFIRED row with direction "
                         f"{want_direction!r} is held by no ruling today")


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
    """THE PLANT A COUNT PIN CANNOT SEE: two rows exchange holds, totals unchanged.

    A row cited under the target hold loses its marker, and a row held by no
    ruling -- a jobs row, so its direction cannot supply a hold -- gains one.
    """
    holds, _ = _holds()
    a = _first_cited(holds, _TARGET)
    b = _first_free(holds, "unknown")
    texts = _texts()
    texts[_key(a)] = texts[_key(a)].replace("HELD BY", "held, once, by")
    texts[_key(b)] += f" **HELD BY `{_TARGET}`**"
    planted, problems = _holds(texts=texts)
    assert not problems
    assert sorted(planted.values(), key=str) == sorted(holds.values(), key=str), \
        "the swap changed a count; it no longer tests what it claims to"
    moves = cc.bucket1_moves(planted)
    assert f"{a}: pinned as held by {_TARGET}, now held by {cc.NO_RULING}" in moves
    assert f"{b}: pinned as held by {cc.NO_RULING}, now held by {_TARGET}" in moves


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
    (_ANSWERED, f"cites `{_ANSWERED}` as its hold, and that ruling is lifted"),
], ids=["an-unknown-id", "a-lifted-ruling", "an-answered-question"])
def test_an_unreadable_hold_withholds_the_whole_split(planted_id, needle) -> None:
    """Withheld, never guessed: a stale or unknown citation yields no split."""
    rows = list(cc.walk())
    holds, _ = _holds(rows)
    victim = _first_free(holds, "R")
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
