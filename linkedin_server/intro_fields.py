"""A NAME-FREE FIELD SIGNATURE for the intro editor, and nothing else.

`INTRO-EDITOR-UNREAD-CONTROLS` (rows `P A14` postal code, `P A15` location
display, `P A22` primary position) is blocked on a precondition: **does the
control exist to be written?** Answering it needs the editor's field
inventory, and the shipped reader is the wrong SHAPE for a caller to hold.

## Why this is not a second reader

``dom.read_self_owned_editor_fields`` already reads that container and this
module **does not re-read it**. It takes that reader's output and projects it.
Four waves reimplemented a shipped instrument on 2026-09-05 and three got a
broken one; the standing rule is IMPORT IT.

**What it changes is the CONTRACT, not the source.** The shipped reader is a
MEASUREMENT INSTRUMENT -- its own tool says so in capitals -- and it emits one
record per control carrying ``name``, ungated, because
``linkedin_update_profile_field`` needs to aim. That is the right contract for
a human extending the server and the wrong one for anything that stores,
logs or returns a payload:

    read_self_owned_editor_fields   per-control records, names UNGATED
    this module                     counts and booleans, NO NAME AT ALL

**The vocabulary ships INTO the comparison and only a flag comes back.** That
is the ``menus.py`` shape, and it is why this module can be held by a caller
that must never carry a name.

## What it cannot do, stated before what it can

**IT CANNOT BANK `A14`, `A15` OR `A22`. All three are WRITES.** A field
inventory settles whether the control is THERE; every one of those rows also
needs a WriteSpec, a gate and a ruling. A run that moved no row is the
expected outcome, not a failure.

**IT CANNOT SEE PAST THE CONTAINER IT IS GIVEN.** Measured 2026-09-19: the
shipped reader returned **16 controls on one run and 17 on another**, while
the intro editor has been measured at **67**. So this container is a SUBSET
of the editor, the count is not stable across loads, and an absence here is
an absence FROM THIS CONTAINER and never from the editor. Every verdict this
module emits carries that bound rather than leaving a reader to infer it.

**A FIELD IT CANNOT NAME IS `unnamed`, NOT ABSENT.** On that same run four of
sixteen controls had ``name_source`` of ``none`` -- no accessible name of any
kind. A projection that silently dropped them would report a smaller, tidier
inventory than the page actually has.
"""
from __future__ import annotations

from typing import Any, Iterable, Optional

#: LinkedIn's own documented intro fields, as the census cites them, each with
#: the spellings a label might use. SHIPPED IN so that only a boolean comes
#: back. Extend by adding a spelling, never by returning a name.
DOCUMENTED_FIELDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("first_name", ("first name", "given name")),
    ("last_name", ("last name", "surname", "family name")),
    ("headline", ("headline",)),
    ("current_position", ("current position", "primary position",
                          "show in your intro")),
    ("education", ("education", "school")),
    ("country_region", ("country", "region")),
    ("postal_code", ("postal code", "zip code", "pin code")),
    ("city", ("city", "locality", "location")),
    ("industry", ("industry",)),
    ("website", ("website",)),
    ("contact_info", ("contact info",)),
)

#: Tags that are a FORM FIELD rather than a control on the form.
FORM_TAGS: frozenset[str] = frozenset({"input", "select", "textarea"})

#: What the shipped shaper emits when it will not certify a label. A record
#: wearing one of these is NOT evidence about what the field is called.
OPAQUE_MARKERS: frozenset[str] = frozenset({"<opaque>", "<redacted>"})


def _label_of(record: Any) -> Optional[str]:
    """The record's name, or None when there is nothing to compare.

    None is returned for a missing name AND for an opaque one, and the two are
    counted separately by the caller. Collapsing them would let an
    uncertifiable label read as an absent field.
    """
    if not isinstance(record, dict):
        return None
    raw = record.get("name")
    if raw is None:
        return None
    text = str(raw).strip()
    if not text or text in OPAQUE_MARKERS:
        return None
    return text.lower()


def signature(fields: Iterable[Any]) -> dict[str, Any]:
    """Project the shipped reader's records into a signature carrying no name.

    Returns counts, a tri-state per documented field, and the bound that makes
    the whole thing readable:

        present    a label in this container matched a shipped spelling
        absent     no label matched, AND every label was comparable
        unknown    no label matched, but some label could not be compared --
                   so the field may be sitting behind one of them

    **THE THIRD STATE IS THE POINT.** With four unnamed controls in the
    container, a bare present/absent answer would report `absent` for a field
    that might be one of those four. `unknown` is what an honest inventory
    says, and it is the difference between an instrument and a tidy answer.
    """
    records = [r for r in fields if isinstance(r, dict)]
    labels = [_label_of(r) for r in records]
    comparable = [lab for lab in labels if lab is not None]
    uncomparable = len(labels) - len(comparable)

    tags: dict[str, int] = {}
    for rec in records:
        tag = str(rec.get("tag") or "?").lower()
        tags[tag] = tags.get(tag, 0) + 1

    verdicts: dict[str, str] = {}
    for field, spellings in DOCUMENTED_FIELDS:
        hit = any(sp in lab for lab in comparable for sp in spellings)
        if hit:
            verdicts[field] = "present"
        elif uncomparable:
            verdicts[field] = "unknown"
        else:
            verdicts[field] = "absent"

    form_fields = sum(count for tag, count in tags.items() if tag in FORM_TAGS)
    return {
        "controls": len(records),
        "form_fields": form_fields,
        "comparable_labels": len(comparable),
        "uncomparable_labels": uncomparable,
        "tags": dict(sorted(tags.items())),
        "fields": dict(sorted(verdicts.items())),
        # THE BOUND TRAVELS WITH THE VERDICT, ALWAYS. A caller that reads
        # `absent` without this is reading a claim about the editor when the
        # measurement is about one container inside it.
        "scope": (
            "one container inside the intro editor. The editor has been "
            "measured at 67 controls and this container at 16-17, so an "
            "absence here is an absence FROM THIS CONTAINER and never from "
            "the editor."
        ),
    }


def is_answerable(sig: dict[str, Any]) -> bool:
    """Would any verdict in this signature be worth acting on?

    A signature over an empty container answers nothing, and every field in it
    would read `absent` -- which is the tidy-zero this repository keeps
    paying for. So a caller asks this first.
    """
    if not isinstance(sig, dict):
        return False
    return int(sig.get("controls") or 0) > 0 and (
        int(sig.get("comparable_labels") or 0) > 0
    )
