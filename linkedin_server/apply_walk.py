"""The multi-step Easy Apply walker, PHASE A: its guards, its plan and its inverse.

UNWIRED, deliberately. Lane apply-26, 2026-11-25; the record is
``_audit/2026-11-25-apply.md``, and ``tests/test_apply_walk.py`` holds every
guard below to a test that was shown failing first.

WHERE THIS STANDS, MEASURED. LinkedIn's apply flow has been opened on exactly
two postings, and what survives is COUNTS from one of them (2026-08-24): one
dialog, 2 forms, 1 file input, 43 buttons, one enabled "Submit application"
carrying ``dom.APPLY_SUBMIT_HOOK``, and no Next. The raw capture is gone, and
no step of a MULTI-STEP flow has ever been seen by anybody here. So nothing in
this module may drive a page, and nothing in it does: there is no click, fill,
press, check or select call in this file, and the one function that takes a
``page`` reads the job tracker's Draft tab and nothing else.

WHAT IS HERE, in the order the walk uses it:

* THE READING CONTRACT -- :class:`StepReading`, :class:`FieldReading` and
  :class:`ControlReading`, what a phase-B reader must report for one step.
  ``scan_complete`` defaults to False, as ``dom.read_apply_modal``'s does: an
  unscanned step must never read as an empty one.
* THE SHAPE REGISTRY -- :data:`SHAPES`. Every step, field and control shape the
  walker could recognise, each ``MEASURED`` (with the committed skeleton that
  measured it) or ``PROPOSED`` (with the capture that will measure it). TODAY
  ONE SHAPE IS MEASURED, the Draft tab the inverse verifies on; every
  multi-step shape is PROPOSED, so the walker refuses the first step of every
  multi-step flow and names what it saw. That is the measured state of the
  world, not a configuration to be flipped: a shape moves to ``MEASURED`` only
  with a tracked skeleton as its evidence, and ``tests/test_apply_walk.py``
  checks that the path exists.
* RECOGNITION -- :func:`classify_field`, :func:`classify_control`,
  :func:`classify_step`. Structure only: tags, input types, roles, the
  autocomplete and inputmode tokens, and data-attribute NAMES. A step's heading
  never decides its kind. Anything outside the known set is ``None`` and the
  plan refuses it, naming the structure it saw in a closed vocabulary.
* THE PLAN -- :func:`plan_step` and :func:`plan_walk`, the PREVIEW: every step,
  every field, what will be put in it and from which CONFIRMED bank class
  (``apply_answers``), or NEEDS-OPERATOR quoting the question and its input
  kind. Values come from his confirmed bank or from LinkedIn's own prefill,
  never from anything else on the page and never from his profile or resume.
* THE CONFIRM GUARDS -- :func:`step_matches_plan`, :func:`advanced` and
  :func:`submit_gate`: the confirm walk must meet the step the preview planned,
  and Submit is pressed once, on the final planned step, or not at all.
* THE INVERSE -- :func:`inverse_plan` and :func:`may_open_flow`: dismiss, take
  Discard, verify no draft is left. NO FLOW IS OPENED UNTIL ITS INVERSE IS
  MEASURED, because a round trip whose return leg has never been seen is not a
  round trip (the 2026-10-10 lesson: an unfollow was fired on a Page whose
  re-follow had already been refused). Today the dismiss and discard controls
  are PROPOSED, so :func:`may_open_flow` is False.
* :func:`read_draft_state` -- the inverse's verification, the ONE part built on
  real markup: the tracker's Draft tab, ``tests/fixtures/jobs_tracker_row.html``
  (a skeleton of the live tab, ``Draft &#183; 1``, one row), read through the
  shipped reconciliation ``writes._read_tracker_membership`` rather than a
  second copy of it.

PAGE TEXT. A question's words, and an option's, are the employer's: they leave
this module only inside a NEEDS-OPERATOR item or a plan field, sanitised by
``people_data.sanitise``, capped, and marked with ``people_data.UNTRUSTED_KEY``
-- the mitigations THIRD-PARTY-TEXT-AT-RUNTIME applies to a post's text and an
organisation's prose. Whether that ruling reaches screening questions, and
through which declared record, is a question the record puts to the
orchestrator before phase B wires anything; nothing here is wired.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any, Mapping, Optional, Sequence

from . import apply_answers, dom, people_data

# ---------------------------------------------------------------------------
# The reading contract
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FieldReading:
    """One form field in the step, as a phase-B reader must report it.

    Every attribute below is STRUCTURE except ``question``, ``options`` and
    ``value``, which are what the page drew and are untrusted. A radio group is
    ONE field: ``input_type`` "radio" and its labels in ``options``; so is a
    group of checkboxes (``tag`` "fieldset", ``input_type`` "checkbox"), whose
    ``value`` lists the checked labels joined by
    ``apply_answers.OPTION_SEPARATOR``.
    """

    tag: str
    input_type: str = ""
    role: str = ""
    aria_autocomplete: str = ""
    autocomplete: str = ""
    inputmode: str = ""
    #: None when the page did not say. The plan treats None as required.
    required: Optional[bool] = None
    question: str = ""
    options: tuple[str, ...] = ()
    #: What the field holds when read: LinkedIn's prefill, a selected option's
    #: label, or "" when empty. A checkbox reports ``checked`` instead. A
    #: select whose selected option is a PLACEHOLDER reports "" -- the reader
    #: decides that by the option's own empty ``value`` attribute (or its
    #: ``disabled``), never by its words, because a placeholder read as a
    #: value is a prefill nobody gave and the plan keeps prefills.
    value: str = ""
    checked: Optional[bool] = None


@dataclass(frozen=True)
class ControlReading:
    """One button-like control inside the dialog."""

    name: str = ""
    #: data-* attribute NAMES the control carries, never their values.
    hooks: tuple[str, ...] = ()
    enabled: bool = True
    visible: bool = True


@dataclass(frozen=True)
class StepReading:
    """One screen of the apply dialog."""

    heading: str = ""
    fields: tuple[FieldReading, ...] = ()
    controls: tuple[ControlReading, ...] = ()
    #: ``[role=dialog]`` on the page; the measured flow drew exactly one.
    dialogs: int = 0
    #: DEFAULT REFUSES. A reader earns True by reading every control and field.
    scan_complete: bool = False
    #: role=alert / aria-live text drawn inside the dialog (untrusted).
    notices: tuple[str, ...] = ()


# ---------------------------------------------------------------------------
# The shape registry
# ---------------------------------------------------------------------------

MEASURED = "MEASURED"
PROPOSED = "PROPOSED"
STATUSES = (MEASURED, PROPOSED)

#: The step kinds the brief names, plus the two states a walk must stop at.
STEP_KINDS: tuple[str, ...] = (
    "contact_info",
    "resume_choice",
    "screening",
    "review",
    "daily_limit_or_pause",
)
#: The field kinds: the bank's six, plus the file input a resume step may draw
#: (never filled by the walker -- uploading is census row J 70).
FIELD_KINDS: tuple[str, ...] = apply_answers.INPUT_KINDS + ("file",)
CONTROL_KINDS: tuple[str, ...] = ("submit", "advance", "dismiss", "discard")


@dataclass(frozen=True)
class Shape:
    id: str
    status: str
    evidence: str
    description: str


#: THE CAPTURE THAT MEASURES EVERY PROPOSED MULTI-STEP SHAPE. Its line is in
#: ``_audit/_census/capture-queue.tsv``; its spec is the record's section 3.
WALK_CAPTURE = "C-J68-1"
DRAFT_CAPTURE = "C-J68-2"

_ONE_SINGLE_SCREEN_OBSERVATION = (
    "measured ONCE, on a single-screen flow (2026-08-24; dom.APPLY_SUBMIT_HOOK, "
    "counts only, the raw capture gone); whether a multi-step flow's final step "
    "carries it is "
)

SHAPES: dict[str, Shape] = {
    "step.contact_info": Shape(
        "step.contact_info", PROPOSED, WALK_CAPTURE,
        "a form step every field of which is text, select or typeahead, and "
        "every text field of which carries a contact autocomplete token or an "
        "email/tel type",
    ),
    "step.resume_choice": Shape(
        "step.resume_choice", PROPOSED, WALK_CAPTURE,
        "a form step that draws a file input (the one flow measured drew 1, "
        "page-level, placement unrecorded)",
    ),
    "step.screening": Shape(
        "step.screening", PROPOSED, WALK_CAPTURE,
        "any other form step: one or more labelled fields of the six bank kinds",
    ),
    "step.review": Shape(
        "step.review", PROPOSED,
        _ONE_SINGLE_SCREEN_OBSERVATION + WALK_CAPTURE + "'s to measure",
        "a step with no editable field and exactly one control carrying the "
        "submit hook",
    ),
    "step.daily_limit_or_pause": Shape(
        "step.daily_limit_or_pause", PROPOSED,
        "census J 82, a PRECONDITION row under APPLY-FLOW-IS-THE-APPLICATION: "
        "observable only when the limit is reached, so no capture can be "
        "scheduled; the first natural occurrence is kept as a skeleton",
        "a dialog with no field, no submit hook, no advance control and at "
        "least one notice",
    ),
    "field.text": Shape("field.text", PROPOSED, WALK_CAPTURE,
                        "input type text/email/tel/url or none, or a textarea"),
    "field.numeric": Shape("field.numeric", PROPOSED, WALK_CAPTURE,
                           "input type number, or inputmode numeric/decimal"),
    "field.select": Shape("field.select", PROPOSED, WALK_CAPTURE, "a select"),
    "field.radio": Shape("field.radio", PROPOSED, WALK_CAPTURE,
                         "a radio group, reported as one field with its labels"),
    "field.checkbox": Shape("field.checkbox", PROPOSED, WALK_CAPTURE,
                            "ONE input type checkbox"),
    "field.multi_select": Shape("field.multi_select", PROPOSED, WALK_CAPTURE,
                                "a group of checkboxes, reported as one field "
                                "with its labels"),
    "field.typeahead": Shape("field.typeahead", PROPOSED, WALK_CAPTURE,
                             "role combobox with aria-autocomplete list or both"),
    "field.file": Shape(
        "field.file", PROPOSED,
        "1 file input counted page-level on the single-screen flow "
        "(2026-08-24); its place in a multi-step flow is " + WALK_CAPTURE
        + "'s to measure",
        "an input type file; never filled",
    ),
    "control.submit": Shape(
        "control.submit", PROPOSED,
        _ONE_SINGLE_SCREEN_OBSERVATION + WALK_CAPTURE + "'s to measure",
        "a control carrying dom.APPLY_SUBMIT_HOOK",
    ),
    "control.advance": Shape(
        "control.advance", PROPOSED,
        "NEVER SEEN: dom.APPLY_ADVANCE_WORDS were chosen to REFUSE on, and "
        "zero advance controls have ever been drawn; " + WALK_CAPTURE,
        "a control whose name carries next, continue or review",
    ),
    "control.dismiss": Shape(
        "control.dismiss", PROPOSED, WALK_CAPTURE,
        "the dialog's own close control",
    ),
    "control.discard": Shape(
        "control.discard", PROPOSED,
        WALK_CAPTURE + " (the prompt the dismiss draws, if it draws one) and "
        + DRAFT_CAPTURE,
        "the Discard of the prompt a dismiss draws; never its Save",
    ),
    # THE EVIDENCE IS A SENTENCE THAT CITES THE SKELETON, never the bare path:
    # a package module naming a tracked data file in code reads as a READ to
    # the impact gate's sentence rule (tests/test_impact_gate_selects_data_
    # dependencies.py), which rests on the package never doing that. The
    # registry's own test pulls the path out of the sentence and checks it is
    # tracked. Lane CI run 45654516809 failed on the bare path.
    "verify.draft_tab": Shape(
        "verify.draft_tab", MEASURED,
        "a skeleton of his live Draft tab, tests/fixtures/jobs_tracker_row.html",
        "the job tracker's Draft tab, ?stage=draft, read through "
        "writes._read_tracker_membership",
    ),
}

#: The step shape for each step kind.
STEP_SHAPE = {kind: f"step.{kind}" for kind in STEP_KINDS}

# ---------------------------------------------------------------------------
# Recognition, by structure only
# ---------------------------------------------------------------------------

#: The HTML autocomplete tokens a contact field carries. Structure, not text:
#: these are the attribute's standard values, and a field is counted as a
#: contact field by them or by an email/tel input type.
CONTACT_AUTOCOMPLETE = frozenset(
    {"email", "tel", "tel-national", "tel-country-code", "name", "given-name",
     "family-name", "country", "country-name", "address-level2"}
)
_TEXT_TYPES = frozenset({"", "text", "email", "tel", "url"})
_CONTACT_TYPES = frozenset({"email", "tel"})

#: The closed vocabularies a refusal may describe a field in. An attribute
#: value outside them is reported as "other", so a page cannot write a string
#: into a refusal by putting it in a type attribute.
_TAGS = ("input", "select", "textarea", "fieldset", "div")
_INPUT_TYPES = ("", "text", "email", "tel", "url", "number", "radio",
                "checkbox", "file", "date", "hidden", "search", "password")
_ROLES = ("", "combobox", "radiogroup", "listbox", "textbox", "spinbutton",
          "checkbox", "radio")


def _closed(value: str, vocabulary: Sequence[str]) -> str:
    value = (value or "").strip().lower()
    return value if value in vocabulary else "other"


def classify_field(f: FieldReading) -> Optional[str]:
    """The field's kind, by structure, or ``None`` for a shape not in the set."""
    tag = (f.tag or "").strip().lower()
    itype = (f.input_type or "").strip().lower()
    role = (f.role or "").strip().lower()
    if role == "combobox":
        auto = (f.aria_autocomplete or "").strip().lower()
        return "typeahead" if auto in ("list", "both") else None
    if tag == "input" and itype == "file":
        return "file"
    if tag == "select":
        return "select"
    if itype == "radio" and tag in ("input", "fieldset"):
        return "radio"
    if tag == "input" and itype == "checkbox":
        return "checkbox"
    if tag == "fieldset" and itype == "checkbox":
        return "multi_select"
    if tag == "input" and (
        itype == "number"
        or (f.inputmode or "").strip().lower() in ("numeric", "decimal")
    ):
        return "numeric"
    if tag == "input" and itype in _TEXT_TYPES:
        return "text"
    if tag == "textarea":
        return "text"
    return None


def classify_control(c: ControlReading) -> str:
    """``submit`` / ``advance`` / ``dismiss`` / ``other`` / ``unnamed``.

    The submit HOOK decides submit, whatever the name says -- the gate checks
    the name corroborates it. Advance is ``dom.APPLY_ADVANCE_WORDS``, the same
    words the shipped gate refuses on, so the two cannot drift apart.
    """
    if dom.APPLY_SUBMIT_HOOK in c.hooks:
        return "submit"
    name = apply_answers.normalise_answer(c.name)
    if not name:
        return "unnamed"
    if any(word in name for word in dom.APPLY_ADVANCE_WORDS):
        return "advance"
    if name == "dismiss":
        return "dismiss"
    return "other"


def _is_contact_field(f: FieldReading) -> bool:
    return (
        (f.autocomplete or "").strip().lower() in CONTACT_AUTOCOMPLETE
        or (f.input_type or "").strip().lower() in _CONTACT_TYPES
    )


def classify_step(step: StepReading) -> Optional[str]:
    """The step's kind by structure, or ``None``. The heading is never read.

    Precedence, stated because two signatures can both fit: review (no field,
    one submit) before anything; then the limit-or-pause shape (no field, no
    submit, no advance, a notice); then a form step is resume_choice if it draws
    a file input, contact_info if every text field is a contact field and
    every field is text, select or typeahead, and screening otherwise.
    """
    kinds = [classify_field(f) for f in step.fields]
    roles = [classify_control(c) for c in step.controls]
    if None in kinds:
        return None
    if not kinds:
        if roles.count("submit") == 1:
            return "review"
        if not roles.count("submit") and not roles.count("advance") and step.notices:
            return "daily_limit_or_pause"
        return None
    if "file" in kinds:
        return "resume_choice"
    if all(k in ("text", "select", "typeahead") for k in kinds) and all(
        _is_contact_field(f) for f, k in zip(step.fields, kinds) if k == "text"
    ) and any(k == "text" for k in kinds):
        return "contact_info"
    return "screening"


def describe_step(step: StepReading) -> dict[str, Any]:
    """What a refusal says it saw: structure only, in closed vocabularies."""
    kinds = [classify_field(f) for f in step.fields]
    roles = [classify_control(c) for c in step.controls]
    unrecognised = [
        {
            "tag": _closed(f.tag, _TAGS),
            "input_type": _closed(f.input_type, _INPUT_TYPES),
            "role": _closed(f.role, _ROLES),
        }
        for f, k in zip(step.fields, kinds)
        if k is None
    ]
    return {
        "fields": len(step.fields),
        "field_kinds": {k: kinds.count(k) for k in FIELD_KINDS if kinds.count(k)},
        "fields_unrecognised": unrecognised,
        "fields_required": sum(1 for f in step.fields if f.required is True),
        "fields_required_unstated": sum(1 for f in step.fields if f.required is None),
        "fields_holding_a_value": sum(
            1 for f in step.fields if f.value or f.checked is True
        ),
        "controls": {r: roles.count(r) for r in
                     ("submit", "advance", "dismiss", "other", "unnamed")},
        "dialogs": step.dialogs,
        "scan_complete": step.scan_complete,
        "notices": len(step.notices),
        "looks_like": classify_step(step),
    }


# ---------------------------------------------------------------------------
# Page text, as it may leave
# ---------------------------------------------------------------------------

#: A question is cut here, an option label here, and at most this many options
#: are quoted.
QUESTION_CHARS = 300
OPTION_CHARS = 120
MAX_OPTIONS_QUOTED = 50


def _quoted(field_reading: FieldReading, kind: Optional[str]) -> dict[str, Any]:
    """The field as a NEEDS-OPERATOR item or a plan line may carry it."""
    out: dict[str, Any] = {
        "question": people_data.sanitise(field_reading.question, cap=QUESTION_CHARS),
        "input_kind": kind,
        people_data.UNTRUSTED_KEY: people_data.UNTRUSTED_NOTE,
    }
    if field_reading.options:
        out["options"] = [
            people_data.sanitise(option, cap=OPTION_CHARS)
            for option in field_reading.options[:MAX_OPTIONS_QUOTED]
        ]
        out["options_drawn"] = len(field_reading.options)
    return out


# ---------------------------------------------------------------------------
# The plan
# ---------------------------------------------------------------------------

PLAN = "PLAN"
NEEDS_OPERATOR = "NEEDS_OPERATOR"
REFUSED = "REFUSED"
LIMIT = "LIMIT"
VERDICTS = (PLAN, NEEDS_OPERATOR, REFUSED, LIMIT)

#: More steps than this is not a flow this walker has a reason to believe in.
MAX_STEPS = 12

#: The bank's platform for every answer this walker asks for: a row of his
#: answers LinkedIn's questions if it is LinkedIn's own or ``any``.
PLATFORM = "linkedin"


def _measured(registry: Mapping[str, Shape], shape_id: str) -> bool:
    shape = registry.get(shape_id)
    return shape is not None and shape.status == MEASURED


def _refusal(code: str, why: str, step: Optional[int], saw: Optional[dict] = None,
             registry: Mapping[str, Shape] = SHAPES) -> dict[str, Any]:
    out: dict[str, Any] = {
        "verdict": REFUSED,
        "refused_condition": code,
        "why": why,
        "step": step,
        "inverse": inverse_plan(registry),
    }
    if saw is not None:
        out["saw"] = saw
    return out


def _field_plan(f: FieldReading, kind: str, bank: apply_answers.Bank) -> dict[str, Any]:
    """What to do with one recognised field: an action, or a NEEDS item.

    Returns a dict with ``action`` -- ``keep_prefill``, ``fill``, ``choose``,
    ``check``, ``leave_empty`` -- or with ``needs`` naming why he must answer.
    """
    line = _quoted(f, kind)
    if kind == "file":
        if f.required is False or f.value:
            line["action"] = "leave_as_drawn"
            return line
        line["refused"] = "file_upload_required"
        return line
    if not apply_answers.normalise_question(f.question):
        line["refused"] = "unlabelled_field"
        return line
    answer = bank.answer_for(f.question, kind, options=f.options, platform=PLATFORM)
    if answer is not None and not answer.auto:
        # A NEVER-AUTO answer (an attestation, a consent, his own prose) is
        # used only because the preview puts it in front of him: the plan
        # names it, and the confirm token is his yes to it for THIS posting.
        line["never_auto"] = True
    if kind == "checkbox":
        # A CHECKBOX IS NEVER KEPT ON LINKEDIN'S WORD ALONE. A box can be an
        # act -- a consent, or a follow of the employer's Page -- so one that
        # arrives checked, with no confirmed answer of his, is an act nobody
        # chose, and the walk asks him. Only an unchecked, optional box with
        # no answer is left as it is.
        held = None if f.checked is None else ("checked" if f.checked else "unchecked")
        if answer is None:
            if held == "unchecked" and f.required is False:
                line["action"] = "leave_empty"
                return line
            line["needs"] = "checkbox_needs_his_answer"
            return line
        if held == answer.value:
            line.update(action="keep_prefill", source="linkedin_prefill_equals_bank",
                        bank_entry=answer.entry_id, value=held)
        else:
            line.update(action="check", bank_entry=answer.entry_id, value=answer.value)
        return line
    held = people_data.sanitise(f.value, cap=apply_answers.MAX_ANSWER_CHARS) or None
    if held is not None:
        if answer is None:
            line.update(action="keep_prefill", source="linkedin_prefill", value=held)
            return line
        if apply_answers.same_answer(kind, held, answer.value):
            line.update(action="keep_prefill", source="linkedin_prefill_equals_bank",
                        bank_entry=answer.entry_id, value=held)
            return line
        line.update(needs="prefill_differs_from_confirmed", bank_entry=answer.entry_id)
        return line
    if answer is None:
        if f.required is False:
            line["action"] = "leave_empty"
            return line
        line["needs"] = "not_in_bank"
        return line
    if kind in apply_answers.OPTION_KINDS:
        drawn = apply_answers.options_key_of(f.options)
        chosen = (apply_answers.split_options(answer.value) if kind == "multi_select"
                  else [answer.value])
        if not chosen or not all(apply_answers.normalise_answer(c) in drawn for c in chosen):
            line.update(needs="confirmed_answer_is_not_an_option_drawn",
                        bank_entry=answer.entry_id)
            return line
        line.update(action="choose", bank_entry=answer.entry_id, value=answer.value)
        return line
    line.update(action="fill", bank_entry=answer.entry_id, value=answer.value)
    return line


def plan_step(step: StepReading, bank: apply_answers.Bank, *, index: int,
              final: bool, registry: Mapping[str, Shape] = SHAPES) -> dict[str, Any]:
    """Decide ONE step: its plan, or the refusal that stops the walk here.

    ``final`` says whether the walk believes this is the last step -- the step
    on which, at confirm, Submit would be pressed. A step that draws the submit
    hook when it is not final, or that is final and is not a measured review
    step, is refused.
    """
    if not step.scan_complete:
        return _refusal(
            "scan_incomplete",
            "the step's scan did not finish, so an empty list beside it means "
            "UNKNOWN and not none -- absent is not zero",
            index, describe_step(step), registry)
    if step.dialogs != 1:
        return _refusal(
            "dialog_count",
            f"the page draws {step.dialogs} dialogs; the measured flow drew exactly 1",
            index, describe_step(step), registry)
    if any(classify_field(f) is None for f in step.fields):
        return _refusal(
            "unrecognised_field",
            "a field on this step is not one of the field shapes the walker "
            "knows; the refusal lists its tag, type and role",
            index, describe_step(step), registry)
    kind = classify_step(step)
    if kind is None:
        return _refusal(
            "unrecognised_step",
            "this step's structure matches no step shape the walker knows",
            index, describe_step(step), registry)
    if not _measured(registry, STEP_SHAPE[kind]):
        shape = registry.get(STEP_SHAPE[kind])
        evidence = shape.evidence if shape else "no registry entry"
        return _refusal(
            "unmeasured_step",
            f"this step looks like {kind} by a PROPOSED signature, and no "
            f"capture has measured that shape; it waits on: {evidence}",
            index, describe_step(step), registry)
    if kind == "daily_limit_or_pause":
        return {
            "verdict": LIMIT,
            "refused_condition": "daily_limit_or_pause",
            "why": (
                "LinkedIn drew the shape measured as its daily-limit or "
                "rate-pause state. Reported, and NEVER retried around: no "
                "second posting, no reopening, no wait-and-retry."
            ),
            "step": index,
            "retry": "never",
            "inverse": inverse_plan(registry),
        }
    roles = [classify_control(c) for c in step.controls]
    for role in set(roles) & {"submit", "advance", "dismiss"}:
        if not _measured(registry, f"control.{role}"):
            return _refusal(
                "unmeasured_control",
                f"the step draws a {role} control, a shape no capture has measured",
                index, describe_step(step), registry)
    if final:
        if kind != "review":
            return _refusal(
                "final_step_is_not_review",
                f"the walk's last step reads as {kind}, and Submit is pressed "
                "only on a measured review step",
                index, describe_step(step), registry)
        if roles.count("advance"):
            return _refusal(
                "advance_on_the_review_step",
                "the review step still draws an advance control",
                index, describe_step(step), registry)
    else:
        if roles.count("submit"):
            return _refusal(
                "submit_before_review",
                "a step before the last draws the submit hook; the walk never "
                "presses Submit except on the final planned step",
                index, describe_step(step), registry)
        if roles.count("advance") != 1:
            return _refusal(
                "advance_count",
                f"a step before the last must draw exactly one advance "
                f"control and this one draws {roles.count('advance')}",
                index, describe_step(step), registry)

    lines: list[dict[str, Any]] = []
    for f in step.fields:
        fkind = classify_field(f)
        assert fkind is not None  # classify_step returned None otherwise
        if not _measured(registry, f"field.{fkind}"):
            return _refusal(
                "unmeasured_field",
                f"the step draws a {fkind} field, a shape no capture has measured",
                index, describe_step(step), registry)
        lines.append(_field_plan(f, fkind, bank))
    refused = [line for line in lines if "refused" in line]
    if refused:
        return _refusal(
            refused[0]["refused"],
            "a field the walker will not touch stands between this step and the next",
            index, describe_step(step), registry)
    needs = [line for line in lines if "needs" in line]
    if needs:
        return {
            "verdict": NEEDS_OPERATOR,
            "why": (
                "the walk stops here: the questions below have no CONFIRMED "
                "answer in his bank (or LinkedIn's prefill disagrees with the "
                "one it has). Nothing is inferred from the page, his profile "
                "or his resume. Add each exactly as quoted, with its input "
                "kind, and confirm it."
            ),
            "step": index,
            "needs_operator": needs,
            "bank": bank.status(),
            "inverse": inverse_plan(registry),
        }
    return {
        "verdict": PLAN,
        "step": index,
        "kind": kind,
        "fields": lines,
        "press": "submit" if final else "advance",
        "fingerprint": step_fingerprint(step),
    }


def plan_walk(steps: Sequence[StepReading], bank: apply_answers.Bank, *,
              registry: Mapping[str, Shape] = SHAPES) -> dict[str, Any]:
    """The PREVIEW: a dry walk's step readings, planned end to end.

    The dry walk reads step 1, plans it, presses its advance, reads step 2, and
    so on, and NEVER presses Submit (:func:`dry_walk_presses`); this function
    is the same decision taken over the readings it recorded. It stops at the
    first step that refuses or needs him -- later steps were never seen.
    """
    if not steps:
        return _refusal("no_steps", "no step was read", None, None, registry)
    if len(steps) > MAX_STEPS:
        return _refusal(
            "too_many_steps",
            f"{len(steps)} steps; the walker stops at {MAX_STEPS}",
            None, None, registry)
    planned: list[dict[str, Any]] = []
    for index, step in enumerate(steps):
        if index and not advanced(steps[index - 1], step):
            return _refusal(
                "stuck",
                "the step read after an advance is the step read before it, "
                "so the press did not move the flow (a validation stop, or a "
                "control that does nothing) and the walk does not press again",
                index, describe_step(step), registry)
        decision = plan_step(step, bank, index=index,
                             final=index == len(steps) - 1, registry=registry)
        if decision["verdict"] != PLAN:
            decision["steps_planned_before_this"] = len(planned)
            return decision
        planned.append(decision)
    review = [
        {key: line.get(key) for key in
         ("question", "input_kind", "action", "value", "bank_entry",
          people_data.UNTRUSTED_KEY)}
        for step_plan in planned for line in step_plan["fields"]
    ]
    return {
        "verdict": PLAN,
        "steps": planned,
        "review_will_show": review,
        # THE ANSWERS HE MUST READ BEFORE HE CONFIRMS: never-auto rows of his
        # bank (attestations, consents, his own prose) and every value kept
        # from LinkedIn's prefill rather than from his bank.
        "answers_he_must_see": [
            line for step_plan in planned for line in step_plan["fields"]
            if line.get("never_auto") or line.get("source") == "linkedin_prefill"
        ],
        "submits_on_confirm": 1,
        "fingerprint": plan_fingerprint(planned),
        "bank": bank.status(),
        "inverse": inverse_plan(registry),
    }


# ---------------------------------------------------------------------------
# Fingerprints, and the confirm guards
# ---------------------------------------------------------------------------


def step_fingerprint(step: StepReading) -> str:
    """A step's identity: its fields' kinds, questions, options and required
    flags, and its controls' kinds. NOT the values it holds -- a confirm walk
    may meet the values the dry walk typed, prefilled -- and NOT its heading."""
    canonical = {
        "fields": [
            [classify_field(f) or "unrecognised",
             apply_answers.normalise_question(f.question),
             [apply_answers.normalise_answer(o) for o in f.options],
             f.required]
            for f in step.fields
        ],
        "controls": sorted(classify_control(c) for c in step.controls),
        "dialogs": step.dialogs,
    }
    blob = json.dumps(canonical, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(blob.encode("ascii")).hexdigest()[:16]


def plan_fingerprint(planned: Sequence[Mapping[str, Any]]) -> str:
    """The plan's identity: every step's fingerprint and every planned value's
    bank class and digest, so a bank edit after the preview invalidates it."""
    canonical = [
        [step_plan["fingerprint"],
         [[line.get("action"), line.get("bank_entry"),
           hashlib.sha256(str(line.get("value") or "").encode("utf-8")).hexdigest()[:16]]
          for line in step_plan["fields"]]]
        for step_plan in planned
    ]
    blob = json.dumps(canonical, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(blob.encode("ascii")).hexdigest()[:16]


def advanced(before: StepReading, after: StepReading) -> bool:
    """Did a press move the flow? Two equal fingerprints say it did not."""
    return step_fingerprint(before) != step_fingerprint(after)


def step_matches_plan(plan: Mapping[str, Any], index: int,
                      live: StepReading) -> dict[str, Any]:
    """At confirm: is the step on screen the step the preview planned here?"""
    steps = plan.get("steps") or []
    if plan.get("verdict") != PLAN or not 0 <= index < len(steps):
        return {"proceed": False, "refused_condition": "no_planned_step",
                "why": f"the plan has no step {index}"}
    if step_fingerprint(live) != steps[index]["fingerprint"]:
        return {
            "proceed": False,
            "refused_condition": "drifted_from_the_plan",
            "why": (
                "the step on screen is not the step the preview planned -- a "
                "question, an option, a required flag or a control differs -- "
                "so the confirm stops before anything is put in it"
            ),
            "saw": describe_step(live),
        }
    return {"proceed": True, "refused_condition": None, "why": ""}


def submit_gate(plan: Mapping[str, Any], live: StepReading, *, index: int,
                submits_pressed: int,
                registry: Mapping[str, Shape] = SHAPES) -> dict[str, Any]:
    """THE ONE PRESS THAT CANNOT BE TAKEN BACK, decided on the step on screen.

    Every condition is required, each refuses under its own code, and the
    first two are why Submit is pressed EXACTLY ONCE: never a second time,
    and never on any step but the final planned one.
    """
    out: dict[str, Any] = {"proceed": False, "refused_condition": None, "why": ""}
    steps = plan.get("steps") or []

    def refuse(code: str, why: str) -> dict[str, Any]:
        out.update(refused_condition=code, why=why)
        return out

    if plan.get("verdict") != PLAN or not steps:
        return refuse("0_no_plan", "there is no complete plan to submit")
    if submits_pressed != 0:
        return refuse("1_already_submitted",
                      f"Submit has been pressed {submits_pressed} time(s) on this "
                      "walk; it is pressed once or not at all")
    if index != len(steps) - 1:
        return refuse("2_not_the_final_step",
                      f"step {index} is not the plan's final step {len(steps) - 1}")
    if not live.scan_complete:
        return refuse("3_scan_incomplete", "the review step's scan did not finish")
    matched = step_matches_plan(plan, index, live)
    if not matched["proceed"]:
        return refuse("4_drifted_from_the_plan", matched["why"])
    # 5-8 BEFORE 9, so that each is reachable on its own: the review shape
    # requires exactly one submit, so a review check placed first would answer
    # for the submit count too, and a guard no reading can reach on its own is
    # one nobody can show failing.
    submits = [c for c in live.controls if classify_control(c) == "submit"]
    if len(submits) != 1:
        return refuse("5_submit_count",
                      f"{len(submits)} controls carry the submit hook; one is the shape")
    control = submits[0]
    if not (control.visible and control.enabled):
        return refuse("6_submit_not_pressable", "the submit control is hidden or disabled")
    if "submit" not in apply_answers.normalise_answer(control.name):
        return refuse("7_name_does_not_corroborate",
                      "the control carrying the hook is not named as a submit")
    if any(classify_control(c) == "advance" for c in live.controls if c.visible):
        return refuse("8_advance_present", "an advance control is still drawn")
    if classify_step(live) != "review" or not _measured(registry, STEP_SHAPE["review"]):
        return refuse("9_not_a_measured_review_step",
                      "the step on screen is not a measured review step")
    out.update(proceed=True, why="every condition holds on the final planned step")
    return out


# ---------------------------------------------------------------------------
# The presses each walk may make, and the inverse
# ---------------------------------------------------------------------------

#: The inverse, in order. It never contains a submit and never a save.
INVERSE: tuple[tuple[str, str], ...] = (
    ("dismiss", "control.dismiss"),
    ("discard", "control.discard"),
    ("verify_no_draft", "verify.draft_tab"),
)
_NEVER_IN_THE_INVERSE = frozenset({"submit", "save", "advance"})
assert not {act for act, _shape in INVERSE} & _NEVER_IN_THE_INVERSE


def inverse_plan(registry: Mapping[str, Shape] = SHAPES) -> list[dict[str, Any]]:
    """What an aborted walk does: dismiss, take Discard, verify no draft."""
    return [
        {"act": act, "shape": shape_id,
         "status": registry[shape_id].status if shape_id in registry else "MISSING"}
        for act, shape_id in INVERSE
    ]


def may_open_flow(registry: Mapping[str, Shape] = SHAPES) -> tuple[bool, str]:
    """May a walk open an apply flow at all? Only once its inverse is measured."""
    missing = [shape_id for _act, shape_id in INVERSE if not _measured(registry, shape_id)]
    if missing:
        return (
            False,
            "no flow is opened until its inverse is measured, and these are "
            f"not: {', '.join(missing)}",
        )
    return True, "every step of the inverse is measured"


def dry_walk_presses(plan: Mapping[str, Any]) -> list[str]:
    """The presses the PREVIEW's dry walk makes: open, advance per step, then
    the inverse. Submit is never among them."""
    steps = plan.get("steps") or []
    presses = ["open"] + ["advance" for _step in steps[:-1]]
    presses += [act for act, _shape in INVERSE if act != "verify_no_draft"]
    assert "submit" not in presses
    return presses


def confirm_presses(plan: Mapping[str, Any]) -> list[str]:
    """The presses the CONFIRM walk makes: open, advance per step, Submit once."""
    steps = plan.get("steps") or []
    if plan.get("verdict") != PLAN or not steps:
        return []
    return ["open"] + ["advance" for _step in steps[:-1]] + ["submit"]


# ---------------------------------------------------------------------------
# The inverse's verification, on real markup
# ---------------------------------------------------------------------------

DRAFT_LIST_URL = "https://www.linkedin.com/jobs-tracker/?stage=draft"
DRAFT_LEFT = "draft_left"
NO_DRAFT = "no_draft"
_JOB_ID = re.compile(r"^[0-9]{6,}$")


async def read_draft_state(page: Any, job_id: str, *, navigator: Any = None) -> tuple[str, str]:
    """Is a draft application for THIS posting in his tracker's Draft tab?

    Three answers -- ``draft_left``, ``no_draft``, ``unknown`` -- by the shipped
    reconciliation (absence from a partial list is not absence, in both
    directions), over a page the CALLER has already loaded at
    :data:`DRAFT_LIST_URL`. ``tab_key`` is ``draft`` because LinkedIn relabels
    the "In Progress" tab "Draft" on that address (measured; see
    ``linkedin_draft_applications``), so a page that is any other tab has no
    such count and reads ``unknown``, never ``no_draft``.

    The job id is the posting HE named, validated here; it never comes from a
    page.
    """
    from . import writes  # lazy: phase B wires this module into writes

    if not isinstance(job_id, str) or not _JOB_ID.match(job_id):
        return (writes.UNKNOWN, "the job id is not a numeric LinkedIn job id")
    stage = writes._TrackerStage(
        url=DRAFT_LIST_URL,
        tab_key="draft",
        tab_label="Draft",
        present=DRAFT_LEFT,
        absent=NO_DRAFT,
    )
    return await writes._read_tracker_membership(page, job_id, stage, navigator=navigator)
