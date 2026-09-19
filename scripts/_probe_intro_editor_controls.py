"""Run the SHIPPED intro-editor reader, because the blocker is an unread page.

`INTRO-EDITOR-UNREAD-CONTROLS` (rows `P A14`, `P A15`, `P A22`) says the intro
editor's controls have never been read. **The reader is not missing.**
``linkedin_profile_editor_fields`` ships, is wired, and its docstring says in
its first line that it names the controls inside the intro editor on his own
profile. What is missing is a RUN.

So this file imports the shipped tool and awaits it. It reimplements nothing:
four waves reimplemented a shipped instrument on 2026-09-05 and three got a
broken one, and the standing rule is IMPORT IT.

=============================================================================
WHAT THIS ANSWERS, AND WHAT IT CANNOT
=============================================================================

    P A14   Postal code                  "not among the 17 controls"
    P A15   Location display choice      "not among the 17 controls"
    P A22   Primary Position(s)          "real control, named verbatim in
                                          LinkedIn's own help article"

**ALL THREE ARE WRITES AND NONE OF THEM CAN BE BANKED BY A READ.** A read
settles their PRECONDITION -- whether the control exists to be written -- and
nothing more. Saying so first is the point: a run that moved no row would
otherwise look like a failure, when the honest outcome is that the blocker's
premise moves and the rows stay where they are.

The seventeen were read on 2026-09-02 and the editor has been measured at
**67 controls**, so a name absent from the seventeen may simply be in the other
fifty. That is the whole question.

=============================================================================
WHAT IS PRINTED -- and the reader already refuses to publish names
=============================================================================

``dom.read_self_owned_editor_fields`` runs its labels through the census
shaper, so a control whose name it cannot certify comes back ``<opaque>``.
**This file prints its verdict, its counts, and BOOLEANS about a closed
vocabulary this file owns** -- the field names from LinkedIn's own help
articles, shipped INTO the comparison so only a yes/no comes back. That is the
``menus.py`` shape: the vocabulary goes in, a position or a flag comes out.

No raw label is printed even when the shaper certifies it. The reader is
allowed to know; this file is not allowed to say.

CONTROL: the tool establishes self-ownership before reading and REFUSES
otherwise, and its refusal is forwarded whole. A refusal here is a result, not
an error -- and a run that silently returned no fields would be
indistinguishable from an editor with no controls, so the verdict is printed
before any count.

**NOTHING IS PRESSED.** The tool loads two pages and reads a container.

Run::

    LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224 \
        LINKEDIN_CDP_ATTACH_TIMEOUT_MS=60000 \
        ./venv/Scripts/python.exe scripts/_probe_intro_editor_controls.py

Writes NOTHING. Prints to stdout.
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import config, intro_fields  # noqa: E402
from linkedin_server import server as server_module  # noqa: E402

#: The closed vocabulary, from LinkedIn's own help articles as the census cites
#: them. Shipped INTO the comparison so only a boolean comes back.
FIELD_VOCABULARY: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("A14 postal code", ("postal code", "zip", "pin code")),
    ("A15 location display", ("location", "display", "region", "city")),
    ("A22 primary position", ("primary position", "primary", "current role",
                              "show in your intro")),
    # Controls the seventeen already named, as a POSITIVE CONTROL: if these
    # read absent too, the run saw nothing and the zeros above are void.
    ("CONTROL first name", ("first name",)),
    ("CONTROL last name", ("last name",)),
    ("CONTROL headline", ("headline",)),
)


def _structure(fields: list) -> int:
    """STRUCTURE, never a name. Returns how many controls are FORM FIELDS.

    **THE FIRST VERSION OF THIS BLOCK GUESSED FIELD NAMES AND ITS POSITIVE
    CONTROL CAUGHT IT.** It looked for "first name" / "last name" / "headline"
    and found none of the three, which voided every other boolean it printed.
    The diagnosis is structural rather than a wider needle list: the reader
    projects the container's CONTROLS, and a control is not a field. So this
    asks what KIND of thing the seventeen are before asking what they are
    called.
    """
    from collections import Counter
    tags = Counter(str(r.get("tag") or "?") for r in fields if isinstance(r, dict))
    types = Counter(str(r.get("type") or "-") for r in fields if isinstance(r, dict))
    roles = Counter(str(r.get("role") or "-") for r in fields if isinstance(r, dict))
    srcs = Counter(str(r.get("name_source") or "-") for r in fields if isinstance(r, dict))
    for label, counter in (("tag", tags), ("type", types),
                           ("role", roles), ("name_source", srcs)):
        rendered = "  ".join(f"{k}={v}" for k, v in counter.most_common())
        print(f"      {label:12s} {rendered}")
    form_like = sum(
        v for k, v in tags.items() if k in ("input", "select", "textarea")
    )
    print(f"    FORM FIELDS among the seventeen: {form_like}")
    print("    CHECKABLE (tri-state, None means NOT checkable): " + "  ".join(
        f"{k}={v}" for k, v in Counter(
            str(r.get("checked")) for r in fields if isinstance(r, dict)
        ).most_common()
    ))
    return form_like


async def main() -> int:
    if not config.CDP_ATTACH:
        print("REFUSED: LINKEDIN_CDP_ATTACH is not set.")
        print(f"    Re-run with LINKEDIN_CDP_ATTACH=1 "
              f"LINKEDIN_CDP_PORT={config.CDP_PORT}")
        return 2

    print("=" * 70)
    print("RUNNING THE SHIPPED TOOL: linkedin_profile_editor_fields")
    print("=" * 70)
    fn = getattr(server_module.linkedin_profile_editor_fields, "fn",
                 server_module.linkedin_profile_editor_fields)
    out = await fn()

    if not isinstance(out, dict):
        print(f"    unexpected return type: {type(out).__name__}")
        return 1

    # THE VERDICT BEFORE ANY COUNT. A refusal forwarded whole is a result.
    if "refused" in out:
        print(f"    REFUSED: {out.get('refused')}")
        print(f"    reason : {str(out.get('reason'))[:300]}")
        print("    That is the tool declining to aim, which it does when "
              "self-ownership is not established. It is a result, not an "
              "error, and nothing below it would be a reading.")
        return 0

    print(f"    pages_loaded: {out.get('pages_loaded')}")
    own = out.get("self_ownership")
    if isinstance(own, dict):
        print("    self_ownership: " + "  ".join(
            f"{k}={v}" for k, v in sorted(own.items())
            if isinstance(v, (bool, int))
        ))
    fields = out.get("fields")
    if not isinstance(fields, list):
        print("    NO fields key. Nothing below would be a reading.")
        return 0

    print(f"\n    controls read: {len(fields)}")
    labels: list[str] = []
    opaque = 0
    for rec in fields:
        if not isinstance(rec, dict):
            continue
        lab = rec.get("label") or rec.get("name") or ""
        if str(lab).strip() in ("<opaque>", "<redacted>"):
            opaque += 1
        labels.append(str(lab))
    print(f"    of which the shaper returned opaque: {opaque}")
    print(f"    certifiable labels available to compare: "
          f"{len(labels) - opaque}\n")
    print("    WHAT KIND OF THING ARE THEY -- structure only, no name:")
    form_like = _structure(fields)
    sig = intro_fields.signature(fields)
    print("    THE SIGNATURE, via linkedin_server.intro_fields:")
    print(f"      answerable: {intro_fields.is_answerable(sig)}   "
          f"comparable={sig['comparable_labels']}  "
          f"uncomparable={sig['uncomparable_labels']}")
    for field, verdict in sig["fields"].items():
        print(f"      {field:20s} {verdict}")
    if not form_like:
        print("    NO FORM FIELD IS IN THIS CONTAINER. The reader projects "
              "the editor's CONTROLS, and A14/A15/A22 are FIELDS -- so this "
              "tool does not answer them, and a wider needle list would not "
              "have helped. That is a finding about the INSTRUMENT, not "
              "about the page.")

    print("\n    REMEMBER WHAT THIS CAN SETTLE: A14, A15 and A22 are WRITES. "
          "A read moves their PRECONDITION and cannot bank them.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
