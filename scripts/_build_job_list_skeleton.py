"""Turn a captured job-LIST page into a skeleton fixture that carries its SHAPE and nothing else.

Kept as the PROVENANCE of ``tests/fixtures/jobs_recommended_skeleton.html``:
it is the exact record of what was measured on the capture and what the
fixture keeps, which is the thing a privacy review needs and cannot get from
the output alone.

WHY A SKELETON, AND WHY NO SANITISATION KEY IS NEEDED. The reader this fixture
exists for -- ``linkedin_server/job_collections.py`` -- reads three attributes
and nothing else: the slot tier ``data-occludable-job-id``, the card tier
``data-job-id``, and the ``job-card-container`` class token. So the fixture
keeps exactly those, in the captured ORDER and the captured TIER STATE, and
drops everything a person, an employer or a place could live in: every text
node, every other attribute, every href, the detail pane, the pagination.
Nothing textual is renamed because nothing textual survives, which is why this
builder -- unlike ``_build_job_fixtures.py`` -- needs no key.

**THE IDS ARE REPLACED, NOT KEPT.** A posting id addresses a public job
advertisement and the reader is allowed to publish one, but a committed fixture
has no business freezing which postings LinkedIn recommended to this account on
one day. Each slot's id becomes ``1000000101 + position``, the same shape the
control fixture uses (ten digits, as measured on every slot), and a hydrated
card carries its own slot's replacement -- so the measured cross-tier equality
survives the replacement.

WHAT IT REFUSES TO BUILD FROM. A capture on which a card's id differs from its
slot's, or on which a slot sits outside ``main``: a skeleton of either would
misrepresent the page it claims to describe, and the reader's scoping and
tier assertions would then be tested against a shape LinkedIn did not draw.

The raw capture is gitignored and is NEVER committed -- it embeds a member urn
in a tracking blob. Re-run this only after re-capturing:

    python scripts/_build_job_list_skeleton.py --capture <path to the capture>

It prints counts only. It never prints a title, an employer, a place or an id.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_CAPTURE = ROOT / "_state" / "cap-jobs-recommended.html"
DEFAULT_OUT = ROOT / "tests" / "fixtures" / "jobs_recommended_skeleton.html"

#: The first synthetic id. Ten digits, clear of every real range this repo has
#: seen, and 100 above the control fixture's run so the two never collide.
FIRST_ID = 1000000101

_SLOT = re.compile(r'<li\b[^>]*\bdata-occludable-job-id="([^"]*)"')
_CARD = re.compile(r'\bdata-job-id="([^"]*)"')
_CONTAINER = re.compile(r'class="[^"]*\bjob-card-container\b[^"]*"')
_STRIP = re.compile(r"<(script|style|svg|noscript|code)\b.*?</\1>", re.S | re.I)


def measure(html: str) -> dict:
    """The capture's list shape: per slot, hydrated or not. Counts only."""
    body = _STRIP.sub("", html)
    found = re.search(r"<main\b.*?</main>", body, re.S)
    if not found:
        raise SystemExit("the capture has no <main>; this builder reads a job "
                         "list inside one and will not guess where else to look")
    main = found.group(0)
    slots = [(m.start(), m.group(1)) for m in _SLOT.finditer(main)]
    everywhere = len(_SLOT.findall(body))
    if everywhere != len(slots):
        raise SystemExit(f"{everywhere - len(slots)} slot(s) sit outside <main>; "
                         "a skeleton of this page would misrepresent it")
    pattern: list[bool] = []
    for index, (start, slot_id) in enumerate(slots):
        end = slots[index + 1][0] if index + 1 < len(slots) else len(main)
        segment = main[start:end]
        card = _CARD.search(segment)
        if card and card.group(1) != slot_id:
            raise SystemExit(f"slot {index}: its card's id differs from the "
                             "slot's; cross-tier equality is what this fixture "
                             "preserves, so it refuses")
        if card and not _CONTAINER.search(segment):
            raise SystemExit(f"slot {index}: a card with no job-card-container "
                             "token; the reader counts that token, so the "
                             "skeleton cannot drop the difference")
        pattern.append(bool(card))
    return {
        "slots": len(slots),
        "hydrated": sum(pattern),
        "pattern": pattern,
        "id_lengths": sorted({len(slot_id) for _s, slot_id in slots}),
    }


def skeleton(shape: dict) -> str:
    """The fixture: the measured tier pattern, synthetic ids, no text at all."""
    items = []
    for index, hydrated in enumerate(shape["pattern"]):
        ident = FIRST_ID + index
        card = (f'<div><div class="job-card-container" data-job-id="{ident}">'
                f'</div></div>') if hydrated else ""
        items.append(f'<li data-occludable-job-id="{ident}">{card}</li>')
    header = (
        "<!--\n"
        "  SKELETON of the recommended job collection, /jobs/collections/recommended/,\n"
        "  built by scripts/_build_job_list_skeleton.py from a live capture that is\n"
        "  gitignored and never committed. It keeps the list's SHAPE and nothing\n"
        "  else: the slot tier and the card tier in the captured order and state,\n"
        "  with synthetic ids. No text, no href, no other attribute survives.\n"
        f"  Measured on the capture: {shape['slots']} slots inside main, "
        f"{shape['hydrated']} hydrated,\n"
        "  every card id equal to its slot id, no slot outside main.\n"
        "-->\n"
    )
    return (header + "<html><body><main><ul>\n" + "\n".join(items)
            + "\n</ul></main></body></html>\n")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--capture", type=pathlib.Path, default=DEFAULT_CAPTURE)
    ap.add_argument("--out", type=pathlib.Path, default=DEFAULT_OUT)
    args = ap.parse_args(argv)
    if not args.capture.is_file():
        raise SystemExit(f"no capture at {args.capture.name}; pass --capture")
    shape = measure(args.capture.read_text(encoding="utf-8", errors="replace"))
    out = skeleton(shape)
    out.encode("ascii")
    args.out.write_text(out, encoding="ascii", newline="\n")
    print(f"slots {shape['slots']}  hydrated {shape['hydrated']}  "
          f"id lengths {shape['id_lengths']}  -> {args.out.name} "
          f"({len(out)} bytes)")
    return 0


if __name__ == "__main__":
    # Guarded: main() WRITES a committed fixture, so importing this module
    # must never rebuild one.
    sys.exit(main())
