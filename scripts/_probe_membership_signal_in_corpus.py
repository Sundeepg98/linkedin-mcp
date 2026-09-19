"""Is there ANY route in this repository's captured corpus that says whether
he belongs to a group or is registered for an event?

WHY THIS EXISTS. ``GROUPS-SURFACE`` (32 census rows) and ``EVENTS-SURFACE``
(18) both rest on a precondition nobody has established: **if he belongs to
zero groups, twenty-nine of those thirty-two rows are unreachable in principle
for this account.** Two routes to that answer have already been tried and both
are dead -- ``/in/me/details/interests/`` REDIRECTS (measured 2026-09-04, with
two sibling controls), and the profile's own Interests region is not in the
document. Before proposing a THIRD page load, the cheap question is whether
the signal is already sitting in something this project has captured.

THE ANSWER THIS PRINTS IS ONLY WORTH READING BECAUSE OF THE CONTROL.

**The control is ``/company/``, and it is not decoration.** It must be
NON-ZERO somewhere in the corpus, because ``linkedin_followed_companies``
ships and reads exactly that data, and ``manage_pages_following.html`` is a
tracked capture of the surface it reads. A sweep that reports zero groups AND
zero companies has measured its own blindness, not his memberships -- which is
the precise failure this repository has catalogued repeatedly and the reason
every zero below is printed beside a needle that must fire.

**A second control, ``NEEDLE-THAT-CANNOT-MATCH``, runs in the other
direction.** A sweep that finds everything is as useless as one that finds
nothing: if a string nobody has ever written appears, the matcher is wrong
rather than the corpus rich.

NO IDENTITY LEAVES THIS PROBE. It prints counts, file names and needle names.
The needles are LinkedIn's own route words; nothing captured is echoed.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

#: Where captured HTML lives in this repository. Both are swept: the tracked
#: sanitised fixtures survive a clone, the raw ``_audit`` captures do not, and
#: a finding that exists only in the second is a finding with a shelf life.
CORPUS_DIRS = (ROOT / "tests" / "fixtures", ROOT / "_audit")

#: TARGETS -- what a groups or events membership signal looks like in a
#: LinkedIn document. Route words rather than display text, because display
#: text is localised and a route is not.
TARGETS: tuple[tuple[str, str], ...] = (
    ("groups-href", r"linkedin\.com/groups/"),
    ("groups-path", r"/groups/[A-Za-z0-9]"),
    ("groups-urn", r"urn:li:[A-Za-z]*[Gg]roup"),
    ("events-href", r"linkedin\.com/events/"),
    ("events-path", r"/events/[A-Za-z0-9]"),
    ("events-urn", r"urn:li:[A-Za-z]*[Ee]vent"),
)

#: CONTROLS. The first MUST fire somewhere or every zero above is void; the
#: second MUST NOT fire anywhere or the matcher is over-broad.
CONTROL_MUST_FIRE = ("company-href", r"linkedin\.com/company/")
CONTROL_MUST_NOT_FIRE = (
    "needle-that-cannot-match",
    r"zzq-no-such-linkedin-route-zzq",
)


def _documents() -> list[Path]:
    found: list[Path] = []
    for directory in CORPUS_DIRS:
        if not directory.is_dir():
            continue
        found.extend(sorted(p for p in directory.glob("*.html") if p.is_file()))
    return found


def main() -> int:
    documents = _documents()
    if not documents:
        print("NO DOCUMENTS FOUND -- the sweep has nothing to say")
        return 1

    needles = list(TARGETS) + [CONTROL_MUST_FIRE, CONTROL_MUST_NOT_FIRE]
    compiled = {name: re.compile(pattern) for name, pattern in needles}
    totals = {name: 0 for name, _ in needles}
    per_file: dict[str, dict[str, int]] = {}

    total_bytes = 0
    for document in documents:
        text = document.read_text(encoding="utf-8", errors="replace")
        total_bytes += len(text)
        row = {name: len(compiled[name].findall(text)) for name, _ in needles}
        per_file[document.name] = row
        for name in row:
            totals[name] += row[name]

    print("=== CORPUS")
    print(f"    {len(documents)} documents, {total_bytes} characters")
    for directory in CORPUS_DIRS:
        count = len([p for p in documents if p.parent == directory])
        print(f"    {count:3d} from {directory.relative_to(ROOT)}")

    print()
    print("=== PER DOCUMENT -- only rows where SOMETHING matched")
    header = f"{'document':<48}" + "".join(
        f"{name.split('-')[0][:7]:>9}" for name, _ in needles
    )
    print("    " + header)
    for name in sorted(per_file):
        row = per_file[name]
        if not any(row.values()):
            continue
        print(
            "    "
            + f"{name[:47]:<48}"
            + "".join(f"{row[needle]:>9}" for needle, _ in needles)
        )

    print()
    print("=== TOTALS, BY NEEDLE")
    for name, pattern in needles:
        print(f"    {name:<28} {totals[name]:>7}   /{pattern}/")

    print()
    print("=== CONTROLS")
    must_fire = totals[CONTROL_MUST_FIRE[0]]
    must_not_fire = totals[CONTROL_MUST_NOT_FIRE[0]]
    ok_fire = must_fire > 0
    ok_silent = must_not_fire == 0
    print(
        f"    {'MUST FIRE':<22} {CONTROL_MUST_FIRE[0]:<26} "
        f"{must_fire:>6}   {'PASS' if ok_fire else 'FAIL'}"
    )
    print(
        f"    {'MUST STAY SILENT':<22} {CONTROL_MUST_NOT_FIRE[0]:<26} "
        f"{must_not_fire:>6}   {'PASS' if ok_silent else 'FAIL'}"
    )

    target_total = sum(totals[name] for name, _ in TARGETS)
    print()
    print("=== VERDICT")
    if not (ok_fire and ok_silent):
        print(
            "    CONTROLS FAILED. The target counts above are NOT a reading "
            "about his memberships -- they are a reading about this sweep."
        )
        return 1
    print(
        f"    Controls behave: a needle that must match found {must_fire}, "
        f"a needle that cannot match found {must_not_fire}."
    )
    if target_total == 0:
        print(
            "    TARGETS: 0 across the whole corpus. With the controls "
            "behaving, this is a NEGATIVE READING rather than a blind one: "
            "nothing this project has ever captured carries a group or event "
            "signal, so no offline route to the precondition exists."
        )
    else:
        print(
            f"    TARGETS: {target_total} matches. An offline route MAY "
            "exist -- read the per-document rows above before proposing a "
            "page load."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
