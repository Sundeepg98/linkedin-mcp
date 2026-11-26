"""The multi-step Easy Apply walker's guards (lane apply-26, phase A).

SCAFFOLDING, AND LABELLED SO. Every step reading in sections 1-6 is written by
hand: no LinkedIn markup of any multi-step step exists anywhere (the record,
``_audit/2026-11-25-apply.md`` section 1, says where it looked). These
readings exercise the walker's LOGIC and measure nothing about LinkedIn; they
move no census row. Where a test needs the walker to believe a shape is
measured it uses :data:`SCAFFOLD`, a registry in which every shape is marked
measured on no evidence -- the label is in each entry's evidence -- and the
production registry ``apply_walk.SHAPES`` is used everywhere the point is what
happens TODAY.

Section 7 is the exception and is NOT scaffolding: ``read_draft_state`` runs
over ``tests/fixtures/jobs_tracker_row.html``, a skeleton of his live Draft
tab, in a local headless Chromium.

Every guard was shown failing before it was trusted; the mutations and their
failures are in the record, section 2.6.
"""

from __future__ import annotations

import dataclasses
import datetime
import json
import re
import subprocess
from pathlib import Path

import pytest

from linkedin_server import apply_answers, apply_walk, dom, people_data, writes
from linkedin_server.apply_walk import (
    LIMIT,
    MEASURED,
    NEEDS_OPERATOR,
    PLAN,
    REFUSED,
    SHAPES,
    ControlReading,
    FieldReading,
    StepReading,
)

REPO = Path(__file__).resolve().parents[1]
FIXTURES = REPO / "tests" / "fixtures"

#: SCAFFOLDING: every shape marked measured, on no evidence.
SCAFFOLD = {
    key: dataclasses.replace(
        shape, status=MEASURED, evidence="SCAFFOLDING: marked measured with no capture"
    )
    for key, shape in SHAPES.items()
}

# ---------------------------------------------------------------------------
# Hand-written readings (SCAFFOLDING)
# ---------------------------------------------------------------------------

NEXT = ControlReading(name="Continue to next step")
REVIEW = ControlReading(name="Review your application")
DISMISS = ControlReading(name="Dismiss")
SUBMIT = ControlReading(name="Submit application", hooks=(dom.APPLY_SUBMIT_HOOK,))

Q_YEARS = "How many years of experience do you have with Widgets?"
Q_AUTH = "Are you legally authorized to work in Elsewhere?"
Q_NOTICE = "What is your notice period in days?"
Q_LANG = "What is your level of proficiency in Esperanto?"
Q_RESUME = "Choose a resume"


def contact_step() -> StepReading:
    return StepReading(
        heading="Contact info",
        fields=(
            FieldReading(tag="input", input_type="email", question="Email address",
                         value="the-address-as-prefilled", required=True),
            FieldReading(tag="input", input_type="tel", question="Mobile phone number",
                         value="", required=True),
        ),
        controls=(DISMISS, NEXT),
        dialogs=1,
        scan_complete=True,
    )


def resume_step() -> StepReading:
    return StepReading(
        heading="Resume",
        fields=(
            FieldReading(tag="fieldset", input_type="radio", question=Q_RESUME,
                         options=("Resume-A.pdf", "Resume-B.pdf"), required=True),
            FieldReading(tag="input", input_type="file", question="Upload resume",
                         required=False),
        ),
        controls=(DISMISS, NEXT),
        dialogs=1,
        scan_complete=True,
    )


def screening_step() -> StepReading:
    return StepReading(
        heading="Additional questions",
        fields=(
            FieldReading(tag="input", input_type="text", inputmode="numeric",
                         question=Q_YEARS, required=True),
            FieldReading(tag="fieldset", input_type="radio", question=Q_AUTH,
                         options=("Yes", "No"), required=True),
            FieldReading(tag="input", input_type="text", question=Q_NOTICE, required=True),
            # The placeholder is DRAWN as an option and reported as no value:
            # the reading contract's rule for a select (see FieldReading.value).
            FieldReading(tag="select", question=Q_LANG,
                         options=("Select an option", "Elementary", "Professional", "Native"),
                         value="", required=True),
        ),
        controls=(DISMISS, REVIEW),
        dialogs=1,
        scan_complete=True,
    )


def review_step(*controls: ControlReading) -> StepReading:
    return StepReading(
        heading="Review your application",
        fields=(),
        controls=controls or (DISMISS, SUBMIT),
        dialogs=1,
        scan_complete=True,
    )


def walk() -> list[StepReading]:
    return [contact_step(), resume_step(), screening_step(), review_step()]


def bank_line(entry_id, kind, question, confirmed, *, cls="other", platform="any",
              draft="", expires_at="") -> dict:
    """One SYNTHETIC bank entry: one class, one wording on one platform."""
    return {
        "id": entry_id, "family": cls, "input_kind": kind,
        "platforms": {platform: {"questions": [question], "options": [], "native_type": ""}},
        "draft": {"value": draft, "per_platform": {}, "source": "synthetic"},
        "confirmed": {"value": confirmed, "per_platform": {},
                      "confirmed_at": "2026-11-01" if confirmed else "",
                      "expires_at": expires_at, "auto": ""},
        "notes": "",
    }


def bank_text(*entries: dict) -> apply_answers.Bank:
    return apply_answers.parse_bank(
        json.dumps({"schema": apply_answers.SCHEMA_ID, "entries": list(entries)}),
        today=datetime.date(2026, 11, 25))


def bank_of(*rows: tuple[str, str, str, str]) -> apply_answers.Bank:
    """(id, input_kind, question, CONFIRMED) rows -> a parsed SYNTHETIC bank."""
    return bank_text(*(bank_line(*r) for r in rows))


def full_bank() -> apply_answers.Bank:
    return bank_of(
        ("phone", "text", "Mobile phone number", "5550100"),
        ("resume", "radio", Q_RESUME, "Resume-B.pdf"),
        ("yoe-widgets", "numeric", Q_YEARS, "4"),
        ("auth-elsewhere", "radio", Q_AUTH, "Yes"),
        ("notice", "text", Q_NOTICE, "30"),
        ("lang-esperanto", "select", Q_LANG, "Professional"),
    )


# ---------------------------------------------------------------------------
# 1. The registry says what is measured, and nothing more
# ---------------------------------------------------------------------------


def test_today_one_shape_is_measured_and_it_is_the_draft_tab():
    measured = {key for key, shape in SHAPES.items() if shape.status == MEASURED}
    assert measured == {"verify.draft_tab"}, (
        f"a shape moved to MEASURED: {sorted(measured)}. A shape is measured "
        "only by a committed skeleton of a live capture -- move it with its "
        "evidence, and change this pin in the same commit."
    )


def test_a_measured_shape_cites_a_tracked_skeleton():
    tracked = set(
        subprocess.run(["git", "-C", str(REPO), "ls-files", "tests/fixtures"],
                       capture_output=True, text=True, check=True).stdout.split()
    )
    for key, shape in SHAPES.items():
        if shape.status == MEASURED:
            # A SENTENCE citing the skeleton, never the bare path: the impact
            # gate reads a package literal naming a tracked data file as a read.
            assert any(ch.isspace() for ch in shape.evidence), (key, shape.evidence)
            cited = re.findall(r"tests/fixtures/[A-Za-z0-9_./-]+\.html", shape.evidence)
            assert cited and all(path in tracked for path in cited), (key, shape.evidence)


def test_every_proposed_shape_names_what_will_measure_it():
    for key, shape in SHAPES.items():
        assert shape.status in apply_walk.STATUSES, key
        if shape.status != MEASURED:
            assert "C-J68-" in shape.evidence or "J 82" in shape.evidence, (key, shape.evidence)


def test_every_step_field_and_control_kind_has_a_shape():
    for kind in apply_walk.STEP_KINDS:
        assert f"step.{kind}" in SHAPES
    for kind in apply_walk.FIELD_KINDS:
        assert f"field.{kind}" in SHAPES
    for kind in apply_walk.CONTROL_KINDS:
        assert f"control.{kind}" in SHAPES


# ---------------------------------------------------------------------------
# 2. Recognition is by structure, and today it refuses
# ---------------------------------------------------------------------------


def test_the_first_step_of_every_multi_step_flow_is_refused_today():
    for step in walk():
        result = apply_walk.plan_walk([step], full_bank())
        assert result["verdict"] == REFUSED, result
        assert result["refused_condition"] == "unmeasured_step", result
        assert "C-J68-1" in result["why"], result["why"]
        saw = result["saw"]
        assert saw["looks_like"] in apply_walk.STEP_KINDS
        assert saw["dialogs"] == 1 and saw["scan_complete"] is True
        assert [a["act"] for a in result["inverse"]] == ["dismiss", "discard", "verify_no_draft"]


@pytest.mark.parametrize("registry", [SHAPES, SCAFFOLD], ids=["today", "scaffold"])
def test_an_unknown_field_is_refused_naming_its_structure(registry):
    step = dataclasses.replace(
        screening_step(),
        fields=(FieldReading(tag="div", role="slider", question=Q_YEARS),),
    )
    result = apply_walk.plan_step(step, full_bank(), index=0, final=False, registry=registry)
    assert result["verdict"] == REFUSED
    assert result["refused_condition"] == "unrecognised_field"
    assert result["saw"]["fields_unrecognised"] == [
        {"tag": "div", "input_type": "", "role": "other"}
    ]


def test_a_refusal_never_carries_an_attribute_value_outside_its_vocabulary():
    plant = "PLANTED<attr>value"
    step = dataclasses.replace(
        screening_step(),
        fields=(FieldReading(tag=plant, input_type=plant, role=plant, question="Q?"),),
    )
    result = apply_walk.plan_step(step, full_bank(), index=0, final=False, registry=SCAFFOLD)
    assert result["refused_condition"] == "unrecognised_field"
    assert plant not in json.dumps(result)
    assert result["saw"]["fields_unrecognised"] == [
        {"tag": "other", "input_type": "other", "role": "other"}
    ]


def test_the_heading_never_decides_the_kind():
    looks_like_review = dataclasses.replace(screening_step(), heading="Review your application")
    assert apply_walk.classify_step(looks_like_review) == "screening"
    titled_contact = review_step()
    titled_contact = dataclasses.replace(titled_contact, heading="Contact info")
    assert apply_walk.classify_step(titled_contact) == "review"


def test_the_field_kinds_are_read_from_structure():
    cases = {
        "text": FieldReading(tag="input", input_type="text"),
        "numeric": FieldReading(tag="input", input_type="text", inputmode="numeric"),
        "select": FieldReading(tag="select"),
        "radio": FieldReading(tag="fieldset", input_type="radio"),
        "checkbox": FieldReading(tag="input", input_type="checkbox"),
        "typeahead": FieldReading(tag="input", role="combobox", aria_autocomplete="list"),
        "file": FieldReading(tag="input", input_type="file"),
    }
    for kind, reading in cases.items():
        assert apply_walk.classify_field(reading) == kind, kind
    assert apply_walk.classify_field(FieldReading(tag="input", role="combobox")) is None
    assert apply_walk.classify_field(FieldReading(tag="input", input_type="date")) is None


def test_an_unscanned_step_is_refused_not_read_as_empty():
    step = StepReading(fields=(), controls=(DISMISS, SUBMIT), dialogs=1)
    assert step.scan_complete is False, "the reading contract's default no longer refuses"
    result = apply_walk.plan_step(step, full_bank(), index=0, final=True, registry=SCAFFOLD)
    assert result["refused_condition"] == "scan_incomplete", result


@pytest.mark.parametrize("dialogs", [0, 2])
def test_a_page_with_other_than_one_dialog_is_refused(dialogs):
    step = dataclasses.replace(contact_step(), dialogs=dialogs)
    result = apply_walk.plan_step(step, full_bank(), index=0, final=False, registry=SCAFFOLD)
    assert result["refused_condition"] == "dialog_count", result


def test_a_step_no_shape_fits_is_refused():
    """No field, no submit, no notice: not review, not a limit, not a form."""
    bare = StepReading(controls=(DISMISS,), dialogs=1, scan_complete=True)
    result = apply_walk.plan_step(bare, full_bank(), index=0, final=False, registry=SCAFFOLD)
    assert result["refused_condition"] == "unrecognised_step", result
    assert result["saw"]["looks_like"] is None


def _measured_except(*shape_ids: str) -> dict:
    """SCAFFOLDING: every shape measured but the ones named."""
    return {
        key: (SHAPES[key] if key in shape_ids else shape)
        for key, shape in SCAFFOLD.items()
    }


def test_a_measured_step_with_an_unmeasured_control_is_refused():
    registry = _measured_except("control.dismiss")
    result = apply_walk.plan_step(contact_step(), full_bank(), index=0, final=False,
                                  registry=registry)
    assert result["refused_condition"] == "unmeasured_control", result
    assert "dismiss" in result["why"]


def test_a_measured_step_with_an_unmeasured_field_is_refused():
    registry = _measured_except("field.numeric")
    result = apply_walk.plan_step(screening_step(), full_bank(), index=2, final=False,
                                  registry=registry)
    assert result["refused_condition"] == "unmeasured_field", result
    assert "numeric" in result["why"]


def test_a_field_with_no_question_is_refused_not_asked_about():
    unlabelled = StepReading(
        fields=(FieldReading(tag="input", input_type="text", question="  "),),
        controls=(DISMISS, NEXT), dialogs=1, scan_complete=True,
    )
    result = apply_walk.plan_step(unlabelled, full_bank(), index=0, final=False, registry=SCAFFOLD)
    assert result["verdict"] == REFUSED and result["refused_condition"] == "unlabelled_field", result


# ---------------------------------------------------------------------------
# 3. His bank, and NEEDS-OPERATOR (SCAFFOLD registry)
# ---------------------------------------------------------------------------


def _plan(steps, bank):
    return apply_walk.plan_walk(steps, bank, registry=SCAFFOLD)


def test_a_question_not_in_the_bank_stops_the_walk_quoting_it():
    partial = bank_of(("phone", "text", "Mobile phone number", "5550100"),
                      ("resume", "radio", Q_RESUME, "Resume-B.pdf"))
    result = _plan(walk(), partial)
    assert result["verdict"] == NEEDS_OPERATOR, result
    assert result["step"] == 2 and result["steps_planned_before_this"] == 2
    asked = {item["question"]: item for item in result["needs_operator"]}
    assert set(asked) == {Q_YEARS, Q_AUTH, Q_NOTICE, Q_LANG}, sorted(asked)
    assert asked[Q_YEARS]["input_kind"] == "numeric"
    assert asked[Q_AUTH]["input_kind"] == "radio" and asked[Q_AUTH]["options"] == ["Yes", "No"]
    for item in asked.values():
        assert item[people_data.UNTRUSTED_KEY] == people_data.UNTRUSTED_NOTE
    assert "inverse" in result


def test_a_draft_value_never_reaches_a_field():
    drafts_only = bank_text(
        bank_line("r0", "text", "Mobile phone number", "", draft="5550100"),
        bank_line("r1", "radio", Q_RESUME, "", draft="Resume-B.pdf"),
    )
    result = _plan(walk(), drafts_only)
    assert result["verdict"] == NEEDS_OPERATOR, result
    assert result["step"] == 0
    assert [item["question"] for item in result["needs_operator"]] == ["Mobile phone number"]


def test_the_page_never_supplies_an_answer():
    only_option = StepReading(
        fields=(FieldReading(tag="fieldset", input_type="radio",
                             question="Do you agree?", options=("Yes",), required=True),),
        controls=(DISMISS, NEXT), dialogs=1, scan_complete=True,
    )
    result = apply_walk.plan_step(only_option, full_bank(), index=0, final=False, registry=SCAFFOLD)
    assert result["verdict"] == NEEDS_OPERATOR, result
    assert result["needs_operator"][0]["needs"] == "not_in_bank"


def test_a_linkedin_prefill_is_kept_and_named_as_such():
    result = apply_walk.plan_step(contact_step(), full_bank(), index=0, final=False, registry=SCAFFOLD)
    assert result["verdict"] == PLAN, result
    email, phone = result["fields"]
    assert email["action"] == "keep_prefill" and email["source"] == "linkedin_prefill"
    assert phone["action"] == "fill" and phone["bank_entry"] == "phone"


def test_a_prefill_that_disagrees_with_his_confirmed_answer_stops_the_walk():
    bank = bank_of(("email", "text", "Email address", "the-address-he-confirmed"),
                   ("phone", "text", "Mobile phone number", "5550100"))
    result = apply_walk.plan_step(contact_step(), bank, index=0, final=False, registry=SCAFFOLD)
    assert result["verdict"] == NEEDS_OPERATOR, result
    assert result["needs_operator"][0]["needs"] == "prefill_differs_from_confirmed"
    assert "the-address-he-confirmed" not in json.dumps(result["needs_operator"])


def test_a_confirmed_answer_that_is_not_an_option_stops_the_walk():
    bank = bank_of(("phone", "text", "Mobile phone number", "5550100"),
                   ("resume", "radio", Q_RESUME, "Resume-C.pdf"))
    result = apply_walk.plan_step(resume_step(), bank, index=1, final=False, registry=SCAFFOLD)
    assert result["verdict"] == NEEDS_OPERATOR, result
    assert result["needs_operator"][0]["needs"] == "confirmed_answer_is_not_an_option_drawn"


def test_a_checked_box_nobody_confirmed_stops_the_walk():
    """A box can be an act -- a consent, a follow -- so LinkedIn's tick is not his."""
    boxed = StepReading(
        fields=(FieldReading(tag="input", input_type="checkbox",
                             question="Follow the company", checked=True, required=False),),
        controls=(DISMISS, NEXT), dialogs=1, scan_complete=True,
    )
    result = apply_walk.plan_step(boxed, full_bank(), index=0, final=False, registry=SCAFFOLD)
    assert result["verdict"] == NEEDS_OPERATOR, result
    assert result["needs_operator"][0]["needs"] == "checkbox_needs_his_answer"
    confirmed = bank_of(("follow", "checkbox", "Follow the company", "unchecked"))
    result = apply_walk.plan_step(boxed, confirmed, index=0, final=False, registry=SCAFFOLD)
    assert result["verdict"] == PLAN and result["fields"][0]["action"] == "check"
    assert result["fields"][0]["value"] == "unchecked"


def test_an_optional_empty_field_is_left_empty_and_an_unstated_one_is_not():
    def one(required):
        return StepReading(
            fields=(FieldReading(tag="input", input_type="text", question="Website",
                                 required=required),),
            controls=(DISMISS, NEXT), dialogs=1, scan_complete=True,
        )
    optional = apply_walk.plan_step(one(False), full_bank(), index=0, final=False, registry=SCAFFOLD)
    assert optional["verdict"] == PLAN and optional["fields"][0]["action"] == "leave_empty"
    unstated = apply_walk.plan_step(one(None), full_bank(), index=0, final=False, registry=SCAFFOLD)
    assert unstated["verdict"] == NEEDS_OPERATOR, unstated


def test_a_file_input_is_never_filled():
    required_file = StepReading(
        fields=(FieldReading(tag="input", input_type="file", question="Upload resume",
                             required=True),),
        controls=(DISMISS, NEXT), dialogs=1, scan_complete=True,
    )
    result = apply_walk.plan_step(required_file, full_bank(), index=0, final=False, registry=SCAFFOLD)
    assert result["verdict"] == REFUSED and result["refused_condition"] == "file_upload_required"
    optional = apply_walk.plan_step(resume_step(), full_bank(), index=1, final=False, registry=SCAFFOLD)
    assert optional["verdict"] == PLAN, optional
    assert optional["fields"][1]["action"] == "leave_as_drawn"
    assert all(line.get("action") != "fill" for line in optional["fields"]
               if line["input_kind"] == "file")


def test_a_bank_answer_crosses_no_input_kind():
    numeric_as_text = bank_of(("phone", "numeric", "Mobile phone number", "5550100"))
    result = apply_walk.plan_step(contact_step(), numeric_as_text, index=0, final=False,
                                  registry=SCAFFOLD)
    assert result["verdict"] == NEEDS_OPERATOR, result


def test_another_platforms_answer_never_reaches_a_linkedin_field():
    naukri_only = bank_text(bank_line("phone", "text", "Mobile phone number", "5550100",
                                      platform="naukri"))
    result = apply_walk.plan_step(contact_step(), naukri_only, index=0, final=False,
                                  registry=SCAFFOLD)
    assert result["verdict"] == NEEDS_OPERATOR, result


def test_a_never_auto_answer_is_planned_only_where_he_must_see_it():
    attested = bank_text(
        bank_line("phone", "text", "Mobile phone number", "5550100"),
        bank_line("resume", "radio", Q_RESUME, "Resume-B.pdf"),
        bank_line("yoe-widgets", "numeric", Q_YEARS, "4"),
        bank_line("auth-elsewhere", "radio", Q_AUTH, "Yes", cls="work_authorisation"),
        bank_line("notice", "text", Q_NOTICE, "30"),
        bank_line("lang-esperanto", "select", Q_LANG, "Professional"),
    )
    plan = _plan(walk(), attested)
    assert plan["verdict"] == PLAN, plan
    must_see = {line["question"]: line for line in plan["answers_he_must_see"]}
    assert must_see[Q_AUTH]["never_auto"] is True
    assert must_see["Email address"]["source"] == "linkedin_prefill"
    assert Q_YEARS not in must_see


def test_a_group_of_boxes_is_answered_by_its_labels():
    tools = StepReading(
        fields=(FieldReading(tag="fieldset", input_type="checkbox", question="Tools used?",
                             options=("Docker", "Kafka", "Redis"), required=True),),
        controls=(DISMISS, NEXT), dialogs=1, scan_complete=True,
    )
    assert apply_walk.classify_field(tools.fields[0]) == "multi_select"
    chosen = bank_of(("tools", "multi_select", "Tools used?", "Redis | Docker"))
    result = apply_walk.plan_step(tools, chosen, index=0, final=False, registry=SCAFFOLD)
    assert result["verdict"] == PLAN and result["fields"][0]["action"] == "choose", result
    stray = bank_of(("tools", "multi_select", "Tools used?", "Docker | Rust"))
    result = apply_walk.plan_step(tools, stray, index=0, final=False, registry=SCAFFOLD)
    assert result["needs_operator"][0]["needs"] == "confirmed_answer_is_not_an_option_drawn"
    held = dataclasses.replace(tools, fields=(dataclasses.replace(tools.fields[0],
                                                                  value="Redis | Docker"),))
    same = apply_walk.plan_step(held, bank_of(("tools", "multi_select", "Tools used?",
                                               "Docker | Redis")),
                                index=0, final=False, registry=SCAFFOLD)
    assert same["fields"][0]["action"] == "keep_prefill", "a set compared as a string"


# ---------------------------------------------------------------------------
# 4. The plan (the PREVIEW)
# ---------------------------------------------------------------------------


def test_a_complete_walk_plans_every_field_and_submits_once_on_confirm():
    plan = _plan(walk(), full_bank())
    assert plan["verdict"] == PLAN, plan
    assert [s["kind"] for s in plan["steps"]] == ["contact_info", "resume_choice", "screening", "review"]
    assert [s["press"] for s in plan["steps"]] == ["advance", "advance", "advance", "submit"]
    shown = {line["question"]: (line["action"], line.get("value")) for line in plan["review_will_show"]}
    assert shown[Q_YEARS] == ("fill", "4")
    assert shown[Q_AUTH] == ("choose", "Yes")
    assert shown[Q_LANG] == ("choose", "Professional")
    assert shown[Q_RESUME] == ("choose", "Resume-B.pdf")
    assert plan["submits_on_confirm"] == 1
    assert apply_walk.confirm_presses(plan).count("submit") == 1
    assert apply_walk.confirm_presses(plan)[-1] == "submit"
    assert "submit" not in apply_walk.dry_walk_presses(plan)
    assert apply_walk.dry_walk_presses(plan)[-2:] == ["dismiss", "discard"]


def test_a_submit_hook_before_the_last_step_is_refused():
    early = dataclasses.replace(contact_step(), controls=(DISMISS, NEXT, SUBMIT))
    result = _plan([early] + walk()[1:], full_bank())
    assert result["verdict"] == REFUSED and result["refused_condition"] == "submit_before_review"
    assert result["step"] == 0


@pytest.mark.parametrize("controls", [(DISMISS,), (DISMISS, NEXT, REVIEW)], ids=["none", "two"])
def test_a_step_before_the_last_needs_exactly_one_advance(controls):
    step = dataclasses.replace(contact_step(), controls=controls)
    result = _plan([step] + walk()[1:], full_bank())
    assert result["refused_condition"] == "advance_count", result


def test_the_last_step_must_be_a_review_step():
    result = _plan(walk()[:3], full_bank())
    assert result["verdict"] == REFUSED and result["refused_condition"] == "final_step_is_not_review"


def test_the_review_step_may_draw_no_advance():
    result = _plan(walk()[:3] + [review_step(DISMISS, SUBMIT, NEXT)], full_bank())
    assert result["verdict"] == REFUSED, result
    assert result["refused_condition"] == "advance_on_the_review_step", result


def test_no_steps_is_no_plan():
    result = apply_walk.plan_walk([], full_bank(), registry=SCAFFOLD)
    assert result["verdict"] == REFUSED and result["refused_condition"] == "no_steps"
    assert apply_walk.confirm_presses(result) == []


def test_too_many_steps_is_refused():
    many = [dataclasses.replace(screening_step(), heading=str(i),
                                fields=(FieldReading(tag="input", input_type="text",
                                                     question=f"Question {i}?", required=False),))
            for i in range(apply_walk.MAX_STEPS)] + [review_step()]
    result = _plan(many, full_bank())
    assert result["refused_condition"] == "too_many_steps", result


def test_a_press_that_did_not_move_the_flow_stops_the_walk():
    steps = [contact_step(), contact_step()] + walk()[1:]
    result = _plan(steps, full_bank())
    assert result["verdict"] == REFUSED and result["refused_condition"] == "stuck", result
    assert result["step"] == 1


def test_a_bank_edit_after_the_preview_changes_the_plan_fingerprint():
    before = _plan(walk(), full_bank())
    edited = bank_of(
        ("phone", "text", "Mobile phone number", "5550100"),
        ("resume", "radio", Q_RESUME, "Resume-B.pdf"),
        ("yoe-widgets", "numeric", Q_YEARS, "5"),
        ("auth-elsewhere", "radio", Q_AUTH, "Yes"),
        ("notice", "text", Q_NOTICE, "30"),
        ("lang-esperanto", "select", Q_LANG, "Professional"),
    )
    after = _plan(walk(), edited)
    assert before["fingerprint"] != after["fingerprint"]
    assert _plan(walk(), full_bank())["fingerprint"] == before["fingerprint"]


# ---------------------------------------------------------------------------
# 5. The confirm walk, and the one press that cannot be taken back
# ---------------------------------------------------------------------------


def _complete_plan():
    plan = _plan(walk(), full_bank())
    assert plan["verdict"] == PLAN
    return plan


def test_the_submit_gate_proceeds_only_on_the_final_planned_step():
    plan = _complete_plan()
    gate = apply_walk.submit_gate(plan, review_step(), index=3, submits_pressed=0, registry=SCAFFOLD)
    assert gate["proceed"] is True, gate


def _one_step_plan(live):
    return {"verdict": PLAN, "steps": [{"fingerprint": apply_walk.step_fingerprint(live)}]}


GATE_CASES = {
    "1_already_submitted": lambda: (_complete_plan(), review_step(), 3, 1, SCAFFOLD),
    "2_not_the_final_step": lambda: (_complete_plan(), review_step(), 2, 0, SCAFFOLD),
    "3_scan_incomplete": lambda: (
        _complete_plan(), dataclasses.replace(review_step(), scan_complete=False), 3, 0, SCAFFOLD),
    "4_drifted_from_the_plan": lambda: (
        _complete_plan(), review_step(DISMISS, SUBMIT, ControlReading(name="Edit")), 3, 0, SCAFFOLD),
    "5_submit_count": lambda: (
        _one_step_plan(review_step(DISMISS, SUBMIT, SUBMIT)),
        review_step(DISMISS, SUBMIT, SUBMIT), 0, 0, SCAFFOLD),
    "6_submit_not_pressable": lambda: (
        _complete_plan(),
        review_step(DISMISS, dataclasses.replace(SUBMIT, enabled=False)), 3, 0, SCAFFOLD),
    "7_name_does_not_corroborate": lambda: (
        _complete_plan(),
        review_step(DISMISS, dataclasses.replace(SUBMIT, name="Send it")), 3, 0, SCAFFOLD),
    "8_advance_present": lambda: (
        _one_step_plan(review_step(DISMISS, SUBMIT, NEXT)),
        review_step(DISMISS, SUBMIT, NEXT), 0, 0, SCAFFOLD),
    "9_not_a_measured_review_step": lambda: (_complete_plan(), review_step(), 3, 0, SHAPES),
}


@pytest.mark.parametrize("code", sorted(GATE_CASES))
def test_each_submit_condition_refuses_under_its_own_code(code):
    plan, live, index, pressed, registry = GATE_CASES[code]()
    gate = apply_walk.submit_gate(plan, live, index=index, submits_pressed=pressed, registry=registry)
    assert gate["proceed"] is False, gate
    assert gate["refused_condition"] == code, gate


def test_a_step_that_drifted_from_the_plan_stops_before_anything_is_put_in_it():
    plan = _complete_plan()
    grown = dataclasses.replace(
        screening_step(),
        fields=screening_step().fields + (
            FieldReading(tag="input", input_type="text", question="A question added later?",
                         required=True),),
    )
    check = apply_walk.step_matches_plan(plan, 2, grown)
    assert check["proceed"] is False and check["refused_condition"] == "drifted_from_the_plan"
    assert apply_walk.step_matches_plan(plan, 2, screening_step())["proceed"] is True


@pytest.mark.parametrize("index", [-1, 4])
def test_a_confirm_step_the_plan_never_had_is_refused(index):
    check = apply_walk.step_matches_plan(_complete_plan(), index, review_step())
    assert check["proceed"] is False and check["refused_condition"] == "no_planned_step"
    refusal = _plan(walk()[:3], full_bank())
    check = apply_walk.step_matches_plan(refusal, 0, contact_step())
    assert check["refused_condition"] == "no_planned_step", "a refusal was matched as a plan"


def test_a_value_the_dry_walk_typed_is_not_drift():
    """LinkedIn may hand the confirm walk what the dry walk typed, prefilled."""
    plan = _complete_plan()
    typed = dataclasses.replace(
        contact_step(),
        fields=(contact_step().fields[0],
                dataclasses.replace(contact_step().fields[1], value="5550100")),
    )
    assert apply_walk.step_matches_plan(plan, 0, typed)["proceed"] is True


# ---------------------------------------------------------------------------
# 6. The inverse, and the states a walk stops at
# ---------------------------------------------------------------------------


def test_no_flow_is_opened_until_its_inverse_is_measured():
    may, why = apply_walk.may_open_flow()
    assert may is False
    assert "control.dismiss" in why and "control.discard" in why
    assert apply_walk.may_open_flow(SCAFFOLD)[0] is True


def test_every_refusal_carries_the_inverse_and_the_inverse_never_submits_or_saves():
    stops = [
        _plan([dataclasses.replace(contact_step(), dialogs=2)], full_bank()),
        _plan(walk()[:3], full_bank()),
        _plan(walk(), bank_of()),
        apply_walk.plan_walk(walk(), full_bank()),
    ]
    for result in stops:
        assert result["verdict"] in (REFUSED, NEEDS_OPERATOR), result
        acts = [step["act"] for step in result["inverse"]]
        assert acts == ["dismiss", "discard", "verify_no_draft"]
        assert not {"submit", "save", "advance"} & set(acts)


def limit_step() -> StepReading:
    return StepReading(
        heading="",
        fields=(),
        controls=(DISMISS,),
        dialogs=1,
        scan_complete=True,
        notices=("A notice the page drew",),
    )


def test_a_limit_state_is_reported_and_never_retried():
    result = apply_walk.plan_step(limit_step(), full_bank(), index=0, final=False, registry=SCAFFOLD)
    assert result["verdict"] == LIMIT, result
    assert result["retry"] == "never"
    assert [a["act"] for a in result["inverse"]] == ["dismiss", "discard", "verify_no_draft"]
    assert "fields" not in result and "press" not in result


def test_without_a_measured_signature_a_limit_is_an_unmeasured_step_never_a_plan():
    result = apply_walk.plan_step(limit_step(), full_bank(), index=0, final=False)
    assert result["verdict"] == REFUSED, result
    assert result["refused_condition"] == "unmeasured_step"
    assert result["saw"]["looks_like"] == "daily_limit_or_pause"


def test_the_walker_drives_nothing():
    """No mutating call in the module: it plans, it never presses."""
    source = (REPO / "linkedin_server" / "apply_walk.py").read_text(encoding="ascii")
    for call in (".click(", ".fill(", ".press(", ".check(", ".select_option(",
                 ".set_input_files(", ".type(", ".goto(", ".dispatch_event("):
        assert call not in source, call


# ---------------------------------------------------------------------------
# 7. read_draft_state over the REAL Draft-tab skeleton (not scaffolding)
# ---------------------------------------------------------------------------

#: The posting the skeleton's one draft row carries (a synthetic id).
DRAFT_ROW_JOB = "4011223344"
OTHER_JOB = "4099887766"
VIEWPORT = {"width": 1280, "height": 720}


def tracker(name: str) -> str:
    return (FIXTURES / f"{name}.html").read_text(encoding="ascii")


@pytest.fixture
async def over():
    playwright = pytest.importorskip("playwright.async_api")
    async with playwright.async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)

        async def _run(html: str, job_id: str):
            context = await browser.new_context(viewport=dict(VIEWPORT))
            try:
                page = await context.new_page()
                await page.set_content(html, wait_until="domcontentloaded", timeout=60_000)
                return await apply_walk.read_draft_state(page, job_id)
            finally:
                await context.close()

        try:
            yield _run
        finally:
            await browser.close()


def test_the_draft_skeleton_is_the_draft_tab_with_one_row():
    html = tracker("jobs_tracker_row")
    assert "Draft &#183; 1" in html
    assert html.count(f"/jobs/view/{DRAFT_ROW_JOB}") >= 1
    assert OTHER_JOB not in html


async def test_the_drafted_posting_reads_as_a_draft_left_behind(over):
    state, why = await over(tracker("jobs_tracker_row"), DRAFT_ROW_JOB)
    assert state == apply_walk.DRAFT_LEFT, why


async def test_another_posting_reads_as_no_draft_when_the_whole_tab_was_read(over):
    state, why = await over(tracker("jobs_tracker_row"), OTHER_JOB)
    assert state == apply_walk.NO_DRAFT, why
    assert "all 1 rows" in why


async def test_a_partial_draft_tab_is_unknown_never_no_draft(over):
    """DERIVED from the skeleton by one asserted edit: the count says 3."""
    html = tracker("jobs_tracker_row").replace("Draft &#183; 1", "Draft &#183; 3")
    assert "Draft &#183; 3" in html
    state, why = await over(html, OTHER_JOB)
    assert state == writes.UNKNOWN, why


async def test_another_tab_cannot_say_no_draft(over):
    """The Saved tab draws "In Progress", never a Draft count, so: unknown."""
    html = tracker("jobs_tracker_empty")
    assert "Draft &#183;" not in html and "In Progress &#183; 1" in html
    state, why = await over(html, OTHER_JOB)
    assert state == writes.UNKNOWN, why


class _NoPage:
    def __getattr__(self, name):
        raise AssertionError(f"the page was touched ({name}) for an invalid job id")


@pytest.mark.parametrize("job_id", ["", "12345", "not-a-number", "4011223344/../x", None])
async def test_a_job_id_that_is_not_a_job_id_is_refused_without_reading(job_id):
    state, why = await apply_walk.read_draft_state(_NoPage(), job_id)
    assert state == writes.UNKNOWN and "numeric" in why
