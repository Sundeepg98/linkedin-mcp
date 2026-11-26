"""His job alerts, as LinkedIn's own alert manager lists them -- census row ``J 37``, the LIST half.

*List and manage all alerts.* Lane build-jobs2, 2026-11-26, over the live
lane's session-11 capture of the jobs home (``/jobs/jam/``, load 17), tracked
as ``tests/fixtures/live11/jobs_alerts_manager.html`` and, with its one
LinkedIn heading measured by keyed shape, as
``tests/fixtures/live11/jobs_alerts_manager_words.html``
(``scripts/_build_live11_word_skeletons.py``).

## WHAT WAS MEASURED (session 11)

Inside ``main`` the page draws only the jobs discovery feed. OUTSIDE ``main``
it draws a ``div[role="dialog"]`` -- the manager, open on load -- whose ``h2``
reads :data:`DIALOG_HEADING` (keyed shape; session 2's jobs home draws the
same heading). In it ONE list of five rows. Each row holds exactly one anchor,
to the alert's own job search (``/jobs/<x>/?keywords=...&distance=...&geoId=...``,
with ``f_TPR`` or ``f_SAL`` on some), whose text is the alert's query words
(his own); a second line (his own words, reduced to ``x``); one button whose
title and label matched no candidate tried; and a detail line. The dialog
draws ``Done`` and a ``Dismiss`` control.

## WHAT LEAVES, AND UNDER WHICH RULING

* Each alert's ``search_keywords`` -- the query exactly as
  ``linkedin_search_jobs`` takes it, read off the row's own href by the
  SHIPPED ``shape.notification_handles`` (the function ``job_home`` already
  reads a recent search's keywords with). HIS OWN TEXT: a job alert's
  keywords are text he typed on his own account, returned to his own session
  under HIS-OWN-TEXT-AT-RUNTIME (the orchestrator, 2026-11-26: "his resume
  file names, his job-alert keywords"), through the tool-envelope guard's one
  narrow door, ``ADMITTED_OWN_TEXT``. Sanitised and bounded, never stored.
* Each alert's ``facets`` -- the NAMES of the filter keys its href carries,
  from a closed list; a filter's VALUE never leaves (a salary band is his pay
  expectation), and the place id never does.
* Counts: rows seen, rows without a search anchor, and the buttons drawn.

NOT READ: the second line and the detail line (unmeasured words), the row
button's label, and anything a press would open. The MANAGE half -- what the
row button opens, and editing or deleting an alert from here -- is not built:
that button's label and its dialog have never been measured.

## THE ZERO RULE

No manager dialog headed :data:`DIALOG_HEADING`, or a dialog with no alert row
read, is not "you have no alerts": no empty manager has been captured, so it
raises ``ExtractionFailedError`` in this module's words, never the page's.

## IT PRESSES NOTHING

It reads the document it is handed; the tool owns the address. Nothing read
here becomes an address: the rows' hrefs are parsed in this process and never
followed.
"""
from __future__ import annotations

from typing import Any, Optional
from urllib.parse import parse_qs, urlsplit

from linkedin_server import dom, job_home, shape
from linkedin_server.errors import ExtractionFailedError

#: The jobs home: the one address, ``J 18``'s.
HOME_URL = job_home.HOME_URL

#: The manager's heading, MEASURED by keyed shape (session 11).
DIALOG_HEADING = "Manage job alerts"

#: The query keys a row's search may carry that name a FILTER, as the recent
#: searches list publishes them. Their PRESENCE leaves; their values never do.
FACETS: tuple[str, ...] = job_home.FACETS + ("geoId",)

#: Characters kept of a query, as the recent searches list keeps.
MAX_KEYWORDS_CHARS = job_home.MAX_KEYWORDS_CHARS

#: The most rows read in one manager; the capture draws five.
MAX_ROWS = 60

#: Milliseconds any one read may wait.
READ_TIMEOUT_MS = 2000


def collapsed(text: Any) -> str:
    return " ".join(text.split()) if isinstance(text, str) else ""


def landed_on_the_home(landed: Any) -> bool:
    """Did the one load keep the jobs home's own path? A yes or a no."""
    if not isinstance(landed, str):
        return False
    try:
        parts = urlsplit(landed)
    except ValueError:
        return False
    return (
        parts.scheme == "https"
        and parts.netloc.lower() == "www.linkedin.com"
        and parts.path.rstrip("/") == "/jobs/jam"
    )


def alert_entry(href: Optional[str]) -> Optional[dict[str, Any]]:
    """One row's anchor -> its search, or ``None`` when it is not a job search.
    PURE; nothing here raises on what the page chose."""
    try:
        parts = urlsplit(str(href or ""))
        query = parse_qs(parts.query, keep_blank_values=True)
    except ValueError:
        return None
    if not parts.path.startswith("/jobs/") or "keywords" not in query:
        return None
    keywords = shape.notification_handles(str(href)).get("search_keywords")
    return {
        "search_keywords": shape.trim(keywords, MAX_KEYWORDS_CHARS) if keywords else None,
        "facets": [facet for facet in FACETS if facet in query],
    }


async def _count(locator: Any, failed: list[int]) -> int:
    try:
        value = await locator.count()
    except Exception:  # noqa: BLE001 -- counted; the message may quote the page
        failed[0] += 1
        return 0
    return value if isinstance(value, int) and not isinstance(value, bool) and value > 0 else 0


async def _text(locator: Any, failed: list[int]) -> str:
    try:
        return collapsed(await locator.text_content(timeout=READ_TIMEOUT_MS))
    except Exception:  # noqa: BLE001 -- counted; the message may quote the page
        failed[0] += 1
        return ""


async def _href(locator: Any, failed: list[int]) -> Optional[str]:
    try:
        value = await locator.get_attribute("href", timeout=READ_TIMEOUT_MS)
    except Exception:  # noqa: BLE001 -- counted; the message may quote the page
        failed[0] += 1
        return None
    return value if isinstance(value, str) else None


async def read_alert_manager(page: Any) -> dict[str, Any]:
    """His job alerts off the manager ``page`` already shows.

    RETURNS ``alerts`` (one per row with a search anchor, page order:
    ``position``, ``search_keywords``, ``facets``), ``rows_seen``,
    ``rows_without_a_search``, ``row_buttons`` and ``reads_failed``.
    Raises ``ExtractionFailedError`` when no manager is drawn, or when it
    lists no alert this reader can read.
    """
    failed = [0]
    dialogs = page.locator('div[role="dialog"]')
    managers = []
    for index in range(min(await _count(dialogs, failed), 8)):
        dialog = dialogs.nth(index)
        headings = dialog.locator("h2")
        texts = [await _text(headings.nth(i), failed)
                 for i in range(min(await _count(headings, failed), 4))]
        if texts.count(DIALOG_HEADING) == 1:
            managers.append(dialog)
    if len(managers) != 1:
        raise ExtractionFailedError(
            f"the jobs home drew {len(managers)} alert manager(s) headed with "
            "LinkedIn's words, where exactly one is required; an empty list "
            "here would be indistinguishable from a broken read.",
            hint=dom._landing_note(page),
        )
    rows = managers[0].locator("ul li")
    out: dict[str, Any] = {
        "alerts": [],
        "rows_seen": 0,
        "rows_without_a_search": 0,
        "row_buttons": 0,
    }
    for index in range(min(await _count(rows, failed), MAX_ROWS)):
        row = rows.nth(index)
        out["rows_seen"] += 1
        out["row_buttons"] += await _count(row.locator("button"), failed)
        anchors = row.locator("a[href]")
        if await _count(anchors, failed) != 1:
            out["rows_without_a_search"] += 1
            continue
        entry = alert_entry(await _href(anchors.nth(0), failed))
        if entry is None or entry["search_keywords"] is None:
            out["rows_without_a_search"] += 1
            continue
        out["alerts"].append({"position": len(out["alerts"]), **entry})
    out["reads_failed"] = failed[0]
    if not out["alerts"]:
        raise ExtractionFailedError(
            f"the alert manager drew {out['rows_seen']} row(s) and none read as "
            "a job search; no empty manager has been captured, so this is not "
            "read as 'you have no alerts'.",
            hint=dom._landing_note(page),
        )
    return out
