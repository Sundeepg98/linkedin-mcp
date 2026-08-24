"""Capture the LinkedIn-hosted apply flow, WITHOUT applying to anything.

WHAT THIS IS FOR. ``writes.SANCTIONED_WRITES['linkedin_apply_job']`` is
specced, gated and refuses, and the reason is a missing capture rather than a
missing code path: across the thirteen job captures this repo holds there are
**zero forms, zero file inputs, zero dialogs, zero screening questions and zero
controls that submit anything**. Nothing here has ever seen what a caller would
have to fill in or press. Until something has, a selector for it would be a
guess pointed at an irreversible action.

Open To Work got an exact capture procedure out of its census. Apply did not,
which left its refusal looking permanent when it is merely unmeasured. This is
that procedure, as a script, so the gap has an address.

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

THE SIDE EFFECT, STATED AS A HYPOTHESIS BECAUSE THAT IS WHAT IT IS. LinkedIn
shows "in progress" applications in its own job tracker, which suggests opening
an Easy Apply flow may create a draft that becomes visible to the operator and
possibly to the employer. **Nobody here has verified that, on this account or
any other.** It is the same class of claim as the messaging auto-open in
``_probe_messaging.py``, and it is labelled the same way rather than asserted:
an unverified belief that a side effect exists is no better a basis for a
decision than an unverified belief that there is none.

So this script measures it the same way that one does -- by reading the applied
tracker BEFORE and AFTER, on a surface the apply navigation does not touch. If
a draft appears, that is a real finding and the operator will see it in the
output. **Run it with him present, on a posting he would not mind having a
draft against.**

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

#: The applied list, read before and after so a new draft is visible. It is
#: ALREADY an allowed read surface, and it is not the surface the apply
#: navigation lands on -- which is the whole point, exactly as the messaging
#: probe reads its badge off the feed rather than off the inbox.
APPLIED_URL = f"{BASE_URL}/jobs-tracker/?stage=applied"

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


async def _inventory(page, label: str) -> None:
    print(f"\n--- CONTROL INVENTORY: {label}")
    for name, selector in _INVENTORY:
        try:
            count = int(await page.locator(selector).count())
        except Exception as exc:  # pragma: no cover - a measurement
            print(f"    {name:<14} UNREADABLE ({type(exc).__name__})")
            continue
        print(f"    {name:<14} {count}")
    try:
        labels = sorted(
            {
                str(await page.locator("button[aria-label]").nth(i).get_attribute("aria-label") or "")
                for i in range(min(int(await page.locator("button[aria-label]").count()), 40))
            }
        )
        print("    button names:", [x for x in labels if x][:25])
    except Exception as exc:
        print(f"    button names UNREADABLE ({type(exc).__name__})")


async def _applied_count(page) -> str:
    """LinkedIn's own Applied tab count, as rendered. Read as TEXT."""
    try:
        text = await page.inner_text("main")
    except Exception:
        return "unreadable"
    found = re.search(r"Applied\s*[^0-9]{0,4}(\d+)", text)
    return found.group(1) if found else "unreadable"


async def main(job_id: str) -> None:
    apply_url = f"{BASE_URL}/jobs/view/{job_id}/apply/?openSDUIApplyFlow=true"
    async with BROWSER.session() as page:
        # --- 1. the applied list BEFORE, on a surface apply does not touch ---
        await _load(page, APPLIED_URL, label="tracker-before")
        before = await _applied_count(page)
        print(f"    Applied tab count BEFORE: {before}")

        # --- 2. the posting, to confirm the route before opening the flow ---
        html = await _load(page, f"{BASE_URL}/jobs/view/{job_id}/", label="posting")
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
        await _inventory(page, "apply flow")
        print("\n    text head:", _strip(await page.content())[:900])

        # --- 4. the applied list AFTER, same surface as step 1 --------------
        await _load(page, APPLIED_URL, label="tracker-after")
        after = await _applied_count(page)
        print(f"    Applied tab count AFTER: {after}")

        print("\n=== SIDE-EFFECT VERDICT")
        if before == "unreadable" or after == "unreadable":
            print("    INCONCLUSIVE: the Applied tab count could not be read on")
            print("    one or both passes, so a change could not have been seen.")
        elif before == after:
            print(f"    NO OBSERVED CHANGE ({before} -> {after}). Not proof that")
            print("    opening the flow created nothing: LinkedIn may count a")
            print("    draft separately, or not at all. Look at your job tracker.")
        else:
            print(f"    CHANGED: {before} -> {after}. OPENING THE FLOW REGISTERED")
            print("    SOMETHING. That is a finding -- write it down, and treat")
            print("    the apply surface as state-creating on load.")

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
