"""Capture the LinkedIn-hosted apply flow, WITHOUT applying to anything.

WHAT THIS IS FOR. ``writes.SANCTIONED_WRITES['linkedin_apply_job']`` is
specced, gated and refuses. It was written when the reason was a missing
capture rather than a missing code path: across the thirteen job captures this
repo held, there were zero forms, zero file inputs, zero dialogs, zero
screening questions and zero controls that submit anything.

**THAT GAP IS NOW CLOSED, AND THE ANSWER ARGUES FOR KEEPING THE REFUSAL.**
Run against job 4447654264 on 2026-08-24, this probe measured the flow, and
what it found is the reason not to drive it:

  * the flow is ONE SCREEN. Visible controls named Submit: 1. Visible controls
    named Next, Continue or Review: **0**.
  * that submit control is **ENABLED on arrival** -- no ``disabled``, no
    ``aria-disabled``.
  * there is no step structure to reason from: zero "N of M" phrases, zero
    ``role="progressbar"``, zero ``aria-valuenow``.

So there is no intermediate control to stop at. The first control whose
activation could submit is the only control the screen offers. A driven apply
here is not "fill several steps and stop before the last one"; it is one click
away from an irreversible send, with nothing in between to check against.

The refusal therefore stands on a measurement rather than on an absence, and
that is a better place for it to stand. Full findings, including two structural
traps (the url does NOT stay on the apply path, and the modal is a different
rendering stack from the posting page) are in
``_audit/2026-08-24-measure-messaging-and-apply.md``.

THE GOOD NEWS ABOUT THE SHAPE. LinkedIn draws the apply control as an
``<a href>``, not a button, and the href is the posting's own apply url. So
reaching the flow is a NAVIGATION rather than a click -- this script never
clicks anything, and the most dangerous class of capture mistake is not
available to it.

WHAT IT REFUSES TO DO, structurally rather than by intention:
  * it never clicks, fills, presses, checks or selects -- there is no such call
    in this file;
  * it takes the job id as an argument and refuses without one, so nobody runs
    it against whatever posting happened to be open;
  * it captures and reports, and every decision about what the capture MEANS is
    left to a human reading it.

THE SIDE EFFECT, AND WHAT MEASURING IT ACTUALLY SHOWED. The expectation was
that opening an Easy Apply flow creates a draft visible in the job tracker. So
this script reads the tracker BEFORE and AFTER, on a surface the apply
navigation does not touch.

Measured 2026-08-24, job 4447654264: the counts did **not** move.

    BEFORE {'saved': 0, 'draft': 1, 'applied': 0, 'interview': 0}
    AFTER  {'saved': 0, 'draft': 1, 'applied': 0, 'interview': 0}

The expectation was wrong, which is why it was measured rather than asserted.
Read that result with the limit the code itself prints: it means nothing
COUNTED changed, not that nothing was created, and it is one observation on one
posting. The tracker is also FLAKY -- repeated loads get redirected to a bare
``/jobs-tracker/?_l=en_US`` with no counts at all -- so the verdict below
reports INCONCLUSIVE when it could not read, rather than calling an unreadable
pass "no change".

**Still: run it with him present, on a posting he would not mind having a
draft against.** One negative observation does not make a load free.

Run:
    python scripts/_probe_apply_flow.py <numeric-job-id>

Writes ``_audit/_probe-apply-*.html`` (gitignored) and prints an inventory of
exactly the controls that are missing from every existing capture.
"""
from __future__ import annotations

import asyncio
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server.browser import BROWSER  # noqa: E402
from linkedin_server.config import BASE_URL, SETTLE_MS  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "_audit"

#: The tracker, read before and after so a NEW DRAFT is visible. Not the
#: surface the apply navigation lands on -- which is the whole point, exactly
#: as the messaging probe reads its badge off the feed rather than the inbox.
#:
#: ``?stage=draft`` rather than ``?stage=applied``, and that token was
#: measured rather than guessed: the tab is LABELLED "In Progress" but
#: ``?stage=in_progress`` renders a page whose main content never appears at
#: all, and ``in-progress`` / ``inprogress`` / ``in_review`` are silently
#: redirected to a bare tracker with no counts. Only ``draft`` renders the
#: rows -- and this is the tab that holds the number an apply flow moves.
TRACKER_URL = f"{BASE_URL}/jobs-tracker/?stage=draft"

#: What every existing capture is missing. Hunted by shape rather than by a
#: guessed selector, because the entire problem is that nobody knows what the
#: selectors are -- a probe that looked for a specific submit button would find
#: nothing and prove nothing.
_INVENTORY = (
    ("forms", "form"),
    ("file inputs", "input[type=file]"),
    ("dialogs", "[role=dialog]"),
    ("text inputs", "input[type=text], input:not([type])"),
    ("radios", "input[type=radio]"),
    ("checkboxes", "input[type=checkbox]"),
    ("selects", "select"),
    ("textareas", "textarea"),
    ("buttons", "button"),
)


def _strip(html: str) -> str:
    text = re.sub(r"<(script|style)\b.*?</\1>", " ", html, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


async def _load(page, url: str, *, label: str) -> str:
    await BROWSER.wait_for_rate_slot()
    await page.goto(url, wait_until="domcontentloaded", timeout=45_000)
    BROWSER._last_navigation_at = time.monotonic()
    html_pre = await page.content()
    (OUT / f"_probe-apply-{label}-pre.html").write_text(html_pre, encoding="utf-8")
    try:
        await page.wait_for_load_state("networkidle", timeout=SETTLE_MS)
    except Exception:
        await page.wait_for_timeout(SETTLE_MS)
    html = await page.content()
    (OUT / f"_probe-apply-{label}-hyd.html").write_text(html, encoding="utf-8")
    print(f"\n=== {label}: asked {url}")
    print(f"    landed  {page.url}")
    print(f"    pre {len(html_pre)} chars / hydrated {len(html)} chars")
    return html


#: Words that, on a control visible BEFORE anything is pressed, mean "this one
#: ends the flow". Kept apart from the advance words because the entire
#: question is whether the two are distinguishable IN ADVANCE.
_TERMINAL_WORDS = ("submit", "send application", "apply now")
_ADVANCE_WORDS = ("next", "continue", "review")


async def _named_controls(page) -> list:
    """Every actionable control, with the fields needed to tell them apart.

    THIS IS THE MEASUREMENT THE PROBE EXISTS FOR. Knowing that a flow rendered
    is not enough: a driven apply is only safe if the control that SUBMITS can
    be told from the control that ADVANCES before either is pressed. So each
    control is read with its aria-label, its visible text and its disabled
    state, and the resulting name is matched against both vocabularies.

    Reading several fields is deliberate rather than defensive. The apply
    census measured a control whose visible text ("Apply") was identical on
    two branches meaning entirely different things, so one field alone has
    already been shown insufficient on this exact surface.
    """
    out: list = []
    sel = "button, [role=button], input[type=submit], input[type=button]"
    try:
        total = int(await page.locator(sel).count())
    except Exception as exc:
        print(f"    controls UNREADABLE ({type(exc).__name__})")
        return out
    for i in range(min(total, 60)):
        node = page.locator(sel).nth(i)
        rec: dict = {}
        for key, coro in (
            ("aria", node.get_attribute("aria-label")),
            ("text", node.inner_text()),
            ("disabled", node.get_attribute("disabled")),
            ("aria_disabled", node.get_attribute("aria-disabled")),
        ):
            try:
                val = await coro
            except Exception:
                val = None
            rec[key] = val.strip() if isinstance(val, str) else val
        try:
            rec["visible"] = bool(await node.is_visible())
        except Exception:
            rec["visible"] = False
        name = f"{rec.get('aria') or ''} {rec.get('text') or ''}".strip().lower()
        rec["name"] = " ".join(name.split())
        rec["terminal"] = any(w in rec["name"] for w in _TERMINAL_WORDS)
        rec["advance"] = any(w in rec["name"] for w in _ADVANCE_WORDS)
        out.append(rec)
    return out


async def _inventory(page, label: str) -> None:
    print(f"\n--- CONTROL INVENTORY: {label}")
    for name, selector in _INVENTORY:
        try:
            count = int(await page.locator(selector).count())
        except Exception as exc:  # pragma: no cover - a measurement
            print(f"    {name:<14} UNREADABLE ({type(exc).__name__})")
            continue
        print(f"    {name:<14} {count}")

    controls = await _named_controls(page)
    print(f"\n--- NAMED CONTROLS ({len(controls)} found)")
    for rec in controls:
        if not rec["name"]:
            continue
        flag = "TERMINAL" if rec["terminal"] else ("advance" if rec["advance"] else "")
        off = rec["disabled"] is not None or rec["aria_disabled"] == "true"
        print(
            f"    {rec['name'][:58]!r:<62}"
            f"{flag:<10}{'disabled' if off else '':<10}"
            f"{'' if rec['visible'] else 'hidden'}"
        )

    term = [r for r in controls if r["terminal"] and r["visible"]]
    adv = [r for r in controls if r["advance"] and r["visible"]]
    print("\n--- DISTINGUISHABILITY (the load-bearing question)")
    print(f"    visible TERMINAL-named: {len(term)} -> {[r['name'][:38] for r in term]}")
    print(f"    visible ADVANCE-named : {len(adv)} -> {[r['name'][:38] for r in adv]}")
    if term and not adv:
        print("    THE FIRST SCREEN CARRIES A SUBMIT AND NO NEXT. One")
        print("    activation from here could complete an application.")
    elif adv and not term:
        print("    First screen advances only. This says NOTHING about later")
        print("    screens, which the probe does not reach because reaching")
        print("    them means pressing something.")
    elif term and adv:
        print("    BOTH on one screen. The names differ, so they ARE")
        print("    distinguishable -- but a driver has to be right every time.")
    else:
        print("    NEITHER vocabulary matched a visible control. Either the")
        print("    flow did not render, or LinkedIn names its controls with")
        print("    words this probe does not know -- which is precisely when")
        print("    a guessed selector would fire blind.")


async def _step_structure(page) -> None:
    """Does the surface say how many steps it has, before you walk them?"""
    print("\n--- STEP STRUCTURE")
    try:
        text = await page.inner_text("body")
    except Exception as exc:
        print(f"    UNREADABLE ({type(exc).__name__})")
        return
    hits = re.findall(r"(?i)\b(?:step\s*)?(\d+)\s*of\s*(\d+)\b", text)
    print(f"    'N of M' phrases: {hits[:10] or 'NONE'}")
    for sel, what in (
        ("[role=progressbar]", "progressbar"),
        ("progress", "progress element"),
        ("[aria-valuenow]", "aria-valuenow"),
    ):
        try:
            n = int(await page.locator(sel).count())
        except Exception:
            n = -1
        print(f"    {what:<16} {n}")


async def _auto_advance(page, seconds: int = 10) -> None:
    """Does anything move WITHOUT being touched?

    Answers "does anything auto-advance or auto-submit" directly. The page is
    left entirely alone and sampled twice; if the url or the control set moves
    while nothing presses anything, that is the finding -- and a surface that
    moves by itself cannot be driven by a plan made before it moved.
    """
    print(f"\n--- AUTO-ADVANCE WATCH ({seconds}s, nothing is touched)")

    async def sample():
        try:
            names = tuple(sorted(r["name"] for r in await _named_controls(page) if r["name"]))
        except Exception:
            names = ("UNREADABLE",)
        return page.url, names

    first = await sample()
    print(f"    t=0   url={first[0]}")
    print(f"          {len(first[1])} named controls")
    await page.wait_for_timeout(seconds * 1000)
    last = await sample()
    print(f"    t={seconds}  url={last[0]}")
    print(f"          {len(last[1])} named controls")
    if first == last:
        print("    STABLE: neither the url nor the control set moved on its own.")
    else:
        if first[0] != last[0]:
            print(f"    URL MOVED UNTOUCHED: {first[0]} -> {last[0]}")
        if first[1] != last[1]:
            print(f"    CONTROLS CHANGED UNTOUCHED.")
            print(f"      gained={sorted(set(last[1]) - set(first[1]))[:6]}")
            print(f"      lost  ={sorted(set(first[1]) - set(last[1]))[:6]}")


async def _tab_counts(page) -> dict:
    """EVERY tracker tab count, not just Applied.

    THE METER THAT MATTERS IS ``in_progress``, NOT ``applied``, and that was a
    discovery rather than a design choice. On this account the tracker reads
    ``applied: 0`` and ``in_progress: 1`` -- so an Easy Apply DRAFT is a
    distinct, counted state that an application never has to reach. A probe
    watching only the Applied number would call a newly created draft "no
    change" and report the load as free.

    Read through the package's own shaper, so the probe and the server agree
    about what a tab count is.
    """
    from linkedin_server import shape as _shape

    try:
        text = await page.inner_text("main")
    except Exception:
        return {}
    return _shape.parse_tracker_tabs(text)


async def main(job_id: str) -> None:
    apply_url = f"{BASE_URL}/jobs/view/{job_id}/apply/?openSDUIApplyFlow=true"
    async with BROWSER.session() as page:
        # --- 1. the applied list BEFORE, on a surface apply does not touch ---
        await _load(page, TRACKER_URL, label="tracker-before")
        before = await _tab_counts(page)
        print(f"    tab counts BEFORE: {before}")

        # --- 2. the posting, to confirm the route before opening the flow ---
        await _load(page, f"{BASE_URL}/jobs/view/{job_id}/", label="posting")

        # WAIT FOR THE CONTROL, NOT FOR A CLOCK -- the same false negative the
        # route screen hit: four postings in a row reported zero apply-ish
        # labels purely because they had not rendered yet. Without this the
        # guard below stops on postings that are perfectly good subjects.
        for _ in range(12):
            try:
                if int(await page.locator('a[aria-label*="Apply"]').count()) > 0:
                    break
            except Exception:
                pass
            await page.wait_for_timeout(2_000)

        html = await page.content()
        names = sorted(set(re.findall(r'aria-label="([^"]*[Aa]pply[^"]*)"', html)))
        print("    apply control names on the posting:", names)
        if not any("LinkedIn Apply" in n for n in names):
            print()
            print("    STOPPING. This posting does not draw the LinkedIn-hosted")
            print("    apply control, so its flow is not the one that needs")
            print("    capturing. Off-site postings hand you to a third party's")
            print("    system, which is not this server's to drive at any")
            print("    capture quality. Pick a posting whose apply_path reads")
            print("    'linkedin_apply' -- linkedin_job_detail reports it.")
            await BROWSER.stop()
            return

        # --- 3. THE FLOW ITSELF. A navigation. Nothing is clicked. ----------
        await _load(page, apply_url, label="flow")

        # Let the flow render before counting it. An inventory taken too early
        # reports zeros, and zeros here would read as "the flow has no
        # controls" when they mean "the page had not drawn yet" -- the single
        # most misleading result this probe could produce, and the one the
        # apply census explicitly warns about for the empty shell capture.
        settled = False
        for _ in range(15):
            try:
                if int(await page.locator("button").count()) > 3:
                    settled = True
                    break
            except Exception:
                pass
            await page.wait_for_timeout(2_000)
        print(f"    flow rendered controls within 30s: {settled}")

        await _inventory(page, "apply flow")
        await _step_structure(page)
        await _auto_advance(page)
        print("\n    text head:", _strip(await page.content())[:900])

        # --- 4. the applied list AFTER, same surface as step 1 --------------
        await _load(page, TRACKER_URL, label="tracker-after")
        after = await _tab_counts(page)
        print(f"    tab counts AFTER : {after}")

        print("\n=== SIDE-EFFECT VERDICT")
        if not before or not after:
            print("    INCONCLUSIVE: the tab counts could not be read on one or")
            print("    both passes, so a change could not have been seen. That is")
            print("    not the same as no change.")
        elif before == after:
            print(f"    NO OBSERVED CHANGE: {before} -> {after}")
            print("    Opening the flow moved no counter LinkedIn renders. Still")
            print("    not proof that nothing was created -- only that nothing")
            print("    COUNTED changed.")
        else:
            moved = {k: (before.get(k), after.get(k))
                     for k in set(before) | set(after)
                     if before.get(k) != after.get(k)}
            print(f"    CHANGED: {moved}")
            print("    OPENING THE FLOW REGISTERED SOMETHING. If in_progress went")
            print("    up, merely LOADING the apply surface creates a draft --")
            print("    which makes it a WRITE wearing a read's clothes, and the")
            print("    single most important fact about this feature.")

        print("\n=== WHAT WOULD LIFT THE REFUSAL")
        print("    The capture is now on disk. What has to be written into the")
        print("    code, by a human who read it, is: the selector for each")
        print("    control the flow requires, the selector that SUBMITS, and")
        print("    whether the flow is one screen or several. Until those are")
        print("    measured from these files, writes.perform stays refusing --")
        print("    an apply cannot be withdrawn by this server under any")
        print("    circumstances, so it is the last action that may be")
        print("    attempted on a guessed selector.")
    await BROWSER.stop()


# Guarded, for the reason set out in _probe_messaging.py: asyncio.run is an
# ATTRIBUTE call and the import-safety rule accepts those, so a probe ending in
# a bare one passes the guard while launching a browser on import. This one
# would navigate into an apply flow. It runs only when run.
if __name__ == "__main__":
    if len(sys.argv) != 2 or not sys.argv[1].strip().isdigit():
        raise SystemExit(
            "usage: python scripts/_probe_apply_flow.py <numeric-job-id>\n"
            "\n"
            "The id is required rather than defaulted. This navigates into a "
            "real apply flow on a real account, and which posting that happens "
            "to be is not a decision a default should make. Pick one whose "
            "linkedin_job_detail apply_path reads 'linkedin_apply', and one "
            "you would not mind holding a draft application against."
        )
    asyncio.run(main(sys.argv[1].strip()))
