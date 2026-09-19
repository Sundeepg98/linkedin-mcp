"""`intro_fields.signature` must never emit a name, and must say `unknown`.

Two properties carry this module and both are asserted adversarially rather
than on clean input:

**1. NO NAME LEAVES.** The whole reason this projection exists is that the
shipped reader emits ungated names. If a name can reach the output, the
module has no purpose. Asserted by feeding it a name-shaped label and
searching the ENTIRE rendered payload for it, not just the fields it was
expected to appear in.

**2. AN UNCOMPARABLE LABEL POISONS `absent` INTO `unknown`.** With four
unnamed controls measured live in this container, a bare present/absent answer
would report `absent` for a field that might be behind one of them. That is
the tidy-zero this repository has paid for repeatedly, and it is the property
most likely to be quietly removed by a later simplification -- so it gets the
adversarial case rather than a happy one.
"""
from __future__ import annotations

import json

from linkedin_server import intro_fields


def _rec(name, tag="input", **kw):
    out = {"name": name, "tag": tag}
    out.update(kw)
    return out


SYNTHETIC_NAME = "Marcus Whitfield"


def test_a_name_cannot_reach_the_output():
    """THE PROPERTY THE MODULE EXISTS FOR, asserted over the WHOLE payload."""
    sig = intro_fields.signature([
        _rec(SYNTHETIC_NAME),
        _rec("Headline"),
    ])
    rendered = json.dumps(sig)
    assert SYNTHETIC_NAME not in rendered
    assert "Marcus" not in rendered and "Whitfield" not in rendered


def test_a_name_shaped_label_still_counts_structurally():
    """It must not leak the name AND must not pretend the control is absent."""
    sig = intro_fields.signature([_rec(SYNTHETIC_NAME)])
    assert sig["controls"] == 1
    assert sig["comparable_labels"] == 1
    assert sig["uncomparable_labels"] == 0


def test_present_is_reported_for_a_documented_field():
    sig = intro_fields.signature([_rec("Headline"), _rec("First name")])
    assert sig["fields"]["headline"] == "present"
    assert sig["fields"]["first_name"] == "present"


def test_absent_only_when_every_label_was_comparable():
    sig = intro_fields.signature([_rec("Headline")])
    assert sig["fields"]["postal_code"] == "absent"


def test_an_unnamed_control_turns_absent_into_unknown():
    """THE TRI-STATE. Four such controls were measured live on 2026-09-19."""
    sig = intro_fields.signature([_rec("Headline"), _rec(None)])
    assert sig["fields"]["headline"] == "present"
    assert sig["fields"]["postal_code"] == "unknown"
    assert sig["uncomparable_labels"] == 1


def test_an_opaque_label_is_uncomparable_and_not_absent():
    """An uncertifiable label is NOT evidence about what the field is called."""
    sig = intro_fields.signature([_rec("<opaque>")])
    assert sig["uncomparable_labels"] == 1
    assert sig["fields"]["headline"] == "unknown"


def test_form_fields_counts_only_form_tags():
    sig = intro_fields.signature([
        _rec("a", tag="input"), _rec("b", tag="select"),
        _rec("c", tag="textarea"), _rec("d", tag="button"),
        _rec("e", tag="a"),
    ])
    assert sig["form_fields"] == 3
    assert sig["tags"]["button"] == 1


def test_the_scope_bound_always_travels():
    """An `absent` read without its bound is a claim about the wrong thing."""
    sig = intro_fields.signature([_rec("Headline")])
    assert "container" in sig["scope"]
    assert "67" in sig["scope"]


def test_is_answerable_refuses_an_empty_container():
    """A signature over nothing answers nothing, and every field reads absent."""
    assert intro_fields.is_answerable(intro_fields.signature([])) is False
    assert intro_fields.is_answerable(
        intro_fields.signature([_rec("Headline")])
    ) is True


def test_is_answerable_refuses_a_container_with_no_comparable_label():
    """Controls present, none nameable -- the tidy-zero case, refused."""
    sig = intro_fields.signature([_rec(None), _rec("<opaque>")])
    assert sig["controls"] == 2
    assert intro_fields.is_answerable(sig) is False


def test_non_dict_records_are_ignored_rather_than_crashing():
    sig = intro_fields.signature([_rec("Headline"), "not a record", None, 7])
    assert sig["controls"] == 1


def test_the_live_shape_measured_on_2026_09_19_is_answerable():
    """The real container: 6 text, 2 checkbox, 2 select, 4 button/a, 4 unnamed.

    Reconstructed from the structural counts of a live run -- tags and
    name_source only, no label from that run is reproduced here.
    """
    records = (
        [_rec(f"field {i}", tag="input") for i in range(6)]
        + [_rec(f"check {i}", tag="input", type="checkbox") for i in range(2)]
        + [_rec(f"select {i}", tag="select") for i in range(2)]
        + [_rec(None, tag="button") for _ in range(4)]
        + [_rec("link", tag="a") for _ in range(2)]
    )
    sig = intro_fields.signature(records)
    assert sig["controls"] == 16
    assert sig["form_fields"] == 10
    assert sig["uncomparable_labels"] == 4
    assert intro_fields.is_answerable(sig) is True
    # With four unnamed controls present, NOTHING may read `absent`.
    assert "absent" not in set(sig["fields"].values())
