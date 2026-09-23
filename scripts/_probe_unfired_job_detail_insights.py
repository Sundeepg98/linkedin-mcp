"""FIRE the six job-posting insight fields that the census carries as UNFIRED.

## WHAT THIS SETTLES, AND WHY IT IS ONE PROBE AND NOT SIX

Six census rows -- ``J 24``, ``J 26``, ``J 27``, ``J 121``, ``J 122`` and
``profile.md K10`` -- all describe fields emitted by ONE reader,
``dom.read_job_insight_panels``, reached through ONE tool,
``linkedin_job_detail``. Every one of them was banked COVERED-UNFIRED on a
SOURCE trace: the field is emitted, the dict is assigned to ``out["insights"]``,
therefore the field reaches a caller. That is a true statement about the tree
and it is not a fire. None of those rows had ever seen the field come back from
a live posting.

This fires the shipped tool against real postings and reports what came back.

## THE DISTINCTION THIS PROBE EXISTS TO PRESERVE

**A FIELD THAT IS PRESENT IS NOT A FIELD THAT WORKS.** ``verified_job`` is
``bool(markers.get("verified"))`` -- a reader with a broken selector returns
``False`` for every posting on earth and looks exactly like a correct reader
over a sample of unverified jobs. So a tally of "present in the dict" would
certify nothing, which is this repository's oldest lesson wearing new clothes.

Therefore every boolean field is reported as a THREE-WAY tally -- how many
postings said True, how many said False, how many did not carry the key at
all -- and the verdict is stated in those terms:

    OBSERVED-BOTH     True on some postings and False on others. The reader
                      discriminates. This is the only tally that proves the
                      field is being READ rather than defaulted.
    OBSERVED-TRUE     True everywhere. Surfaced and populated.
    NEVER-TRUE        False on every posting in the sample. SURFACED BUT
                      UNDISCRIMINATED -- indistinguishable from a dead reader
                      by this run, and reported as such rather than as a pass.
    ABSENT            the key never arrived.

**NEVER-TRUE IS NOT A BANKABLE RESULT AND THIS FILE SAYS SO IN ITS OUTPUT.**

## WHAT LEAVES THIS PROCESS

COUNTS, BOOLEANS AND VERDICTS. No title, no employer, no location, no job id
and no panel text is printed. ``applicant_insights`` and ``company_insights``
are structures full of LinkedIn's prose about a named employer, so they are
reported ONLY as: did it arrive, and how many entries does each sub-part hold.
The raw results are written to ``_state/`` -- gitignored, because the profile
directory rule in ``.gitignore`` covers the whole tree -- so a human can check
this probe's arithmetic without the capture ever being committable.

## THE OBLIGATIONS THIS REPOSITORY PUTS ON A LIVE READ, ALL MET HERE

* A CONTROL, read FIRST and again LAST. An instrument that cannot report
  SERVED would report every posting as unreadable and look authoritative.
  If the control stops serving mid-run the readings are VOID, not data.
* ``dom.read_invitation_badge`` immediately BEFORE and AFTER, which is how
  this repo proves a read did not consume a counter it passed. Unreadable at
  either end reports UNKNOWN, never "nothing was spent".
* IT FIRES NO WRITE. It searches and it reads postings. Nothing is applied
  to, saved, followed or messaged, and ``LINKEDIN_ENABLE_WRITES`` is
  irrelevant to it.
* IT STOPS AT THE FIRST ANOMALY (since 2026-09-23). Any error envelope from a
  shipped tool -- a login or checkpoint landing, a throttled page that drew
  nothing -- ends the run with no further page load, not even the closing
  control. See ``_anomaly``.

Run it as::

    LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224 \\
        ./venv/Scripts/python.exe scripts/_probe_unfired_job_detail_insights.py

The sample size is the first argument, default 10.
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "scripts"))

from linkedin_server import dom, server  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402

#: A known-served admitted address. The control.
CONTROL_URL = "https://www.linkedin.com/jobs/search/?keywords=node.js"

#: Generic, non-identifying search terms. They are literals in this file so
#: that nothing this probe searches for comes from the operator's own saved
#: searches -- one of his spellings is on this repository's denied-terms list.
HARVEST_TERMS = ("node.js", "typescript", "backend engineer")

#: The three boolean insight fields the census rows are about.
BOOLEAN_FIELDS = ("promoted", "verified_job", "responses_managed_off_linkedin")

#: The two structured panels. Reported by SHAPE only, never by content.
PANEL_FIELDS = ("applicant_insights", "company_insights")

#: TOKENS THAT DECIDE J 121 AND J 122, and they are the reason those two rows
#: are not simply "applicant_insights arrived".
#:
#: ``J 121`` is *your ranking percentile vs other applicants* and ``J 122`` is
#: *top skills among applicants, experience/education levels*. A panel that
#: arrives carrying seniority and education splits satisfies HALF of J 122 and
#: NONE of J 121, so a probe that reported only "the panel arrived" would bank
#: both on evidence for neither. Each token is searched for in the panel's own
#: serialised text and only the COUNT of postings carrying it is printed.
PANEL_TOKENS = ("percentile", "rank", "skill", "%")

#: The control label LinkedIn draws over its gated panel. Its PRESENCE is the
#: mechanism behind a missing percentile, so it is counted rather than guessed.
PREMIUM_CONTROL = "Show Premium Insights"


def _verdict(true_n: int, false_n: int, absent_n: int) -> str:
    """The three-way tally reduced to the verdict the census row needs."""
    if true_n and false_n:
        return "OBSERVED-BOTH"
    if true_n and not false_n:
        return "OBSERVED-TRUE"
    if false_n and not true_n:
        return "NEVER-TRUE"
    if absent_n:
        return "ABSENT"
    return "NO-SAMPLE"


def judge_panels(read_ok: int, token_hits: dict, premium_seen: int) -> list:
    """The J 121 / J 122 reading, as lines. PURE, so its branches are testable.

    EXTRACTED FROM `main()` ON PURPOSE. These three arguments decide two census
    rows, and while the logic sat inline the only way to exercise it was to
    drive a browser -- so the branches that matter most could not be shown
    firing at all. A verdict function nobody can test is the shape this
    repository keeps finding at the bottom of its own false claims.

    TWO OF THE THREE BRANCHES EXIST BECAUSE A RATCHET CAUGHT THEM MISSING.
    `tests/test_probe_controls_are_never_decorative.py` flagged `read_ok` and
    `postings_with_premium_control` as computed-but-never-branched. Both
    findings were correct and neither was decorative:

    **`read_ok` IS A PRECONDITION, NOT A STATISTIC.** Every verdict here is
    driven by a token tally, and a tally over ZERO panels is zero for every
    token -- so a run that read nothing would fall into each `else` and print
    NOT DELIVERED, a strong negative claim about LinkedIn derived from nothing
    observed. That is the "zero matched" refusal this repository has been
    burned by twice, wearing a verdict's clothes.

    **A MECHANISM MUST BE OBSERVED BEFORE IT IS NAMED.** The ordinary J 121
    reading blames Premium gating for the missing percentile. That attribution
    is worth something only if the gated control was actually SEEN. With zero
    sightings the percentile is absent AND unexplained -- a different and more
    alarming reading, pointing at a different repair.
    """
    out: list = []
    if not read_ok:
        out.append("    NO POSTING RETURNED AN INSIGHTS DICT. This run")
        out.append("    OBSERVED NOTHING, so it settles nothing. The tallies")
        out.append("    would all read zero, and a zero drawn from an empty")
        out.append("    sample is a fact about this run, never a finding")
        out.append("    about LinkedIn.")
        out.append("    J 121 AND J 122 ARE NOT JUDGED. Re-run before reading.")
        return out

    out.append("    postings whose panel contains each token:")
    for tok in PANEL_TOKENS:
        out.append("        " + tok + ": " + str(token_hits.get(tok, 0))
                   + " of " + str(read_ok))
    out.append("    postings drawing '" + PREMIUM_CONTROL + "': "
               + str(premium_seen) + " of " + str(read_ok))
    out.append("")
    out.append("    J 121 -- your ranking percentile vs other applicants:")
    if token_hits.get("percentile") or token_hits.get("rank"):
        out.append("        a percentile/rank token IS present -- inspect "
                   "before banking")
    elif not premium_seen:
        out.append("        NOT DELIVERED, AND THE USUAL EXPLANATION DOES NOT")
        out.append("        HOLD. No percentile and no rank token appears --")
        out.append("        and NO posting drew the gated control either, so")
        out.append("        the absence CANNOT be attributed to Premium gating")
        out.append("        on this sample. Something else is missing and this")
        out.append("        run does not say what. NOT BANKABLE, and worth a")
        out.append("        look.")
    else:
        out.append("        NOT DELIVERED. No percentile and no rank token")
        out.append("        appears in any panel. The metrics sub-part carries")
        out.append("        applicant COUNTS. The percentile sits behind the")
        out.append("        gated control, drawn on " + str(premium_seen)
                   + " of " + str(read_ok) + " postings here,")
        out.append("        which this reader does not open. NOT BANKABLE.")
    out.append("    J 122 -- top skills among applicants, experience/education "
               "levels:")
    if token_hits.get("skill"):
        out.append("        a skills token IS present -- inspect before banking")
    else:
        out.append("        PARTIAL. seniority and education arrive with")
        out.append("        percentage splits, which is the experience/")
        out.append("        education half. NO skills token appears in any")
        out.append("        panel, so the 'top skills among applicants' half is")
        out.append("        NOT DELIVERED. NOT BANKABLE AS WRITTEN.")
    return out


def _bankable(verdict: str) -> str:
    """Does this verdict support moving a row to COVERED-PROVEN?"""
    if verdict in ("OBSERVED-BOTH", "OBSERVED-TRUE"):
        return "BANKABLE"
    if verdict == "NEVER-TRUE":
        return "NOT BANKABLE -- surfaced but never discriminated in this sample"
    if verdict == "ABSENT":
        return "NOT BANKABLE -- the key never arrived"
    return "NOT BANKABLE -- no sample"


class FireAnomaly(Exception):
    """Raised to STOP EVERY FURTHER PAGE LOAD in this run.

    Carries the server's own error KIND and where the run was, never a
    message: an envelope's ``message`` may quote what the page said, and the
    kind is a token this package chose.
    """

    def __init__(self, kind: str, where: str) -> None:
        self.kind = kind
        self.where = where
        super().__init__(kind + " at " + where)


def _anomaly(out) -> "str | None":
    """The error KIND that must stop the run, or None. PURE, so it is testable.

    ADDED 2026-09-23, because until then an anomaly did not stop this probe.
    A posting whose call came back as an error envelope was counted under
    "errors by type" and the loop went on to the NEXT posting -- so a login
    wall, a checkpoint or a throttled page reached mid-run would have been
    answered with more page loads into the same broken session. The brief
    that wave ran under says to stop at the first anomaly, and so does every
    earlier fire audit.

    ANY ERROR ENVELOPE IS AN ANOMALY HERE, deliberately, and not only
    ``not_authenticated``. A login or checkpoint landing reaches a tool as
    ``not_authenticated`` (``auth.assert_not_authwall``), but a 999 or a
    throttled page that draws nothing reaches it as ``extraction_failed``,
    and the two cannot be told apart from inside the envelope -- no HTTP
    status travels in it. The cost of stopping on a harmless flake is one
    re-run; the cost of continuing into a throttled session lands on the
    account. So the conservative reading wins.

    A REFUSAL IS NOT AN ANOMALY. ``{"refused": ...}`` is a tool answering, and
    the census rows this probe exists for are decided by exactly those
    answers.
    """
    if not isinstance(out, dict):
        return "not_a_dict"
    kind = out.get("error")
    if kind:
        return str(kind)[:40]
    return None


async def _badge(page) -> dict:
    """The structured invitation-badge reading, or a dict carrying an error.

    RETURNS THE DICT RATHER THAN A STRING, and that is a repair of this
    probe's own first version, which reported ``len(str(reading))`` -- the
    character length of the whole dict's repr -- and called a change in it
    "THE BADGE MOVED. Something was spent."

    THAT INSTRUMENT COULD NOT TELL THE TWO CASES APART. ``read_invitation_badge``
    returns ``{links, badge_links, label, error}`` and leaves ``label`` None
    whenever the nav has not hydrated or draws a number of badge links other
    than one. So an UNHYDRATED FIRST READ followed by a HYDRATED SECOND READ
    lengthens the repr by exactly the label, and reads as consumption. Measured
    here 2026-09-20: 60 characters then 89, reported as a spend, on a run that
    opened four job postings and could not have consumed an invitation.
    """
    try:
        reading = await dom.read_invitation_badge(page)
    except Exception as exc:  # noqa: BLE001
        return {"error": type(exc).__name__}
    return reading if isinstance(reading, dict) else {"error": "no reading"}


def _badge_state(reading: dict) -> str:
    """READABLE, or the NAMED reason it is not. Never the label itself."""
    if reading.get("error"):
        return "UNREADABLE (error)"
    if reading.get("badge_links") != 1:
        return "UNREADABLE (badge_links is not exactly 1)"
    if reading.get("label") is None:
        return "UNREADABLE (no label)"
    return "READABLE"


def _consumption(before: dict, after: dict) -> str:
    """Did the counter move? UNKNOWN unless BOTH ends are readable.

    The labels are COMPARED and never printed -- a comparison yields a boolean
    whatever it compared, which is the carve-out both output guards import.
    """
    if _badge_state(before) != "READABLE" or _badge_state(after) != "READABLE":
        return ("UNKNOWN -- one end could not be read, so this says nothing "
                "rather than saying nothing was spent")
    if before.get("label") == after.get("label"):
        return "the badge did not move across this read"
    return "THE BADGE MOVED -- something was spent"


async def _control_serves(page) -> bool:
    """Did the known-served admitted address serve? A BOOLEAN, never its url."""
    await BROWSER.goto(page, CONTROL_URL)
    return await page.locator("div.job-card-container").count() > 0


async def harvest_job_ids(wanted: int) -> list[str]:
    """Collect job ids off ordinary searches, using the SHIPPED search tool.

    The ids come from `linkedin_search_jobs`, so this probe never builds a
    search url of its own and never invents an address.
    """
    found: list[str] = []
    for term in HARVEST_TERMS:
        if len(found) >= wanted:
            break
        result = await server.linkedin_search_jobs(keywords=term, limit=10)
        kind = _anomaly(result)
        if kind:
            raise FireAnomaly(kind, "the harvest search")
        for row in result.get("results") or []:
            jid = str(row.get("job_id") or "").strip()
            if jid and jid not in found:
                found.append(jid)
    return found[:wanted]


async def main() -> int:
    wanted = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    own = None
    tally: dict[str, dict[str, int]] = {
        f: {"true": 0, "false": 0, "absent": 0} for f in BOOLEAN_FIELDS
    }
    panels: dict[str, dict[str, int]] = {
        f: {"arrived": 0, "none": 0, "absent": 0} for f in PANEL_FIELDS
    }
    sub_counts: dict[str, int] = {"metrics": 0, "seniority": 0, "education": 0}
    #: J 121 and J 122 name SPECIFIC sub-parts, and a populated
    #: `applicant_insights` does not prove either of them arrived. These are
    #: CONTAINMENT TESTS over the panel -- a comparison, which yields a boolean
    #: whatever it compared -- and only the TALLY is printed.
    token_hits: dict[str, int] = {t: 0 for t in PANEL_TOKENS}
    postings_with_premium_control = 0
    raw: list[dict] = []
    errors: dict[str, int] = {}
    read_ok = 0

    try:
        # PHASE 1 -- OUR OWN SESSION, HELD ONLY FOR THE CONTROL AND THE BADGE.
        #
        # THE SESSION IS RELEASED BEFORE ANY SHIPPED TOOL IS CALLED, AND THAT
        # IS NOT TIDINESS. `BROWSER.session()` holds a SINGLE-FLIGHT LOCK for
        # the whole of its body, and every shipped tool opens a session of its
        # own. Calling one from inside our session DEADLOCKS -- measured here
        # 2026-09-20, twice, as a silent hang that looks exactly like a slow
        # page. Anything that fires a shipped tool must own no session at the
        # moment it does so.
        print("### CONTROL, before anything")
        async with BROWSER.session() as page:
            own = page
            first_control = await _control_serves(page)
            print("    control serves: " + str(first_control))
            badge_before = await _badge(page)
            print("### invitation badge BEFORE: " + _badge_state(badge_before)
                  + "  (mynetwork links=" + str(badge_before.get("links"))
                  + ", badge links=" + str(badge_before.get("badge_links")) + ")")
        own = None
        if not first_control:
            print("    THE CONTROL DID NOT SERVE. This run is VOID -- an")
            print("    instrument that cannot read a served page would")
            print("    report every posting as unreadable. Stopping.")
            return 1

        # PHASE 2 -- NO SESSION HELD. The shipped tools each take their own,
        # which is exactly how an MCP client reaches them.
        print("\n### HARVEST job ids from ordinary searches")
        ids = await harvest_job_ids(wanted)
        print("    distinct job ids harvested: " + str(len(ids)))
        if not ids:
            print("    NOTHING TO FIRE AT. Stopping.")
            return 1

        print("\n### FIRE linkedin_job_detail on each")
        for n, jid in enumerate(ids, 1):
            try:
                out = await server.linkedin_job_detail(jid)
            except Exception as exc:  # noqa: BLE001
                # A tool that RAISES has escaped its own error envelope, which
                # is itself an anomaly: stop rather than count it and go on.
                raise FireAnomaly(type(exc).__name__,
                                  "posting " + str(n)) from None
            kind = _anomaly(out)
            if kind:
                raise FireAnomaly(kind, "posting " + str(n))
            if out.get("insights_error"):
                name = "insights_error:" + str(out.get("insights_error"))
                errors[name] = errors.get(name, 0) + 1
            ins = out.get("insights")
            if not isinstance(ins, dict):
                print("    posting " + str(n) + ": no insights dict")
                for f in BOOLEAN_FIELDS:
                    tally[f]["absent"] += 1
                for f in PANEL_FIELDS:
                    panels[f]["absent"] += 1
                continue
            read_ok += 1
            raw.append({"insights": ins})
            for f in BOOLEAN_FIELDS:
                if f not in ins:
                    tally[f]["absent"] += 1
                elif ins[f] is True:
                    tally[f]["true"] += 1
                else:
                    tally[f]["false"] += 1
            for f in PANEL_FIELDS:
                if f not in ins:
                    panels[f]["absent"] += 1
                elif ins[f] is None:
                    panels[f]["none"] += 1
                else:
                    panels[f]["arrived"] += 1
            ai = ins.get("applicant_insights")
            if isinstance(ai, dict):
                for part in ("metrics", "seniority", "education"):
                    val = ai.get(part)
                    if val:
                        sub_counts[part] += len(val)
                # CONTAINMENT over the panel's own serialisation. A comparison,
                # so no panel text reaches the output -- only the tally does.
                panel_text = json.dumps(ai, default=str).lower()
                for tok in PANEL_TOKENS:
                    if tok in panel_text:
                        token_hits[tok] += 1
            behind = ins.get("more_behind_a_control") or []
            if PREMIUM_CONTROL in behind:
                postings_with_premium_control += 1
            # A per-posting line of BOOLEANS, so a long run shows movement.
            print("    posting " + str(n) + ": insights ok; keys="
                  + str(len(ins)))

        # PHASE 3 -- OUR SESSION AGAIN, for the closing readings.
        async with BROWSER.session() as page:
            own = page
            badge_after = await _badge(page)
            print("\n### invitation badge AFTER: " + _badge_state(badge_after)
                  + "  (mynetwork links=" + str(badge_after.get("links"))
                  + ", badge links=" + str(badge_after.get("badge_links")) + ")")
            print("    CONSUMPTION: " + _consumption(badge_before, badge_after))

            print("\n### CONTROL AGAIN, at the end")
            last_control = await _control_serves(page)
            print("    control serves: " + str(last_control))
        own = None
        if not last_control:
            print("    THE CONTROL STOPPED SERVING mid-session. Treat every")
            print("    reading above as VOID rather than as data.")
            return 1
    except FireAnomaly as stop:
        # NO FURTHER PAGE LOAD OF ANY KIND -- not even the closing control,
        # which would be one more navigation into the session that just
        # misbehaved. The `finally` below closes our own tab and nothing else.
        print("\n### ANOMALY: " + stop.kind + " at " + stop.where + ".")
        print("    EVERY FURTHER FIRE WAS STOPPED. This run is VOID and banks")
        print("    nothing; the kind above is the server's own error token.")
        return 1
    except Exception as error:  # noqa: BLE001
        name = type(error).__name__
        print("\nRUN ABORTED: " + name)
        if "ProfileLocked" in name:
            print("    The Chrome profile is held by another process. This is")
            print("    the cross-process guard working, not a defect.")
        else:
            print("    " + str(error)[:300])
        return 1
    finally:
        # CLOSE OUR TAB, THEN DROP THE CDP CONNECTION.
        #
        # `BROWSER.stop()` alone would already close it -- its teardown closes
        # the tab this process opened and leaves the operator's Chrome
        # serving. The page is closed EXPLICITLY FIRST anyway, for two
        # reasons. It is the idiom the rest of this package uses and the one
        # `tests/test_a_probe_closes_its_own_tab.py` recognises, and that test
        # is a RATCHET: 39 of 43 session-opening scripts leak a tab per run,
        # the count may only go down, and a probe that cleans up by a route
        # the detector cannot see would have pushed the pin UP while actually
        # being clean. Leaking is not untidiness here -- `connect_over_cdp`
        # enumerates every target on attach, and this wave's own attach took
        # 93 seconds against 56 targets and failed outright at the 15s default.
        #
        # THE PAGE, NEVER THE CONTEXT. In attach mode the context is his
        # signed-in browser; closing it closes his window.
        try:
            own = getattr(BROWSER, "_own_page", None)
            if own is not None and not own.is_closed():
                page = own
                await page.close()
        except Exception as exc:  # noqa: BLE001 - shutdown noise only
            print("    closing our tab raised " + type(exc).__name__)
        try:
            await BROWSER.stop()
        except Exception as exc:  # noqa: BLE001 - shutdown noise only
            print("    cleanup raised " + type(exc).__name__)

    print("\n" + "=" * 68)
    print("### RESULT: postings whose insights dict arrived: " + str(read_ok))
    if errors:
        print("### errors by type:")
        for name in sorted(errors):
            print("    " + name + ": " + str(errors[name]))

    print("\n### THE THREE BOOLEAN FIELDS (census J 24, J 26, J 27, P K10)")
    for f in BOOLEAN_FIELDS:
        t, fa, ab = tally[f]["true"], tally[f]["false"], tally[f]["absent"]
        v = _verdict(t, fa, ab)
        print("    " + f)
        print("        true=" + str(t) + "  false=" + str(fa)
              + "  absent=" + str(ab) + "  -> " + v)
        print("        " + _bankable(v))

    print("\n### THE TWO PANELS (census J 121, J 122) -- shape only")
    for f in PANEL_FIELDS:
        a, n, ab = panels[f]["arrived"], panels[f]["none"], panels[f]["absent"]
        v = "OBSERVED-TRUE" if a else ("NEVER-TRUE" if n else "ABSENT")
        print("    " + f + ": arrived=" + str(a) + "  none=" + str(n)
              + "  absent=" + str(ab) + "  -> " + v)
        print("        " + _bankable(v))
    print("    applicant_insights sub-entry totals across the sample:")
    for part in ("metrics", "seniority", "education"):
        print("        " + part + ": " + str(sub_counts[part]) + " entries")

    print("\n### WHAT THE PANEL ACTUALLY CARRIES (decides J 121 and J 122)")
    # JOINED RATHER THAN LOOPED, deliberately. A `for line in ...: print(line)`
    # binds a name that is only ever printed, which the decorative-control
    # detector reports as a never-branched reading. It is an iteration
    # variable and not a control, but the cheapest honest answer to a detector
    # is to stop creating the binding rather than to argue about it in a
    # baseline file.
    print("\n".join(judge_panels(read_ok, token_hits,
                                 postings_with_premium_control)))

    state = _ROOT / "_state"
    state.mkdir(exist_ok=True)
    dest = state / "unfired-job-detail-insights-raw.json"
    dest.write_text(json.dumps(raw, indent=2, default=str), encoding="utf-8")
    print("\n### RAW capture written under _state/ (gitignored, never committed)")
    print("    entries: " + str(len(raw)))

    # THE EXIT CODE HAS TO MEAN SOMETHING, AND UNTIL NOW IT DID NOT.
    #
    # This probe returned 0 whatever it saw -- including a run that read no
    # panels at all, whose verdicts are drawn from an empty sample. Any caller
    # that checked the exit status was being told "clean" by a run that
    # settled nothing. These two branches are placed AFTER the raw capture on
    # purpose, so a void run still leaves its evidence on disk to diagnose.
    #
    # Both conditions were surfaced by
    # `tests/test_probe_controls_are_never_decorative.py`, which flagged the
    # two counters as computed-but-never-branched. The detector was right
    # twice over: not only did nothing branch on them, nothing SHOULD have
    # been passing silently either.
    if not read_ok:
        print("\n### EXIT 1: no posting returned an insights dict. This run")
        print("    observed nothing and its verdicts are not readings.")
        return 1
    if not postings_with_premium_control:
        print("\n### EXIT 1: the gated control was never drawn in this sample,")
        print("    so a missing percentile CANNOT be attributed to Premium")
        print("    gating. The J 121 reading needs a human before it is used.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
