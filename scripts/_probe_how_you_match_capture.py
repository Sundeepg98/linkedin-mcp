"""CAPTURE THE JOB-DETAIL PAGE SO SOMEBODY ELSE CAN SETTLE SIX ROWS ON EVIDENCE.

`J 110` and `J 116`-`J 120` -- the *How you match* panel's top-applicant flag,
the skills associated with a job, the viewer's matching skills, the skills
missing from the profile, and the additional skills among applicants -- are
filed as a HYPOTHESIS, not a finding. They are held to be parser-only at
boundary 0, which is a claim that *a reader would find something there*. **No
capture of that panel exists in this repository, so nobody has ever checked.**

This takes the capture. **IT BUILDS NO READER AND MOVES NO ROW.** Deciding what
is in the panel is the next wave's job and it needs the bytes first; a probe
that both captures the evidence and rules on it is the same wave marking its
own work.

## WHY IT CAPTURES TWICE PER POSTING, AND WHERE THAT CAME FROM

Measured on the people-search surface hours before this file was written
(`_audit/2026-09-21-the-fourteen-fired.md` section 4b): the shipped
people-search tool read a page that had drawn **45 of its 83 controls** and
reported every filter as zero, because it reads on the navigation settle and
that page fills in afterwards. **A single capture is a reading with a
timestamp**, and a capture taken on the settle can be a capture of a shell --
which a later wave would then parse, find nothing in, and conclude the panel
does not exist.

So each posting is captured TWICE, seconds apart, and **both are kept**. The
byte lengths are printed so the difference is visible without opening anything.

**THE FIRST RUN IMMEDIATELY REFUTED THE ASSUMPTION THIS PARAGRAPH ORIGINALLY
MADE**, which is worth leaving in the file. It said a difference meant the page
was still drawing, so the later capture was the one to parse. Measured on three
postings: every one SHRANK, and hugely -- 860,705 to 208,904 bytes, 858,838 to
497,740, 831,707 to 178,177. That is not a page filling in; it is a served
document being replaced by a lighter client-rendered one. **The panel may live
in either capture**, so this probe keeps both and names neither. A capture tool
that had quietly kept "the later one" would have thrown away the larger
document on a guess, and the wave that parsed the survivor and found nothing
would have concluded the panel does not exist.

**IT DOES NOT WAIT FOR THE PANEL.** Waiting for a named element means choosing a
selector, and choosing a selector is building the reader this file is forbidden
to build -- and it would bias the capture toward the shape the chooser expected.
Two clock-separated captures are the honest instrument for a page nobody has
looked at yet.

## WHAT IT MAY NOT DO, AND THE REASON IS NOT A FORMALITY

**A JOB POSTING IS A THIRD PARTY.** The captured HTML holds employer names,
recruiter names, locations and the viewer's own profile signals. Therefore:

* **CAPTURES GO TO GITIGNORED `_state/` AND NOWHERE ELSE.** They are deliberately
  NOT reachable from a clone. That is not an oversight to be repaired later by
  committing them -- a raw capture of this surface may never be committed, and a
  later wave settles these rows on THIS box or retakes the capture on its own.
* **NOTHING FROM THE PAGE IS PRINTED.** Not a title, not an employer, not a job
  id, not a url, not an exception message -- only its type. Postings are
  numbered by position in this run; the id-to-file mapping is written INSIDE the
  gitignored directory, never to the console, because a job id names an
  employer's posting.
* **NO TOKEN TEST, NO SEARCH, NO COUNT OF ANYTHING INSIDE THE HTML.** Any of
  those is a reader by another name and would let this wave smuggle a verdict
  into a capture task.

## BOUNDS

Reads only. Ids come from the SHIPPED search tool, so this file invents no
search address. Each posting is opened at `/jobs/view/<id>/`, the shape
`readonly` admits, and `assert_read_url` is called on it before navigating.
Nothing is pressed, filled, scrolled or applied to. Attach mode only, so it can
never start a second Chrome on the persistent profile, and it closes its own
tab.

USAGE::

    set LINKEDIN_CDP_ATTACH=1
    ./venv/Scripts/python.exe scripts/_probe_how_you_match_capture.py
    ./venv/Scripts/python.exe scripts/_probe_how_you_match_capture.py --postings 5
"""

from __future__ import annotations

import argparse
import asyncio
import json
import pathlib
import sys
import time

REPO = pathlib.Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from linkedin_server import config  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import BASE_URL  # noqa: E402
from linkedin_server.readonly import assert_read_url  # noqa: E402

#: Between the two captures of one posting. Same reasoning, and the same
#: number, as the people-search probe's settle gap.
SECOND_CAPTURE_GAP_S = 6.0

#: Ordinary search terms, in this repository's own stack vocabulary. They are
#: a way to reach SOME postings, not a sample of anything, and no finding here
#: depends on which postings came back.
HARVEST_TERMS = ("node.js", "typescript", "backend engineer")


def say(line: str = "") -> None:
    print(line, flush=True)


async def harvest_ids(wanted: int) -> list[str]:
    """Job ids off ordinary searches, through the SHIPPED search tool.

    Going through the tool is what keeps this file from inventing a search
    address. It holds NO session while it does so: the tool opens one of its
    own, and `BROWSER.session()` takes a single-flight lock for the whole of
    its body, so calling a tool from inside a session deadlocks.
    """
    from linkedin_server import server

    found: list[str] = []
    for term in HARVEST_TERMS:
        if len(found) >= wanted:
            break
        result = await server.linkedin_search_jobs(keywords=term, limit=10)
        for row in result.get("results") or []:
            jid = str(row.get("job_id") or "").strip()
            if jid and jid not in found:
                found.append(jid)
    return found[:wanted]


async def capture_one(page, job_id: str, index: int, out_dir: pathlib.Path) -> dict:
    """Two captures of one posting. Returns SIZES, never content.

    On a navigation failure it returns a record whose `loaded` is False and
    whose `error_type` NAMES the exception class. It does not return an empty
    reading: a zero-byte capture and a failed navigation are the same number
    and different findings, and filing the outage as an absence is how a later
    wave concludes the panel is not there.
    """
    url = f"{BASE_URL}/jobs/view/{job_id}/"
    assert_read_url(url)
    await BROWSER.wait_for_rate_slot()
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=45_000)
    except Exception as exc:  # noqa: BLE001 - type only, never the message
        return {
            "index": index,
            "loaded": False,
            "error_type": type(exc).__name__,
            "bytes": [],
        }

    sizes: list[int] = []
    for pass_number in (1, 2):
        if pass_number == 2:
            await asyncio.sleep(SECOND_CAPTURE_GAP_S)
        html = await page.content()
        target = out_dir / f"posting-{index:02d}-capture-{pass_number}.html"
        target.write_text(html, encoding="utf-8")
        sizes.append(len(html))
    return {"index": index, "loaded": True, "error_type": "", "bytes": sizes}


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--postings", type=int, default=3)
    parser.add_argument("--out", default=str(REPO / "_state" / "how-you-match"))
    args = parser.parse_args()

    if not config.CDP_ATTACH:
        say("REFUSING: LINKEDIN_CDP_ATTACH is not set. This probe attaches only.")
        say("Launching a second Chrome on the persistent profile costs the")
        say("signed-in session, and only the operator can put it back.")
        return 2

    out_dir = pathlib.Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    say(f"captures go under {out_dir.parent.name}/{out_dir.name}/ (gitignored)")
    say()

    try:
        await BROWSER.start()
    except Exception as exc:  # noqa: BLE001 - type only
        say(f"COULD NOT ATTACH: {type(exc).__name__}")
        return 2

    tab = None
    records: list[dict] = []
    ids: list[str] = []
    try:
        # NO SESSION HELD -- the shipped tool opens its own. See harvest_ids.
        ids = await harvest_ids(args.postings)
        say(f"postings harvested: {len(ids)}")
        if not ids:
            say("NOTHING TO CAPTURE. The search returned no ids, which is a")
            say("finding about the session or the search, not about the panel.")
            return 1
        say()

        async with BROWSER.session() as page:
            tab = page
            for index, job_id in enumerate(ids, start=1):
                record = await capture_one(page, job_id, index, out_dir)
                records.append(record)
                if not record["loaded"]:
                    say(f"  posting {index:02d}  LOAD FAILED "
                        f"({record['error_type']})")
                    continue
                first, second = record["bytes"]
                drift = second - first
                say(f"  posting {index:02d}  captured twice: {first} then "
                    f"{second} bytes  (drift {drift:+d})")
    except Exception as exc:  # noqa: BLE001 - type only
        say(f"PROBE FAILED: {type(exc).__name__}")
        return 1
    finally:
        if tab is not None and not tab.is_closed():
            await tab.close()
        await BROWSER.stop()

    # THE MAPPING LIVES BESIDE THE CAPTURES AND IS NEVER PRINTED. A job id
    # names an employer's posting, so it belongs in the gitignored directory
    # with the bytes it describes and nowhere else.
    manifest = {
        "taken_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "second_capture_gap_s": SECOND_CAPTURE_GAP_S,
        "postings": [
            {**record, "job_id": ids[record["index"] - 1]} for record in records
        ],
        "what_this_is_for": (
            "J 110 and J 116-J 120 are a hypothesis: parser-only at boundary 0, "
            "with no capture to check it against. These are the bytes. Nothing "
            "in this run parsed them and no census row was moved."
        ),
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
    )

    loaded = sum(1 for record in records if record["loaded"])
    differing = [
        record
        for record in records
        if record["loaded"] and record["bytes"][1] != record["bytes"][0]
    ]
    shrank = sum(1 for r in differing if r["bytes"][1] < r["bytes"][0])
    grew = sum(1 for r in differing if r["bytes"][1] > r["bytes"][0])
    say()
    say(f"POSTINGS LOADED        : {loaded} of {len(ids)}")
    say(f"CAPTURES THAT DIFFER   : {len(differing)} of {loaded}"
        f"   (shrank {shrank}, grew {grew})")
    say()
    say("**WHICH CAPTURE TO PARSE IS NOT DECIDED HERE, AND A SHRINK IS WHY.**")
    say("A page that GREW between captures was still drawing, and the later")
    say("capture is the fuller one. A page that SHRANK did something else --")
    say("the served document was replaced by a lighter client-rendered one --")
    say("and the panel may live in EITHER. Both captures are kept per posting")
    say("precisely because this probe cannot tell, and guessing would hand the")
    say("next wave a parse of the wrong bytes dressed as an instruction.")
    say()
    say("NO ROW WAS MOVED AND NOTHING WAS PARSED. J 110 and J 116-J 120 remain")
    say("a hypothesis; what changed is that the evidence now exists.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
