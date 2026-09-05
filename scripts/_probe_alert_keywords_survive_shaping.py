"""Does a job alert's keyword survive ``shape.parse_notification``?

``shape.notification_handles`` exists to turn a notification url into
something a tool here accepts, and its own docstring names the payoff: "a
keyword a caller can pass straight to linkedin_search_jobs". This asks
whether that key can ever be emitted through the shaper that calls it.

THE CONTROL IS THE WHOLE READING. ``notification_handles`` is run twice on
the SAME link -- once raw, once as ``parse_notification`` hands it over --
and a second key (``company_id``, which lives in the PATH rather than the
query) is run through both as well. Without that second key a zero could
mean a broken extractor; with it, the two keys disagree and the disagreement
names the cause.

Read-only. Module-level literals plus the tracked notifications fixture. No
browser, no session, no member name, no company this account has any
relationship with.
"""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from linkedin_server import shape  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "notifications.html"

#: The shape of a job-alert notification link, taken from the tracked
#: fixture and rewritten with a generic query so no reading of his own is
#: quoted here.
ALERT_LINK = (
    "https://www.linkedin.com/jobs/search-results/?keywords=Senior+Software"
    "+Engineer&f_TPR=a1787213463-&origin=SEMANTIC_SEARCH_JOB_ALERT"
)
#: A Page link whose id belongs to nobody -- the all-zeroes convention this
#: repository already uses for a synthetic urn. It has to be SHAPE-VALID: it
#: is the control, and an id the extractor cannot read would make the zero
#: beside it uninterpretable.
COMPANY_LINK = "https://www.linkedin.com/company/0000/"


def main() -> int:
    print("CONTROL -- the extractor on the RAW link, both keys")
    raw_alert = shape.notification_handles(ALERT_LINK)
    raw_company = shape.notification_handles(COMPANY_LINK)
    print(f"  keywords link  -> {raw_alert}")
    print(f"  company link   -> {raw_company}")
    if not raw_alert or not raw_company:
        print("  CONTROL FAILED: the extractor is silent on a link it should read.")
        return 1

    print("\nWHAT parse_notification HANDS THE EXTRACTOR")
    shaped_alert = shape.absolute_url(ALERT_LINK)
    shaped_company = shape.absolute_url(COMPANY_LINK)
    print(f"  keywords link  -> {shaped_alert}")
    print(f"  company link   -> {shaped_company}")

    print("\nTHE EXTRACTOR ON THE SHAPED LINK")
    out_alert = shape.notification_handles(shaped_alert)
    out_company = shape.notification_handles(shaped_company)
    print(f"  keywords link  -> {out_alert}")
    print(f"  company link   -> {out_company}")

    print("\nEND TO END, through the shaper a tool actually calls")
    record = {
        "text": "Your job alert for Senior Software Engineer: 12 new jobs",
        "time": "2h",
        "href": ALERT_LINK,
        "unread": True,
    }
    print(f"  parse_notification -> {shape.parse_notification(record)}")

    print("\nHOW MUCH OF THIS IS ON DISK ALREADY")
    if FIXTURE.exists():
        html = FIXTURE.read_text(encoding="utf-8", errors="replace")
        hrefs = re.findall(r'href="([^"]*keywords=[^"]*)"', html)
        print(f"  {FIXTURE.name}: {len(hrefs)} links carrying keywords=")
        landing = len(re.findall(r"/jobs/search-results", html))
        print(f"  {FIXTURE.name}: {landing} occurrences of /jobs/search-results")
    else:
        print(f"  {FIXTURE} is absent -- this half of the reading is not taken.")

    lost = bool(raw_alert) and not out_alert
    kept = bool(out_company)
    print("\nVERDICT")
    print(f"  keyword survives shaping : {not lost}")
    print(f"  company id survives      : {kept}")
    if lost and kept:
        print("  The query string is deleted before the extractor runs, so the")
        print("  key that lives in the query can never be emitted and the key")
        print("  that lives in the path always can. One of two keys still")
        print("  fires, which is why nothing looks broken.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
