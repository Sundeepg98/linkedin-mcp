"""The gate's own prose, checked against the code it describes.

WHY THIS FILE EXISTS. ``WriteSpec`` carries four long prose fields that the
confirm block PRINTS -- ``reversible_by``, ``residue``,
``reversibility_evidence`` and ``direction_source``, rendered as
``reversible_by``, ``what_it_cannot_undo``, ``reversibility_evidence`` and the
direction block's ``read_from``. They are the last thing the operator reads
before he authorises an irreversible act, and NOTHING COMPARED THEM TO
ANYTHING.

THE ONE GUARD THAT EXISTED COULD NOT SEE THIS.
``writes._reversibility_disagreement`` compares ``reversibility_class`` against
the FIRST WORD of ``spec.reversibility`` -- two short fields, against each
other. It never reads the four long ones, so every sentence in them was
unchecked by construction.

WORSE, THE SUITE WAS HOLDING THE STALE TEXT IN. ``tests/test_writes.py``
asserted ``"NOT this server" in unfollow_by or "not performed" in unfollow_by``
-- an OR that accepted the very phrase that had gone false as a SATISFYING
condition. A test that pins a sentence pins it whether or not it is true.

FIVE DEFECTS WERE LIVE WHEN THIS FILE WAS WRITTEN, 2026-09-03, all of them in
text the operator reads before confirming:

    update_profile_field.reversible_by          said the previous value is one
                                                "nothing here records", while
                                                perform() reads it before it
                                                types and returns it verbatim
    update_profile_field.reversible_by          said '/edit/' is forbidden "so
                                                it cannot reach the editor in
                                                either direction", while that
                                                exact url is an EXEMPTION
    update_profile_field.reversibility_evidence said the editors "have never
                                                been OPENED", after they were
                                                censused and after a value
                                                reader was wired into the
                                                write path
    follow_company.residue                      said "IT IS WHY THIS ACTION IS
                                                STILL NOT PERFORMED" while
                                                sitting in PERFORMABLE
    unfollow_company.reversible_by              said follow_company "is not
                                                performed", same reason
    send_message.reversible_by                  said '/messaging/compose' is
                                                forbidden "so nothing here can
                                                reach a composer in either
                                                direction" -- on the action
                                                whose whole job is reaching one
    save_job.reversible_by / .direction_source  printed a Saved-tab failure in
                                                the PRESENT TENSE, fixed
                                                2026-08-31

Seven findings, five specs. The brief that commissioned this file named four;
the other three are what a check finds that a census does not.

WHAT A RULE IS ALLOWED TO BE. Every rule pairs a DETECTOR over the prose with
a PREDICATE COMPUTED FROM THE LIVE CODE -- ``PERFORMABLE`` membership, the
read boundary's own answer, the syntax tree of ``perform``. A rule may never
compare prose against a second copy of the prose, because that is the pin this
file exists to replace.

ONE RULE HAS NO CODE PREDICATE AND SAYS SO. ``PRESENT_TENSE_FAILURE`` fires on
any claim that something "is currently failing", whatever the code does,
because a gate cannot re-measure such a sentence: nothing in this process
knows when it was written or whether it still holds. The fix is a DATE, not a
better tense.

AND THE SECOND LAW: an instrument enters only if it has been shown failing.
Every rule below has a control that makes it fire on a CONSTRUCTED spec, and
most have a real spec that must stay green -- ``set_open_to_work`` says its
surface "has never been loaded" and is RIGHT, because its ``url_template`` is
None; ``apply_job`` and ``publish_post`` cite a forbidden ``/withdraw`` and
``/delete`` that genuinely are not their own address. A rule that fired on
those would be a rule that only knows how to read English.
"""

from __future__ import annotations

import ast
import pathlib
import re
from dataclasses import dataclass
from typing import Callable, Optional

import pytest

from linkedin_server import readonly, writes
from linkedin_server.writes import PERFORMABLE, SANCTIONED_WRITES, WriteSpec

WRITES_PY = pathlib.Path(writes.__file__).resolve()

#: The prose fields the confirm block PRINTS. Not every string on the spec:
#: ``reversibility_procedure`` is a TODO addressed to whoever measures next and
#: is deliberately allowed to describe a gap, and ``wrong_state_note`` fires
#: only on a refusal. These four are what he reads while deciding.
PRINTED_PROSE: tuple[str, ...] = (
    "reversible_by",
    "residue",
    "reversibility_evidence",
    "direction_source",
)

#: Two shapes of target, because a spec's own surface is only reachable when
#: its template can be FILLED. A numeric id covers the job and company family;
#: a urn covers the feed-item family. Reachability is "at least one probe
#: builds a url this server may read", which is the question the prose answers.
_PROBE_TARGETS: tuple[str, ...] = (
    "123456789",
    "urn:li:activity:1234567890123456789",
)

#: Sentence boundaries, and the colon is one of them ON PURPOSE. The claim
#: "IT IS WHY THIS ACTION IS STILL NOT PERFORMED: THE UNDO CANNOT BE AIMED"
#: puts its subject and its evidence on opposite sides of a colon, and a
#: splitter that ignored colons would attribute the claim to the wrong action.
_SENTENCE_BREAK = re.compile(r"(?<=[.:;])\s+")

#: A QUOTED RETRACTION IS NOT AN ASSERTION, and this file learned that the
#: hard way -- the first version of it went red on the very corrections it had
#: just demanded, because this package's standing convention is to QUOTE THE
#: SENTENCE IT IS RETRACTING so the mistake stays legible. That convention is
#: everywhere in ``writes.py`` and it is the reason four of the corrections
#: this file drove could be reviewed at all.
#:
#: A CHECK THAT FORBIDS THE CORRECTION IS WORSE THAN NO CHECK. It would push
#: every future fixer into silently swapping sentences, which is exactly the
#: behaviour the convention exists to stop and exactly how these seven
#: defects survived: nobody could see what a field used to say.
#:
#: SO THE EXEMPTION IS NARROW AND TAKES TWO THINGS, never one:
#:
#:   1. the match sits inside a DOUBLE-QUOTED span, and
#:   2. a retraction marker appears in the same field BEFORE that span opens.
#:
#: One alone is not enough, and both halves have a control below. A bare
#: quotation with no marker still fires -- otherwise any false claim could be
#: laundered by putting quotes round it -- and a marker with the claim outside
#: the quotes still fires, which is what caught the half-quoted clause in
#: ``update_profile_field.reversible_by`` on the first run of this rule.
_QUOTED_SPAN = re.compile(r'"[^"]*"')
_RETRACTION_MARKER = re.compile(
    r"used\s+to\s+(?:say|read|end|claim|carry|close|add)"
    r"|\bit\s+(?:said|read)\b"
    r"|(?:was|were|is)\s+(?:false|wrong)"
    r"|quoted\s+(?:so|rather\s+than)"
    r"|is\s+DISCHARGED",
    re.IGNORECASE,
)


def _is_a_quoted_retraction(text: str, match: re.Match) -> bool:
    """True when this match is a sentence being RETRACTED, not asserted."""
    for span in _QUOTED_SPAN.finditer(text):
        if span.start() < match.start() and match.end() <= span.end():
            return bool(_RETRACTION_MARKER.search(text[: span.start()]))
    return False


def _own_surface_read_url(spec: WriteSpec) -> Optional[str]:
    """The spec's own url, IF the read boundary admits it. Else None.

    Asks ``readonly`` rather than re-deriving its rules: an exact-url
    exemption is invisible to any reimplementation of "is this substring
    forbidden", and an exemption is exactly what two of the findings above
    turned on.
    """
    if not spec.url_template:
        return None
    for probe in _PROBE_TARGETS:
        try:
            url = spec.url_template.format(target=probe)
        except Exception:  # pragma: no cover - a template nobody can fill
            continue
        if readonly.is_read_url(url):
            return url
    return None


def _restore_actions() -> frozenset[str]:
    """Actions for which ``perform`` builds a restore block with a previous value.

    READ OFF THE SYNTAX TREE of ``writes.py``, never off a list kept beside it.
    The claim under test is "nothing here records the previous value", and the
    only honest refutation is the code that records it -- so the predicate is
    the assignment itself: an ``if spec.action == "..."`` whose body assigns a
    dict literal to ``restore_block`` carrying the key ``previous_value``.

    Both halves matter. Without the key this would match any per-action branch
    that happened to be named ``restore_block``; without the name it would
    match any dict with a ``previous_value`` in it.
    """
    tree = ast.parse(WRITES_PY.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        test = node.test
        if not (
            isinstance(test, ast.Compare)
            and isinstance(test.left, ast.Attribute)
            and test.left.attr == "action"
            and len(test.ops) == 1
            and isinstance(test.ops[0], ast.Eq)
            and len(test.comparators) == 1
            and isinstance(test.comparators[0], ast.Constant)
            and isinstance(test.comparators[0].value, str)
        ):
            continue
        action = test.comparators[0].value
        for stmt in node.body:
            if not isinstance(stmt, ast.Assign) or not isinstance(stmt.value, ast.Dict):
                continue
            names = {t.id for t in stmt.targets if isinstance(t, ast.Name)}
            keys = {
                k.value
                for k in stmt.value.keys
                if isinstance(k, ast.Constant) and isinstance(k.value, str)
            }
            if "restore_block" in names and "previous_value" in keys:
                found.add(action)
    return frozenset(found)


def _actions_named_in(sentence: str) -> set[str]:
    """Which sanctioned actions this sentence talks about.

    Tool name first, because ``linkedin_follow_company`` is how the specs
    usually refer to a sibling and a word-boundary match on the bare action
    would miss it -- ``_`` is a word character, so ``\\bfollow_company\\b``
    does not match inside ``linkedin_follow_company``. The same property is
    what stops ``follow_company`` matching inside ``unfollow_company``.
    """
    named: set[str] = set()
    for spec in SANCTIONED_WRITES.values():
        if spec.tool_name in sentence:
            named.add(spec.action)
        elif re.search(r"\b%s\b" % re.escape(spec.action), sentence):
            named.add(spec.action)
    return named


# ---------------------------------------------------------------------------
# The rules
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _Finding:
    action: str
    field: str
    rule: str
    quote: str
    code_says: str

    def __str__(self) -> str:
        return "%s.%s [%s]\n      prose: ...%s...\n      code:  %s" % (
            self.action,
            self.field,
            self.rule,
            self.quote,
            self.code_says,
        )


@dataclass(frozen=True)
class _Rule:
    name: str
    detector: re.Pattern[str]
    #: ``(spec, match, sentence) -> reason the code contradicts it``, or None
    #: when the code agrees and the prose may stand.
    contradiction: Callable[[WriteSpec, re.Match, str], Optional[str]]


def _not_performed(spec: WriteSpec, match: re.Match, sentence: str) -> Optional[str]:
    """A claim that an action is not performed, checked against PERFORMABLE.

    The SUBJECT is whichever action the sentence names; a sentence naming none
    is talking about the spec it lives on, which is how "THIS ACTION IS STILL
    NOT PERFORMED" resolves.
    """
    subjects = _actions_named_in(sentence) or {spec.action}
    live = sorted(subject for subject in subjects if subject in PERFORMABLE)
    if not live:
        return None
    return "writes.PERFORMABLE contains %s" % ", ".join(live)


def _no_record(spec: WriteSpec, match: re.Match, sentence: str) -> Optional[str]:
    """A claim that no previous value is kept, checked against ``perform``."""
    if spec.action not in _restore_actions():
        return None
    return (
        "perform() builds a restore block for %s carrying 'previous_value' "
        "-- read off the syntax tree of writes.py, not off a list" % spec.action
    )


def _unreachable_own_surface(
    spec: WriteSpec, match: re.Match, sentence: str
) -> Optional[str]:
    """A claim that this action's own surface cannot be reached, checked.

    ``set_open_to_work`` makes exactly this claim and is RIGHT: it has no
    ``url_template`` at all, so there is nothing for the boundary to admit.
    That is the discrimination this rule has to have, and it is why the
    predicate is the boundary's answer rather than the sentence's confidence.
    """
    url = _own_surface_read_url(spec)
    if url is None:
        return None
    return "readonly.is_read_url(%r) is True -- this server reads that page" % url


def _forbidden_list_claim(
    spec: WriteSpec, match: re.Match, sentence: str
) -> Optional[str]:
    """A named address said to be forbidden, when it is this spec's OWN address.

    The substring may be genuinely forbidden IN GENERAL and still be exempted
    for one exact url -- which is how ``update_profile_field`` reaches
    ``/in/me/edit/intro/`` and how ``send_message`` reaches the composer. A
    spec citing a forbidden fragment that its own address CONTAINS, on an
    address the boundary admits, is describing a wall it walks through daily.

    ``apply_job`` cites ``/withdraw`` and ``publish_post`` cites ``/delete``:
    neither fragment is in its own url, so neither is this rule's business.
    """
    fragment = match.group("fragment")
    if not spec.url_template or fragment.lower() not in spec.url_template.lower():
        return None
    url = _own_surface_read_url(spec)
    if url is None:
        return None
    return (
        "%r is in this action's OWN url_template and readonly.is_read_url(%r) "
        "is True -- the fragment is exempted here, not refused" % (fragment, url)
    )


def _present_tense_failure(
    spec: WriteSpec, match: re.Match, sentence: str
) -> Optional[str]:
    """A present-tense operational failure. No code predicate, and that is the rule.

    THE ONLY RULE HERE WITHOUT ONE. "That read is currently failing" was true
    on 2026-08-30 and false on 2026-08-31, and nothing in this process can
    tell which day it is being read on. A gate may not print a claim it cannot
    re-measure -- the same rule that already forbids an unmeasured
    reversibility verdict, applied to an unmeasured HEALTH verdict.

    The fix is a date on both ends: what was measured, when, and when it
    closed.
    """
    return (
        "nothing re-measures this sentence. State the date it was measured "
        "and the date it closed, or drop it"
    )


RULES: tuple[_Rule, ...] = (
    _Rule(
        name="NOT_PERFORMED",
        detector=re.compile(
            r"\bnot\s+perform(?:ed|able)\b",
            re.IGNORECASE,
        ),
        contradiction=_not_performed,
    ),
    _Rule(
        name="NO_PREVIOUS_VALUE_KEPT",
        detector=re.compile(
            r"nothing\s+here\s+records"
            r"|no\s+previous-value\s+affordance"
            r"|does\s+not\s+record\s+the\s+previous\s+value",
            re.IGNORECASE,
        ),
        contradiction=_no_record,
    ),
    _Rule(
        name="OWN_SURFACE_UNREACHABLE",
        detector=re.compile(
            r"\breach\b[^.]{0,80}?\bin\s+either\s+direction\b"
            r"|\b(?:surface|editor|editors|page|composer)\b[^.]{0,60}?"
            r"\b(?:has|have)\s+never\s+been\s+(?:loaded|opened)\b",
            re.IGNORECASE,
        ),
        contradiction=_unreachable_own_surface,
    ),
    _Rule(
        name="CITES_A_WALL_IT_WALKS_THROUGH",
        detector=re.compile(
            r"['\"]?(?P<fragment>/[A-Za-z0-9/_-]+)['\"]?\s+is\s+on\s+the\s+"
            r"read\s+boundary's\s+forbidden\s+list",
            re.IGNORECASE,
        ),
        contradiction=_forbidden_list_claim,
    ),
    _Rule(
        name="PRESENT_TENSE_FAILURE",
        detector=re.compile(
            r"\b(?:is|are)\s+currently\s+(?:failing|broken)\b"
            r"|\bcurrently\s+FAILING\b",
            re.IGNORECASE,
        ),
        contradiction=_present_tense_failure,
    ),
)


def _sentence_around(text: str, match: re.Match) -> str:
    """The sentence a match landed in, for attributing its subject."""
    for sentence in _SENTENCE_BREAK.split(text):
        if match.group(0) in sentence:
            return sentence
    return text


def findings_for(spec: WriteSpec) -> list[_Finding]:
    """Every contradiction between one spec's printed prose and the code."""
    out: list[_Finding] = []
    for field in PRINTED_PROSE:
        text = getattr(spec, field, "") or ""
        for rule in RULES:
            for match in rule.detector.finditer(text):
                if _is_a_quoted_retraction(text, match):
                    continue
                sentence = _sentence_around(text, match)
                reason = rule.contradiction(spec, match, sentence)
                if reason is None:
                    continue
                start = max(0, match.start() - 90)
                end = min(len(text), match.end() + 90)
                out.append(
                    _Finding(
                        action=spec.action,
                        field=field,
                        rule=rule.name,
                        quote=" ".join(text[start:end].split()),
                        code_says=reason,
                    )
                )
    return out


def all_findings() -> list[_Finding]:
    return [
        finding
        for _, spec in sorted(SANCTIONED_WRITES.items())
        for finding in findings_for(spec)
    ]


# ---------------------------------------------------------------------------
# The check
# ---------------------------------------------------------------------------


def test_no_printed_spec_prose_asserts_what_the_code_denies():
    """THE CHECK. Every printed sentence, against the code it describes."""
    found = all_findings()
    assert not found, (
        "%d sentence(s) the confirm block PRINTS assert something the code "
        "does not do. He reads these before authorising an irreversible act:"
        "\n\n%s" % (len(found), "\n\n".join(str(f) for f in found))
    )


# ---------------------------------------------------------------------------
# Controls -- every rule shown FIRING, and the near-misses shown NOT firing
# ---------------------------------------------------------------------------


def _with(action: str, **overrides: str) -> WriteSpec:
    """A spec with one prose field replaced. Frozen, so this rebuilds it."""
    return WriteSpec(**{**writes.spec_for_action(action).__dict__, **overrides})


def _rules_that_fired(spec: WriteSpec) -> set[str]:
    return {finding.rule for finding in findings_for(spec)}


@pytest.mark.parametrize(
    "action,field,prose,rule",
    [
        # An action that IS performable, said not to be.
        (
            "save_job",
            "residue",
            "This is why this action is still not performed.",
            "NOT_PERFORMED",
        ),
        # A sibling that IS performable, said not to be. The subject is
        # resolved from the sentence, not from the spec it sits on.
        (
            "unsave_job",
            "reversible_by",
            "NOT this server: linkedin_save_job is not performed.",
            "NOT_PERFORMED",
        ),
        # The restore path exists for this action, and the prose denies it.
        (
            "update_profile_field",
            "reversible_by",
            "Only if he still knows the previous value, which nothing here records.",
            "NO_PREVIOUS_VALUE_KEPT",
        ),
        # A surface the read boundary admits, said to be out of reach.
        (
            "save_job",
            "reversible_by",
            "Nothing here can reach the posting in either direction.",
            "OWN_SURFACE_UNREACHABLE",
        ),
        # The same, in the other spelling the specs actually use.
        (
            "publish_post",
            "reversibility_evidence",
            "The composer has never been loaded.",
            "OWN_SURFACE_UNREACHABLE",
        ),
        # A fragment of the action's OWN address, cited as forbidden.
        (
            "update_profile_field",
            "reversible_by",
            "'/edit/' is on the read boundary's forbidden list.",
            "CITES_A_WALL_IT_WALKS_THROUGH",
        ),
        # A health claim with no date, which nothing can re-measure.
        (
            "unfollow_company",
            "direction_source",
            "That read is currently failing.",
            "PRESENT_TENSE_FAILURE",
        ),
    ],
)
def test_each_rule_has_been_shown_failing(action, field, prose, rule):
    """A check that cannot fail certifies nothing.

    Each row is a spec CONSTRUCTED to violate one rule. These are what keep
    the file honest after the seven real defects are fixed: without them, a
    rule whose detector stopped matching -- a reworded phrase, a broken group
    name -- would go quietly green and certify a gate nobody was checking.
    """
    assert rule in _rules_that_fired(_with(action, **{field: prose}))


@pytest.mark.parametrize(
    "action,field,prose,rule",
    [
        # THE DISCRIMINATION THAT MATTERS MOST. set_open_to_work says its
        # surface has never been loaded and is RIGHT -- url_template is None.
        # A rule that fired here would be reading English, not code.
        (
            "set_open_to_work",
            "reversible_by",
            "The editor's surface has never been loaded, so nothing here can "
            "reach it in either direction.",
            "OWN_SURFACE_UNREACHABLE",
        ),
        # A forbidden fragment that is NOT this action's own address. apply_job
        # really cannot withdraw and publish_post really cannot delete.
        (
            "apply_job",
            "reversible_by",
            "'/withdraw' is on the read boundary's forbidden list.",
            "CITES_A_WALL_IT_WALKS_THROUGH",
        ),
        (
            "publish_post",
            "reversible_by",
            "'/delete' is on the read boundary's forbidden list.",
            "CITES_A_WALL_IT_WALKS_THROUGH",
        ),
        # An action that genuinely is not performable, correctly described.
        (
            "unsave_job",
            "residue",
            "set_open_to_work is not performed.",
            "NOT_PERFORMED",
        ),
        # The restore path does not exist for this action, so the same
        # sentence that is false on update_profile_field is true here.
        (
            "save_job",
            "reversible_by",
            "Only if he still knows the previous value, which nothing here records.",
            "NO_PREVIOUS_VALUE_KEPT",
        ),
    ],
)
def test_a_true_sentence_of_the_same_shape_stays_green(action, field, prose, rule):
    """The other half. Over-firing would train the next reader to ignore it."""
    assert rule not in _rules_that_fired(_with(action, **{field: prose}))


@pytest.mark.parametrize(
    "prose,still_fires,why",
    [
        (
            'It used to say "this action is not performed". It is.',
            False,
            "a marker before a quoted span is the retraction this package writes",
        ),
        (
            'The residue notes that "this action is not performed".',
            True,
            "QUOTES ARE NOT A LAUNDRY. No marker, so this is still an assertion",
        ),
        (
            "This field used to say it, and this action is not performed.",
            True,
            "a marker with the claim OUTSIDE the quotes is a half-retraction, "
            "which is exactly the shape that survived the first fix pass",
        ),
        (
            "This action is not performed.",
            True,
            "the bare assertion, which must not become unreachable",
        ),
    ],
)
def test_the_quoted_retraction_exemption_takes_two_things_not_one(
    prose, still_fires, why
):
    """The exemption, shown letting the right thing through and nothing else.

    THIS EXEMPTION IS THE MOST DANGEROUS LINE IN THE FILE. It is the only
    place a rule declines to fire on text that matches its detector, so it is
    the only place a false claim could hide. Each row is one way of getting it
    wrong, and three of the four must still fail.
    """
    fired = "NOT_PERFORMED" in _rules_that_fired(_with("save_job", residue=prose))
    assert fired is still_fires, why


def test_the_restore_predicate_is_derived_and_not_typed():
    """The AST predicate found the branch, and found only it.

    A predicate that silently returned the empty set would make
    ``NO_PREVIOUS_VALUE_KEPT`` unable to fire, which is the failure mode this
    whole file is about -- so the derivation is asserted rather than trusted.
    """
    assert _restore_actions() == frozenset({"update_profile_field"})


def test_every_rule_is_reachable_from_the_printed_fields():
    """No rule may sit on a field the operator never sees.

    A rule pointed at ``reversibility_procedure`` would look like coverage and
    check text nobody reads before confirming.
    """
    printed = set(PRINTED_PROSE)
    assert printed <= set(WriteSpec.__dataclass_fields__)
    rendered = {
        "reversible_by",
        "residue",
        "reversibility_evidence",
        "direction_source",
    }
    assert printed == rendered
