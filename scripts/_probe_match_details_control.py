"""Is "How you match" a COLLAPSED PANEL or a link to something generated?

`MATCH-DETAILS-COLLAPSED`, rows `J 116 117 118 119 120` -- the top-applicant
flag, the skills associated with the job, the profile skills that match, the
skills missing, and the extra skills other applicants have. Section 6 of
`_audit/2026-09-03-linkedin-gap-blockers.md` filed all five as "present,
COLLAPSED behind Show match details", queued DECIDE on the premise that
"pressing a disclosure control is a different permission from reading a
render".

**AMENDMENT A13 MEASURED THAT PREMISE FALSE, ON ONE UNSANITISED CAPTURE.**
`Show match details` is an ``<a href>`` inside an ``<li>``, one of three
anchors sharing a path (`/preload/guideOverlay/`) and ten parameter names,
whose sibling labels are `Create cover letter` and `Help me stand out`. From
that it DERIVED -- explicitly not measured -- that pressing it invokes a
generation product rather than expanding a region already on the page.

THIS FILE DOES TWO THINGS A13 DID NOT.

**1. IT TAKES THE READING LIVE, TODAY.** A13's structure came from a capture.
A capture is a photograph of a page LinkedIn has shipped over since, and this
repository has already been bitten by a conclusion resting on a stale
artefact. Everything below is read off a posting loaded in this session.

**2. IT USES THE DISCRIMINATOR A13 LEFT ON THE TABLE, and it turns a DERIVED
claim into a measured one.** A disclosure control that expands a region
already in the document must SAY SO to a screen reader: ARIA requires
``aria-expanded``, and ``aria-controls`` names the region it governs. A link
that navigates to something generated has neither, because there is no region.

    a collapsed panel   ->  aria-expanded present, and a region to control
    a generated overlay ->  neither, and no region anywhere in the DOM

So the question "is the panel collapsed or absent" is answerable WITHOUT
pressing anything, from attributes the page must carry if the panel exists.
**That matters because pressing it is the thing nobody has ruled on.** A
measurement that needs the disputed action to settle the dispute is no use;
this one needs only a read the server already performs.

=============================================================================
THE CONTROL, AND IT MUST FIRE OR NOTHING BELOW IS A READING
=============================================================================

Every needle here is expected to read ZERO. **A probe whose every expected
answer is zero is indistinguishable from a probe that cannot see**, and this
repository has the scar: a tabbed category read zero because nobody pressed
its tab, and the zero was a fact about the instrument.

So the run carries needles that MUST be non-zero on a job posting:

    Show match details     A13 measured this present -- 3 anchors
    Create cover letter    its sibling
    Help me stand out      its sibling

If those read 0, the reader is blind or the page did not settle, and the run
reports NO VERDICT rather than a comfortable pile of zeros. A13's own
1/1/0 control is the model and this is the same instrument pointed at the
question one step further on.

WHAT IS PRINTED: counts, tag names, attribute names, and LinkedIn's own
control labels -- which are generic product words carrying no identity. No
job id, no employer, no title, no url, no href value. The posting is supplied
by the environment so that not even an id lives in this file.

Run::

    LINKEDIN_PROBE_JOB_ID=<id> LINKEDIN_CDP_ATTACH=1 LINKEDIN_CDP_PORT=9224 \
        ./venv/Scripts/python.exe scripts/_probe_match_details_control.py

Writes ``_audit/_scratch/_probe-match-details.txt``.
"""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import dom  # noqa: E402
from linkedin_server.browser import BROWSER  # noqa: E402

#: **THE POSTING IS SUPPLIED BY THE ENVIRONMENT.** A job id is not an identity
#: and this repository already carries one in a tracked probe -- but a posting
#: expires, and a probe pinned to a dead id reports a confident zero on a page
#: that never loaded, which is the exact failure this file exists to avoid.
JOB_ID = os.environ.get("LINKEDIN_PROBE_JOB_ID", "").strip()

#: **MUST BE NON-ZERO. These are the calibration and not the question.**
#: A13 measured all three present on an unsanitised capture, as the `query`
#: parameter of three anchors sharing one path.
CONTROL_NEEDLES: tuple[str, ...] = (
    "Show match details",
    "Create cover letter",
    "Help me stand out",
)

#: **EXPECTED ZERO. These are the five rows.** Each is a phrase LinkedIn's own
#: Help Centre uses for the panel the census says is collapsed here.
TARGET_NEEDLES: tuple[str, ...] = (
    "How you match",
    "Top applicant",
    "top applicant",
    "Skills associated with the job",
    "skills associated with",
    "skills match your profile",
    "Skills you have",
    "Skills missing",
    "missing from your profile",
    "Add skill",
)

#: The attribute that a genuine disclosure control cannot do without.
DISCLOSURE_ATTRIBUTES: tuple[str, ...] = (
    "aria-expanded",
    "aria-controls",
    "aria-haspopup",
)

OUT_PATH = (
    Path(__file__).resolve().parents[1]
    / "_audit"
    / "_scratch"
    / "_probe-match-details.txt"
)

#: Reads the shape of every element whose accessible text carries one of the
#: control labels. TAG NAMES AND ATTRIBUTE NAMES ONLY -- never an href value,
#: never a parameter value, never any other text on the page.
SHAPE_JS = """
(cfg) => {
  const out = [];
  const wanted = cfg.labels;
  const attrs = cfg.attrs;
  const all = document.querySelectorAll('a, button, [role="button"]');
  for (const el of all) {
    const text = (el.innerText || el.getAttribute('aria-label') || '').trim();
    let hit = null;
    for (const label of wanted) {
      if (text.indexOf(label) !== -1) { hit = label; break; }
    }
    if (!hit) continue;
    const present = {};
    for (const a of attrs) { present[a] = el.hasAttribute(a); }
    let href = el.getAttribute('href') || '';
    // THE PATH ONLY, and only whether it matches a shape we name. No value
    // of any query parameter is read, and the href itself never leaves here.
    let pathShape = 'none';
    if (href) {
      try {
        const u = new URL(href, location.origin);
        pathShape = u.pathname.indexOf('/preload/guideOverlay/') !== -1
          ? 'preload_guide_overlay'
          : 'other_path';
      } catch (e) { pathShape = 'unparseable'; }
    }
    out.push({
      label: hit,
      tag: el.tagName.toLowerCase(),
      hasHref: !!href,
      pathShape: pathShape,
      attrs: present
    });
  }
  return out;
}
"""


def _count(haystack: str, needle: str) -> int:
    return str(haystack or "").count(needle)


async def main() -> None:
    lines: list = []

    def emit(text: str = "") -> None:
        print(text)
        lines.append(text)

    emit("=== IS 'How you match' A COLLAPSED PANEL, OR A LINK TO A GENERATION?")
    emit("    one live posting, nothing pressed, nothing scrolled")
    emit("    counts, tag names and attribute names only")
    emit()

    if not (len(JOB_ID) >= 6 and JOB_ID.isdigit()):
        emit("    NO POSTING SUPPLIED. Set LINKEDIN_PROBE_JOB_ID to a numeric")
        emit("    posting id. NOTHING WAS MEASURED -- and that is reported as a")
        emit("    refusal rather than as a page full of zeros, which is the")
        emit("    whole point of this file.")
        _write(lines)
        return

    url = "https://www.linkedin.com/jobs/view/" + JOB_ID + "/"
    control_visible: dict = {}
    control_html: dict = {}
    target_visible: dict = {}
    target_html: dict = {}
    shapes: list = []
    html_len = -1
    text_len = -1
    served = False

    try:
        await BROWSER.start()
    except Exception as exc:
        emit("    COULD NOT START THE BROWSER: %s: %s"
             % (type(exc).__name__, str(exc)[:300]))
        _write(lines)
        return

    try:
        async with BROWSER.session() as page:
            landed_url = await BROWSER.goto(page, url)
            # Comparisons against literals only. Booleans leave this scope.
            served = "/jobs/view/" in landed_url
            walled = "/authwall" in landed_url or "/login" in landed_url
            emit("    still on /jobs/view/: %s" % ("YES" if served else "NO"))
            emit("    auth wall: %s" % ("YES" if walled else "no"))
            if walled or not served:
                emit("    NOT SERVED. Nothing measured.")
            else:
                # THE READINESS WAIT FIRST, for the reason dom.py already
                # argues about this exact surface: reading before the
                # description arrives measures a page that had not finished.
                try:
                    await dom.wait_for_job_description(page)
                except Exception as exc:
                    emit("    readiness wait raised %s (continuing)"
                         % type(exc).__name__)

                html = await page.content()
                text = await dom.read_main_text(page)
                html_len = len(html or "")
                text_len = len(text or "")
                for needle in CONTROL_NEEDLES:
                    control_visible[needle] = _count(text, needle)
                    control_html[needle] = _count(html, needle)
                for needle in TARGET_NEEDLES:
                    target_visible[needle] = _count(text, needle)
                    target_html[needle] = _count(html, needle)
                try:
                    shapes = await page.evaluate(  # readonly-ok
                        SHAPE_JS,
                        {"labels": list(CONTROL_NEEDLES),
                         "attrs": list(DISCLOSURE_ATTRIBUTES)},
                    )
                except Exception as exc:
                    emit("    SHAPE READ FAILED: %s" % type(exc).__name__)
    except Exception as exc:
        emit("    THE RUN RAISED: %s (message withheld)" % type(exc).__name__)
    finally:
        await BROWSER.stop()

    emit()
    emit("    page: %d chars of html, %d chars of visible main text"
         % (html_len, text_len))
    emit()
    emit("=== THE CONTROL -- MUST BE NON-ZERO OR THERE IS NO VERDICT")
    emit("    %-28s %8s %8s" % ("needle", "visible", "html"))
    for needle in CONTROL_NEEDLES:
        emit("    %-28s %8s %8s"
             % (needle, control_visible.get(needle, "n/a"),
                control_html.get(needle, "n/a")))
    control_fired = any(control_html.get(n, 0) for n in CONTROL_NEEDLES)
    emit()
    if not control_fired:
        emit("    ***  THE CONTROL DID NOT FIRE. Not one of the three labels")
        emit("    ***  A13 measured on a capture is in this page's html. So")
        emit("    ***  this reader cannot see the anchor family at all, and")
        emit("    ***  EVERY ZERO BELOW IS A FACT ABOUT THE INSTRUMENT.")
        emit("    ***  NO VERDICT. Re-take before concluding anything.")
    else:
        emit("    the control fired. Zeros below are readable.")

    emit()
    emit("=== THE FIVE ROWS -- expected zero, and now it means something")
    emit("    %-34s %8s %8s" % ("needle", "visible", "html"))
    for needle in TARGET_NEEDLES:
        emit("    %-34s %8s %8s"
             % (needle, target_visible.get(needle, "n/a"),
                target_html.get(needle, "n/a")))

    emit()
    emit("=== THE DISCRIMINATOR: does the control claim to expand anything?")
    if not shapes:
        emit("    no element carrying a control label was found by the shape")
        emit("    read. That disagrees with the needle counts above if those")
        emit("    were non-zero -- report it, do not average it.")
    for row in shapes:
        emit("    label %-22s tag <%s>  href=%s  path=%s"
             % (row.get("label"), row.get("tag"),
                "yes" if row.get("hasHref") else "no", row.get("pathShape")))
        present = row.get("attrs") or {}
        emit("        %s"
             % ", ".join("%s=%s" % (a, "PRESENT" if present.get(a) else "absent")
                         for a in DISCLOSURE_ATTRIBUTES))

    emit()
    emit("=== VERDICT")
    if not control_fired:
        emit("    NO VERDICT -- the control did not fire.")
    else:
        any_disclosure = any(
            (row.get("attrs") or {}).get(a)
            for row in shapes for a in DISCLOSURE_ATTRIBUTES
        )
        anchors = [r for r in shapes if r.get("tag") == "a"]
        overlay = [r for r in shapes if r.get("pathShape") == "preload_guide_overlay"]
        target_total = sum(target_html.values())
        emit("    elements carrying a control label: %d, of which <a>: %d, of"
             % (len(shapes), len(anchors)))
        emit("    which pointing at the guide-overlay path: %d" % len(overlay))
        emit("    any of %s on any of them: %s"
             % ("/".join(DISCLOSURE_ATTRIBUTES),
                "YES" if any_disclosure else "NO"))
        emit("    total html occurrences of all five rows' needles: %d"
             % target_total)
        emit()
        if not any_disclosure and target_total == 0:
            emit("    ***  NOT A COLLAPSED PANEL. The control carries no")
            emit("    ***  aria-expanded, no aria-controls and no aria-haspopup,")
            emit("    ***  so it claims to expand NOTHING -- and none of the")
            emit("    ***  five rows' text is anywhere in the document, so")
            emit("    ***  there is no region for it to have expanded.")
            emit("    ***  A13's DERIVED reading is now MEASURED on both")
            emit("    ***  halves: the control is a link, and the panel does")
            emit("    ***  not exist on the page in any state.")
        elif any_disclosure and target_total == 0:
            emit("    ***  MIXED, AND THE MIX IS THE FINDING. The control DOES")
            emit("    ***  carry a disclosure attribute, so it claims to expand")
            emit("    ***  something -- but none of the five rows' text is in")
            emit("    ***  the document. Whatever it expands is fetched, not")
            emit("    ***  hidden. Report both halves; do not pick one.")
        elif target_total:
            emit("    ***  THE TEXT IS PRESENT IN HTML. That contradicts A13's")
            emit("    ***  live reading of 0 for 'How you match', twice. Two")
            emit("    ***  readings disagree: date both before adjudicating")
            emit("    ***  either, and re-take rather than overturning A13 on")
            emit("    ***  one sample.")
    emit()
    emit("=== WHAT THIS CANNOT SAY")
    emit("    Nothing about what pressing the control would do -- nothing was")
    emit("    pressed, and that remains an unruled action.")
    emit("    Nothing about postings other than this one. Top-applicant is a")
    emit("    per-posting flag and its absence here is one sample.")
    _write(lines)


def _write(lines: list) -> None:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print()
    print("written to _audit/_scratch/%s" % OUT_PATH.name)


if __name__ == "__main__":
    asyncio.run(main())
