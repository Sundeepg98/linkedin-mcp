"""SHOW THE PER-SITE ERROR-URL RULING FAILING ON THE STATE THAT ACTUALLY SHIPPED.

``tests/test_the_error_url_is_ruled_per_site.py`` holds a verdict for every
site that can feed ``ExtractionFailedError.url``. A guard that has only ever
been seen green certifies nothing, so this restores the spelling that shipped
at ``479761e`` -- the twelve ``dom.py`` readers publishing ``_url_of(page)``
and the seven ``server.py`` sites publishing the landed url -- and requires
the guard to convict EVERY ONE of them.

**THE MUTATION IS THE REAL PREVIOUS STATE, NOT A REPRESENTATIVE ONE**, which
is why no argument is needed that it is typical. It is a text substitution
applied to the source IN MEMORY: nothing is written to ``linkedin_server/``
and no file on disk is touched, so this is safe to run while other waves are
editing the tree.

**NO EXTERNAL TOOL IS CONSULTED.** An earlier instrument in this repository
answered an unreachable version-control binary with an empty string and turned
an OUTAGE into an ABSENCE, in the direction that flattered its own thesis
(``test_an_outage_is_never_filed_as_an_absence``). Rebuilding the previous
state by substitution rather than by ``git show`` means there is no outage to
misreport: if a pattern does not match, the count below is short and this
script fails saying so.

Run::

    venv/Scripts/python scripts/_check_the_error_url_ruling_can_fail.py
"""
from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from tests import test_the_error_url_is_ruled_per_site as ruling  # noqa: E402

#: ``(file, before, after, how many)`` -- the repair, run backwards. The counts
#: are DECLARED so a pattern that stops matching makes this script fail rather
#: than quietly plant less than it claims.
PLANTS: tuple[tuple[str, str, str, int], ...] = (
    # The twelve dom readers, all one spelling.
    ("dom.py", "hint=_landing_note(page),", "url=_url_of(page),", 12),
    # The four server sites that publish a local named `url`.
    ("server.py", "url=url,", "url=final_url,", 4),
    # The two that publish the constant named `requested_url`.
    ("server.py", "url=requested_url,", "url=final_url,", 2),
    # And the loop, whose landed twin is `last_url`.
    ("server.py", "url=last_requested_url,", "url=last_url,", 1),
)

#: Every row the plant must convict. The twenty, minus the relay -- which the
#: plant does not touch, because `dom.require_rows` was never the defect and a
#: control that moved it would be measuring its own edit.
MUST_BE_CONVICTED = tuple(
    key
    for key, (verdict, _count) in ruling.DECLARED.items()
    if verdict in (ruling.WITHHELD, ruling.ASKED_FOR)
)


def _sites_for(source: str, filename: str, key: tuple[str, str]) -> list[dict]:
    return [
        site
        for site in ruling.feeder_sites(source, filename)
        if (site["file"], site["function"]) == key
    ]


def main() -> int:
    failures: list[str] = []

    print("the plant restores the spelling that shipped at 479761e\n")

    # ---------------------------------------------------------------- 1
    print("1. THE TREE AS IT STANDS -- every declared row must be GREEN")
    green_sources = {
        name: (ruling.SCANNED / name).read_text(encoding="utf-8")
        for name in ("dom.py", "server.py")
    }
    still_red = []
    for key in sorted(ruling.DECLARED):
        source = green_sources.get(key[0])
        if source is None:
            source = (ruling.SCANNED / key[0]).read_text(encoding="utf-8")
            green_sources[key[0]] = source
        problems = ruling.verdict_violations(key, _sites_for(source, key[0], key))
        if problems:
            still_red.append((key, problems))
    print("   rows checked %d, rows red %d" % (len(ruling.DECLARED), len(still_red)))
    for key, problems in still_red:
        print("   RED %s::%s -- %s" % (key[0], key[1], problems[0][:90]))
    if still_red:
        failures.append(
            "the tree is not green before the plant, so nothing below is "
            "attributable to the plant"
        )
    print()

    # ---------------------------------------------------------------- 2
    print("2. THE PLANT -- substituted in memory, never on disk")
    planted = dict(green_sources)
    for filename, before, after, expected in PLANTS:
        found = planted[filename].count(before)
        planted[filename] = planted[filename].replace(before, after)
        print(
            "   %-10s %-28s -> %-22s replaced %2d (declared %2d)"
            % (filename, before, after, found, expected)
        )
        if found != expected:
            failures.append(
                "%s: planted %d of a declared %d occurrences of %r -- the "
                "previous state was not restored, so a green verdict below "
                "would mean nothing"
                % (filename, found, expected, before)
            )
    print()

    # ---------------------------------------------------------------- 3
    print("3. WHAT THE PLANT DOES TO EACH DECLARED ROW")
    convicted: list[tuple[str, str]] = []
    acquitted: list[tuple[str, str]] = []
    for key in sorted(MUST_BE_CONVICTED):
        problems = ruling.verdict_violations(key, _sites_for(planted[key[0]], key[0], key))
        (convicted if problems else acquitted).append(key)
    print("   rows planted %d" % len(MUST_BE_CONVICTED))
    print("   CONVICTED    %d" % len(convicted))
    print("   ACQUITTED    %d" % len(acquitted))
    for key in acquitted:
        print("   NOT CONVICTED %s::%s" % key)
    if acquitted:
        failures.append(
            "%d row(s) survived the plant: %s. A guard that does not convict "
            "the state it was written against is not guarding it."
            % (len(acquitted), ["%s::%s" % k for k in acquitted])
        )
    print()

    # ---------------------------------------------------------------- 4
    print("4. THE ROWS THE PLANT DOES NOT TOUCH MUST STAY GREEN")
    untouched = [
        key
        for key, (verdict, _c) in ruling.DECLARED.items()
        if verdict in (ruling.PASSTHROUGH, ruling.NO_ADDRESS_IN_SCOPE)
    ]
    wrongly_red = [
        key
        for key in sorted(untouched)
        if ruling.verdict_violations(key, _sites_for(planted[key[0]], key[0], key))
    ]
    print(
        "   untouched rows %d, wrongly red %d"
        % (len(untouched), len(wrongly_red))
    )
    for key in wrongly_red:
        print("   WRONGLY RED %s::%s" % key)
    if wrongly_red:
        failures.append(
            "the plant convicted %d row(s) it does not touch: %s. A control "
            "that convicts everything convicts nothing."
            % (len(wrongly_red), ["%s::%s" % k for k in wrongly_red])
        )
    print()

    # ---------------------------------------------------------------- 5
    # **THE CONTROLS DECIDE WHETHER THIS REPORT IS ALLOWED TO EXIST.** Branched
    # on rather than printed: a control whose result nothing acts on is
    # decoration, and tests/test_probe_controls_are_never_decorative.py exists
    # because a sibling probe computed fourteen of them and returned 0 anyway.
    if failures:
        print(
            "FAIL -- this control did not hold:\n  " + "\n  ".join(failures),
            file=sys.stderr,
        )
        return 1
    print(
        "PASS -- %d rows green on the tree, all %d convicted by the plant, "
        "%d untouched rows unaffected"
        % (len(ruling.DECLARED), len(convicted), len(untouched))
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
