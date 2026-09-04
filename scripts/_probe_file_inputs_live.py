"""Does the post composer draw a file input? A LIVE READ, and nothing else.

WHY THIS EXISTS. `_audit/2026-09-04-file-input-survey.md` measured every
committed capture and found exactly one file input, in a DERIVED fixture. Of
the five candidate upload surfaces, the post composer is the only one whose
address is already on the read allowlist and which NOBODY HAS EVER OPENED --
so its row reads "unknown", which is a different answer from "none" and must
not be collapsed into one.

This is the one call that settles it.

WHAT IT DOES: takes the profile lock, opens two allowlisted addresses through
the same read door every read tool uses, and counts. WHAT IT DOES NOT DO: it
does not click, type, select, submit or upload. There is no mutating call in
this file and `readonly.scan_source_for_mutations` is what proves it.

ABSENT IS NOT ZERO, and the distinction decides the answer. "The composer drew
no file input" is a claim about the composer. "The page did not render a
composer" is a claim about the page, and a file-input count of zero taken from
it means nothing at all. So the composer's OWN controls are counted first --
editors and publish controls -- and a zero on those makes the file-input
reading UNKNOWN rather than clean. `dom.read_feed_composer` and
`writes._read_feed_composer` already treat zero-of-either as "a page that had
not arrived"; this uses the same rule rather than inventing a second one.

RUN IT:  venv/Scripts/python.exe scripts/_probe_file_inputs_live.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any

# THE REPO ROOT ON THE PATH, the same way every other probe in this directory
# does it. A script run by filename gets its OWN directory on sys.path, not the
# checkout, so the package is not importable without this line.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import config, dom, profile_lock, readonly  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402

#: Both already on the read allowlist -- asserted below rather than assumed,
#: because "I believe this is allowlisted" is not the same as the door saying
#: so, and this file must not be the place a new address quietly enters.
TARGETS: tuple[tuple[str, str], ...] = (
    ("post composer", "https://www.linkedin.com/preload/sharebox/"),
    ("feed", config.FEED_URL),
)

#: ``--shapes`` prints the aggregated control shapes as well as the counts, and
#: ``--only=<substring>`` narrows the targets. Both exist so a re-run costs one
#: page load rather than two: this opens the operator's real account and every
#: avoidable navigation is one he did not need.
_WANT_SHAPES = "--shapes" in sys.argv
_ONLY = next(
    (arg.split("=", 1)[1] for arg in sys.argv if arg.startswith("--only=")), ""
)


def _fmt(label: str, out: dict[str, Any], composer: dict[str, Any]) -> str:
    lines = [f"--- {label}"]
    lines.append(f"    landed:        {out.get('landed')}")
    lines.append(f"    composer:      editors={composer.get('editors')} "
                 f"publish_controls={composer.get('publish')}")
    reading = out["file_inputs"]
    lines.append(f"    file_inputs:   count={reading['count']} "
                 f"described={reading['described']} "
                 f"undercounted={reading['undercounted']} "
                 f"ambiguous={reading['ambiguous']}")
    for record in reading["inputs"]:
        lines.append(
            f"      - shape={record.get('shape')!r} "
            f"container={record.get('container')} "
            f"disabled={record.get('disabled')} "
            f"name_source={record.get('name_source')}"
        )
    # THE VERDICT, in the vocabulary that keeps absent and zero apart.
    if reading["undercounted"]:
        verdict = "UNKNOWN -- the census was truncated; no count may be read off this"
    elif not composer.get("editors") and not composer.get("publish"):
        verdict = (
            "UNKNOWN -- the composer did not render (0 editors, 0 publish "
            "controls), so a file-input count of zero is a fact about the "
            "page and not about the composer"
        )
    elif reading["count"] == 0:
        verdict = "ZERO -- the composer rendered and draws no file input"
    elif reading["count"] == 1:
        verdict = "ONE -- addressable by count alone, no name needed"
    else:
        verdict = (
            f"{reading['count']} -- ambiguous by count; aiming needs an "
            "in-page name comparison"
        )
    lines.append(f"    VERDICT:       {verdict}")
    return "\n".join(lines)


async def _measure(page: Any, url: str) -> dict[str, Any]:
    """One allowlisted navigation and two reads. No mutation anywhere."""
    readonly.assert_read_url(url)
    landed = await BROWSER.goto(page, url)
    census = await dom.read_surface_census(page)
    return {
        "landed": landed,
        "census": census,
        "file_inputs": await dom.read_file_inputs(page, census=census),
    }


async def _run() -> int:
    targets = [t for t in TARGETS if _ONLY in t[0]] if _ONLY else list(TARGETS)
    for label, url in targets:
        # THE DOOR ANSWERS, not me. If either address is not on the allowlist
        # this stops before a browser is started.
        assert readonly.is_read_url(url), (label, url)

    holder = profile_lock.live_holder()
    if holder is not None:
        print(f"REFUSING: the Chrome profile is locked by pid {holder}. "
              "Nothing was opened.")
        return 2

    profile_lock.acquire()
    try:
        await BROWSER.start()
        async with BROWSER.session() as page:
            from linkedin_server.auth import assert_not_authwall

            reports = []
            for label, url in targets:
                out = await _measure(page, url)
                assert_not_authwall(out["landed"], surface=label)
                counts = out["census"]["counts"]
                composer = {
                    "editors": counts.get("contenteditable"),
                    # The publish control is a BUTTON named by the page. Only
                    # its presence is wanted here, so the census's own button
                    # count is enough and no selector is built.
                    "publish": counts.get("buttons"),
                }
                reports.append(_fmt(label, out, composer))
                print(reports[-1])
                print(f"    page counts:   {counts}")
                # WHY there is no file input is the obvious next question, and
                # a zero on its own does not answer it. The composer's own
                # control SHAPES say whether a media affordance exists that
                # would create one on click -- which is the difference between
                # "this surface cannot upload" and "its input is built on
                # demand". Shapes, never names: the same aggregation the
                # census tool ships, so nothing here is weaker than that.
                if _WANT_SHAPES:
                    from linkedin_server import shape as _shape

                    shapes, _hrefs = _shape.census_aggregate(out["census"]["controls"])
                    print("    control shapes:")
                    for row in shapes:
                        print(f"      {row['count']:>3} x {row['shape']!r} "
                              f"({row['tag']}{'/' + row['role'] if row.get('role') else ''})")
        return 0
    finally:
        await BROWSER.stop()
        profile_lock.release()


def main() -> int:
    return asyncio.run(_run())


if __name__ == "__main__":
    sys.exit(main())
