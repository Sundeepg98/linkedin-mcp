"""An empty value is admitted in ONE place: a recorded CLEAR -- census row P A8 (2026-10-10).

THE DEFECT, MEASURED LIVE. P A8 ("Additional name") reads EMPTY on his own
profile, and its live proof is "test, then restore". The original is ``""``,
and ``writes._clean_target_part`` refuses an empty component -- so
``linkedin_update_profile_field(field="Additional name", value="")`` was
refused, while the first write's receipt printed exactly that call under
``to_put_it_back``.

THE RECORD AND THE ADMISSION, held here without a browser:

1. ``linkedin_server/field_restore.py`` keeps a PROCESS-LOCAL restore record
   per canonical field name -- the field, what this server's write typed (out
   of every repr), when, and whether it is used -- assigned into by ONE
   function, single use, thirty minutes of life, and importing nothing that
   reaches a disk or a log.
2. ``writes._clear_target`` admits the empty value for ``update_profile_field``
   ONLY while a live, unused record names that exact field; the canonical
   target is ``<field> :: `` and the typed bytes are its empty slice. Every
   other case is refused: no record, a record for another field, a used or
   expired record, the Premium badge switch, an absent (None) value, and every
   other action and composite kind -- those with their refusal unchanged.

What ``writes.perform`` does with a record -- writes it, checks it at the
click, spends it -- is ``tests/test_an_empty_original_is_restored_by_a_clear.py``.

RED FIRST: the admission tests failed against the unwired module with
"'update_profile_field' needs 'value' and got ''" at ``_clean_target_part``;
the run is in the lane's child-C report.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

from linkedin_server import field_restore, profile_editor, writes
from linkedin_server.errors import WriteAttemptError
from linkedin_server.writes import spec_for_action
from tests.test_writes import _functions_assigning_into

_SPEC = spec_for_action("update_profile_field")

#: LinkedIn's label for the field P A8 reads, as the census names it.
FIELD = "Additional name"
#: INVENTED, distinctive so a leak would be visible.
TYPED = "Zzplaceholder"


@pytest.fixture(autouse=True)
def _no_record_survives_a_test():
    field_restore.discard_all()
    yield
    field_restore.discard_all()


def _expire(monkeypatch, record) -> None:
    """Move THIS MODULE'S clock past the record's life -- grants keep theirs."""
    monkeypatch.setattr(
        field_restore, "_now",
        lambda: record.recorded_at + field_restore.RESTORE_TTL_SECONDS + 1,
    )


# ---------------------------------------------------------------------------
# 1. The record: one writer, single use, bounded, in memory only
# ---------------------------------------------------------------------------


def test_a_record_holds_the_field_what_was_typed_when_and_unused():
    record = field_restore.record_empty_prior(FIELD, TYPED)
    assert record is field_restore.live_record(FIELD)
    assert (record.field, record.typed, record.used) == (FIELD, TYPED, False)
    assert 0 <= record.age() < 5 and not record.expired()
    assert field_restore.RESTORE_TTL_SECONDS == 30 * 60
    assert TYPED not in repr(record), "the typed value leaked into a repr"


def test_a_record_admits_one_clear_and_then_none():
    field_restore.record_empty_prior(FIELD, TYPED)
    assert field_restore.why_no_clear(FIELD) is None
    assert field_restore.spend(FIELD) is True
    assert field_restore.live_record(FIELD) is None
    assert "already been used" in field_restore.why_no_clear(FIELD)


def test_an_expired_record_admits_nothing(monkeypatch):
    _expire(monkeypatch, field_restore.record_empty_prior(FIELD, TYPED))
    assert field_restore.live_record(FIELD) is None
    assert "expired" in field_restore.why_no_clear(FIELD)


def test_a_record_for_one_field_admits_no_other():
    field_restore.record_empty_prior("City", TYPED)
    assert field_restore.live_record(FIELD) is None
    assert "No such write is recorded" in field_restore.why_no_clear(FIELD)


@pytest.mark.parametrize("field, typed", [("", TYPED), ("   ", TYPED), (FIELD, ""), (FIELD, None), (None, TYPED)])
def test_nothing_typed_or_no_field_records_nothing(field, typed):
    assert field_restore.record_empty_prior(field, typed) is None
    assert field_restore._RECORDS == {}


@pytest.mark.parametrize("kind, current, words", [
    ("select_option", TYPED, "TYPED into a text field"),
    ("fill", None, "could not be read"),
    ("fill", "Zzhandedited", "ONLY CLEARS WHAT IT WROTE"),
    ("fill", TYPED, "still holds exactly"),
])
def test_the_click_time_verdict_holds_its_own_rules(kind, current, words):
    """PURE, the four answers of ``clear_verdict``; none of them names a value."""
    field_restore.record_empty_prior(FIELD, TYPED)
    proceed, why = field_restore.clear_verdict(FIELD, current, kind)
    assert proceed is (words == "still holds exactly"), why
    assert words in why, why
    assert TYPED not in why and "Zzhandedited" not in why, why


def test_the_click_time_verdict_refuses_without_a_live_record(monkeypatch):
    assert field_restore.clear_verdict(FIELD, TYPED, "fill")[0] is False
    _expire(monkeypatch, field_restore.record_empty_prior(FIELD, TYPED))
    proceed, why = field_restore.clear_verdict(FIELD, TYPED, "fill")
    assert proceed is False and "expired" in why, why


def test_only_one_function_assigns_into_the_records():
    writers = _functions_assigning_into(
        pathlib.Path(field_restore.__file__).read_text(encoding="utf-8"), "_RECORDS"
    )
    assert writers == {"record_empty_prior"}, writers


def test_the_record_module_imports_nothing_that_reaches_a_disk_or_a_log():
    """Never on disk, never logged: the module imports only what it needs to
    hold a record in memory, so there is no route to either."""
    tree = ast.parse(pathlib.Path(field_restore.__file__).read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module)
    assert imported == {"__future__", "dataclasses", "time", "typing"}, imported
    called = {
        node.func.id for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert not called & {"open", "print", "exec", "eval"}, called


def test_writes_discard_all_drops_the_records_too():
    field_restore.record_empty_prior(FIELD, TYPED)
    writes.discard_all()
    assert field_restore._RECORDS == {}


# ---------------------------------------------------------------------------
# 2. The admission: ONE place, ONE field, ONE live record -- refused elsewhere
# ---------------------------------------------------------------------------


def test_with_a_record_the_empty_value_is_admitted_as_the_clear_target():
    """RED before the build: refused by ``_clean_target_part`` whatever had
    been recorded -- the call the first write's receipt printed."""
    field_restore.record_empty_prior(FIELD, TYPED)
    canonical = writes._target_for(_SPEC, {"field": FIELD, "value": ""})
    assert canonical == FIELD + writes.TARGET_JOIN
    # ONE SPELLING: whitespace is stripped like any value, and the canonical
    # string re-normalises to itself -- mint re-canonicalises the preview's.
    assert writes._target_for(_SPEC, {"field": " " + FIELD + " ", "value": "   "}) == canonical
    assert writes._target_for(_SPEC, canonical) == canonical


def test_the_clear_types_the_empty_slice_of_its_own_target():
    """``tests/test_typed_bytes.py``'s claim, for the clear: what the one fill
    types is the content half of the canonical target -- here the empty
    slice after the separator -- and nothing composed. Every other split of
    the target reads the field."""
    field_restore.record_empty_prior(FIELD, TYPED)
    canonical = writes._target_for(_SPEC, {"field": FIELD, "value": ""})
    assert writes._text_component_of(_SPEC, canonical) == ""
    assert canonical.split(writes.TARGET_JOIN, 1) == [FIELD, ""]
    assert writes.url_target_of(_SPEC, canonical) == FIELD
    assert writes.anchor_label_for(_SPEC, canonical) == FIELD
    assert writes._is_clear_target(_SPEC, canonical)
    assert not writes._is_clear_target(_SPEC, FIELD + writes.TARGET_JOIN + TYPED)


def _refusal(target) -> str:
    with pytest.raises(WriteAttemptError) as excinfo:
        writes._target_for(_SPEC, target)
    return str(excinfo.value)


def test_no_record_refuses_the_empty_value_and_says_why():
    message = _refusal({"field": FIELD, "value": ""})
    assert "needs 'value' and got ''" in message, message
    assert "No such write is recorded" in message, message


def test_a_record_for_another_field_refuses():
    field_restore.record_empty_prior("City", TYPED)
    assert "No such write is recorded" in _refusal({"field": FIELD, "value": ""})


def test_a_used_record_refuses():
    field_restore.record_empty_prior(FIELD, TYPED)
    field_restore.spend(FIELD)
    assert "already been used" in _refusal({"field": FIELD, "value": ""})


def test_an_expired_record_refuses(monkeypatch):
    _expire(monkeypatch, field_restore.record_empty_prior(FIELD, TYPED))
    assert "expired" in _refusal({"field": FIELD, "value": ""})
    assert "expired" in _refusal(FIELD + writes.TARGET_JOIN)


def test_the_premium_badge_switch_refuses_the_empty_value_even_with_a_record():
    field_restore.record_empty_prior(profile_editor.PREMIUM_BADGE_TITLE, "on")
    message = _refusal({"field": profile_editor.PREMIUM_BADGE_TITLE, "value": ""})
    assert "switch" in message, message


@pytest.mark.parametrize("target", [{"field": FIELD, "value": None}, {"field": FIELD}])
def test_a_missing_value_is_not_an_empty_one(target):
    """None is not ``""``: an absent value is refused as before, record or not."""
    field_restore.record_empty_prior(FIELD, TYPED)
    message = _refusal(target)
    assert "needs 'value'" in message and "CLEAR" not in message, message


def _urn() -> str:
    # BUILT AT RUNTIME, as tests/test_typed_bytes.py builds it: a long digit
    # run written out in a tracked file is the shape the identity guard refuses.
    return "urn:li:" + "activity:" + ("1234567890" * 2)[:19]


@pytest.mark.parametrize("action, target, subject", [
    ("update_setting", {"setting": "Dark mode", "value": ""}, "Dark mode"),
    ("comment_on_item", {"item": _urn(), "text": ""}, _urn()),
    ("publish_post", "", "Placeholder post"),
], ids=["setting_and_value", "item_and_text", "post_text"])
def test_every_other_action_refuses_the_empty_value_as_before(action, target, subject):
    """Even with a record planted under the subject's name: the admission is
    ``update_profile_field``'s and nobody else's, and their refusal is the
    unchanged one -- it never mentions a clear."""
    field_restore.record_empty_prior(subject, TYPED)
    with pytest.raises(WriteAttemptError) as excinfo:
        writes._target_for(spec_for_action(action), target)
    message = str(excinfo.value)
    assert "and got ''" in message and "CLEAR" not in message, message
