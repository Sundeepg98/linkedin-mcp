"""The three outward classes built behind the grant, held to what they claim.

``linkedin_server/outward_classes.py`` records, per act the ruling
OUTWARD-CLASSES-BUILT-BEHIND-GRANTS built, whether it is BUILT, waits on a
CAPTURE, or is BLOCKED -- and keeps the three permanent refusals the ruling
retired, verbatim. Every claim it makes is a claim somebody will act on: a
lane builds from a NEEDS-CAPTURE record, an operator reads a BUILT one's
reversibility. So each is held here against the thing it describes:

* the surviving permanent refusals against ``writes.PERMANENTLY_FORBIDDEN``,
  BY NAME;
* the retired texts against their own digests, so "verbatim" stays true;
* BUILT against ``writes.PERFORMABLE`` and the sanctioned specs, in BOTH
  directions -- a record may not claim a build that is not there, and a
  build may not sit behind a record that still says it waits;
* every target kind against the closed list, none of which is a name;
* every census row a record names against the census, and its STATE against
  the record's status.

SHOWN FAILING: :func:`test_each_record_rule_is_shown_failing` plants one
defect per rule into a copy of a real record and asserts the checker names
it. A check that has only been seen passing certifies nothing.
"""
from __future__ import annotations

import dataclasses
import hashlib
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

from linkedin_server import outward_classes, writes  # noqa: E402

# NO MODULE-LEVEL UPPER-CASE CONSTANT BEYOND ``ROOT``, on the impact gate's
# rule: a test file that NAMES an upper-case constant another staged file
# defines is coupled to it.


def _record_problems(records, performable, sanctioned_actions) -> list[str]:
    """Every way a record can say something untrue. Pure; names the record."""
    problems: list[str] = []
    for key, rec in records.items():
        tag = f"{key}"
        if rec.action != key:
            problems.append(f"{tag}: keyed under a different action ({rec.action!r})")
        if rec.status not in outward_classes.OUTWARD_CLASS_STATUSES:
            problems.append(f"{tag}: status {rec.status!r} is off the list")
        if rec.outward_class not in outward_classes.OUTWARD_CLASS_NAMES:
            problems.append(f"{tag}: class {rec.outward_class!r} is not one of the three")
        if rec.target_kind not in outward_classes.OUTWARD_TARGET_KINDS:
            problems.append(f"{tag}: target kind {rec.target_kind!r} is off the closed list")
        if "name" in rec.target_kind:
            problems.append(f"{tag}: a target kind may never be a name")
        built = rec.action in performable and rec.action in sanctioned_actions
        if rec.status == "BUILT" and not built:
            problems.append(f"{tag}: says BUILT and writes cannot perform it")
        if rec.status != "BUILT" and rec.action in performable:
            problems.append(f"{tag}: writes can perform it and the record says {rec.status}")
        if rec.status == "NEEDS-CAPTURE":
            cap = rec.capture
            if cap is None:
                problems.append(f"{tag}: NEEDS-CAPTURE with no capture named")
            else:
                for part in ("page", "state", "element", "why_it_cannot_fire"):
                    if len(getattr(cap, part).strip()) < 30:
                        problems.append(f"{tag}: the capture's {part} is not stated")
        if rec.status == "BLOCKED" and len(rec.blocked_by.strip()) < 30:
            problems.append(f"{tag}: BLOCKED without saying by what")
        if rec.status == "BUILT" and rec.capture is not None:
            problems.append(f"{tag}: BUILT and still carries a capture it waits on")
        if len(rec.reversible_by.strip()) < 20:
            problems.append(f"{tag}: reversible_by is not stated")
        if len(rec.carried_facts.strip()) < 60:
            problems.append(f"{tag}: carried_facts is not stated")
        if rec.target_kind != "none" and "HE NAMES" not in rec.live_proof:
            problems.append(f"{tag}: a live proof must say what HE NAMES")
        try:
            rec.summary.encode("ascii")
            rec.carried_facts.encode("ascii")
        except UnicodeEncodeError:
            problems.append(f"{tag}: not ASCII")
    return problems


def _live_problems() -> list[str]:
    return _record_problems(
        outward_classes.OUTWARD_CLASS_SPECS,
        writes.PERFORMABLE,
        {spec.action for spec in writes.SANCTIONED_WRITES.values()},
    )


def test_the_surviving_permanent_refusals_are_the_ruling_s_six_by_name():
    assert sorted(writes.PERMANENTLY_FORBIDDEN) == sorted(
        outward_classes.SURVIVING_PERMANENT_REFUSALS
    )
    for retired in outward_classes.RETIRED_PERMANENT_REFUSALS:
        assert retired not in writes.PERMANENTLY_FORBIDDEN, retired
    # The two sets partition what the dict held at 1902fcb: nine entries.
    assert not set(outward_classes.SURVIVING_PERMANENT_REFUSALS) & set(
        outward_classes.RETIRED_PERMANENT_REFUSALS
    )
    assert len(outward_classes.SURVIVING_PERMANENT_REFUSALS) + len(
        outward_classes.RETIRED_PERMANENT_REFUSALS
    ) == 9


def test_the_retired_entries_are_kept_verbatim():
    """Byte-for-byte the text each last carried on master.

    A DIGEST, NOT A SECOND COPY, because a second copy in this file would be
    a pin of prose against prose. The digests were taken off the live dict
    before the entries left it, when the module's text compared equal to
    ``writes.PERMANENTLY_FORBIDDEN`` entry by entry. An edit to a retired
    entry is an edit to a record of what was ruled, and turns this red.

    ONE DIGEST MOVED, ONCE, AT THE MERGE THAT RETIRED THE ENTRY ON MASTER
    (2026-09-27). ``delete_or_withdraw_anything`` read ``79f0867297b22471`` at
    ``1902fcb``, where this lane took it; lane L5 had meanwhile rewritten it on
    master to count SIX specs, ``send_reply`` the sixth (``7d13af2``). The text
    the retirement removed from master is that one, so that is the one kept,
    compared equal to master's dict value before the swap.
    """
    want = {
        "repost_or_share": "7c1655c3ac2b725c",
        "endorse_or_recommend": "27dac326eead5ec9",
        "delete_or_withdraw_anything": "1cff9e239b05cb35",
    }
    got = {
        key: hashlib.sha256(text.encode("ascii")).hexdigest()[:16]
        for key, text in outward_classes.RETIRED_PERMANENT_REFUSALS.items()
    }
    assert got == want


def test_every_record_says_only_what_is_true():
    problems = _live_problems()
    assert problems == [], "\n".join(problems)


def test_each_class_the_ruling_names_has_a_record():
    classes = {r.outward_class for r in outward_classes.OUTWARD_CLASS_SPECS.values()}
    assert classes == set(outward_classes.OUTWARD_CLASS_NAMES)


def test_the_brief_s_acts_each_have_a_record():
    """The acts the lane was asked to build or record, by name."""
    for action in (
        "repost_item",
        "endorse_skill",
        "request_recommendation",
        "give_recommendation",
        "delete_own_post",
        "delete_own_comment",
        "withdraw_invitation",
        "withdraw_application",
        "withdraw_from_group",
    ):
        assert action in outward_classes.OUTWARD_CLASS_SPECS, action


@pytest.mark.parametrize(
    "plant, field, value, expect",
    [
        ("repost_item", "status", "DONE", "off the list"),
        ("repost_item", "outward_class", "anything", "not one of the three"),
        ("repost_item", "target_kind", "member_name", "never be a name"),
        ("repost_item", "status", "BUILT", "writes cannot perform it"),
        ("repost_item", "capture", None, "no capture named"),
        ("withdraw_application", "blocked_by", "", "BLOCKED without saying"),
        ("repost_item", "live_proof", "two loads", "what HE NAMES"),
        ("repost_item", "carried_facts", "", "carried_facts is not stated"),
        ("repost_item", "reversible_by", "", "reversible_by is not stated"),
    ],
)
def test_each_record_rule_is_shown_failing(plant, field, value, expect):
    records = dict(outward_classes.OUTWARD_CLASS_SPECS)
    records[plant] = dataclasses.replace(records[plant], **{field: value})
    problems = _record_problems(
        records,
        writes.PERFORMABLE,
        {spec.action for spec in writes.SANCTIONED_WRITES.values()},
    )
    assert any(plant in p and expect in p for p in problems), problems


def test_a_record_left_waiting_after_its_build_is_shown_failing():
    """The other direction: writes performs it, the record says it waits."""
    records = dict(outward_classes.OUTWARD_CLASS_SPECS)
    performable = set(writes.PERFORMABLE) | {"repost_item"}
    problems = _record_problems(
        records,
        performable,
        {spec.action for spec in writes.SANCTIONED_WRITES.values()} | {"repost_item"},
    )
    assert any("repost_item" in p and "writes can perform it" in p for p in problems)


def _census_state() -> dict[str, str]:
    import check_write_classes as cwc  # the shipped walk, imported

    return {k: st for k, (st, _d, _cap, _f) in cwc.census_index(ROOT).items()}


def test_every_row_a_record_names_is_a_census_row_in_the_state_it_implies():
    """BUILT means the row left GAP for a covered state; anything else means
    the row is still GAP. A record and the census disagreeing is a record
    nobody re-read when the census moved, or the reverse."""
    states = _census_state()
    problems = []
    for key, rec in outward_classes.OUTWARD_CLASS_SPECS.items():
        for row in rec.census_rows:
            state = states.get(row)
            if state is None:
                problems.append(f"{key}: names {row}, which is not a census row")
            elif rec.status == "BUILT" and state not in ("COVERED-UNFIRED", "COVERED-PROVEN"):
                problems.append(f"{key}: BUILT, and {row} reads {state}")
            elif rec.status != "BUILT" and state != "GAP":
                problems.append(f"{key}: {rec.status}, and {row} reads {state}")
    assert problems == [], "\n".join(problems)


def test_records_for_row_and_by_status_are_consistent():
    for status in outward_classes.OUTWARD_CLASS_STATUSES:
        for action in outward_classes.records_by_status(status):
            assert outward_classes.OUTWARD_CLASS_SPECS[action].status == status
    for action, rec in outward_classes.OUTWARD_CLASS_SPECS.items():
        for row in rec.census_rows:
            assert action in outward_classes.records_for_row(row)


def test_the_module_opens_nothing():
    """A record module with a page in it would be a reader nobody declared.

    Read off the SYNTAX TREE, not the text: the docstring says in words that
    no function here touches a browser, and a text scan would trip on that
    sentence. What is asserted is that nothing is imported beyond the
    standard library's dataclass and typing, and no call names a page verb.
    """
    import ast

    tree = ast.parse(pathlib.Path(outward_classes.__file__).read_text(encoding="ascii"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {alias.name for alias in node.names}
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            assert node.func.attr not in {
                "click", "goto", "evaluate", "fill", "press", "locator",
            }, node.func.attr
    assert imported <= {"__future__", "dataclasses", "typing"}, imported
