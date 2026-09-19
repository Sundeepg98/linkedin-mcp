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
#: A Page link, and it is the CONTROL: the key that lives in a url's PATH,
#: run beside the key that lives in its QUERY, so that a zero from the second
#: is legible rather than ambiguous. It has to be shape-valid -- an id the
#: extractor cannot read would leave both keys silent and say nothing.
#:
#: THE ID IS TAKEN FROM ``tests/test_no_committed_identity.py``'s
#: ``SYNTHETIC_IDS``, WHICH ALREADY HOLDS IT. That set is the register of
#: values this repository has established are invented, and ``_id_ok`` passes
#: anything in it -- so reusing a member widens NOTHING, where declaring a
#: plant would widen what the guard tolerates in this file forever. Reach for
#: an existing synthetic before reaching for the allowlist.
COMPANY_LINK = "https://www.linkedin.com/company/5417062/"


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
    shaped_row = shape.parse_notification(record) or {}
    print(f"  parse_notification -> {shaped_row}")

    print("\nHOW MUCH OF THIS IS ON DISK ALREADY")
    if FIXTURE.exists():
        html = FIXTURE.read_text(encoding="utf-8", errors="replace")
        hrefs = re.findall(r'href="([^"]*keywords=[^"]*)"', html)
        print(f"  {FIXTURE.name}: {len(hrefs)} links carrying keywords=")
        landing = len(re.findall(r"/jobs/search-results", html))
        print(f"  {FIXTURE.name}: {landing} occurrences of /jobs/search-results")
    else:
        print(f"  {FIXTURE} is absent -- this half of the reading is not taken.")

    # THE VERDICT IS ABOUT THE CALLER, NOT ABOUT THE COMPOSITION.
    #
    # It used to be computed from ``notification_handles(absolute_url(link))``
    # -- the two functions composed by hand here -- which was the same thing
    # ``parse_notification`` did, so the two agreed and the reading was sound.
    # THAT IS NO LONGER TRUE. The fix (2026-09-05) left ``absolute_url``
    # stripping exactly as before and changed WHICH STRING the caller hands
    # over, so the hand-composed reading still comes back empty while the
    # surface works. A verdict computed that way would now be a fact about
    # this script rather than about the server -- the failure this repository
    # keeps finding, arriving inside the instrument that found it.
    lost = "search_keywords" not in shaped_row
    kept = bool(out_company)
    print("\nVERDICT -- measured through parse_notification, which is what ships")
    print(f"  keyword survives shaping : {not lost}")
    print(f"  company id survives      : {kept}")
    if lost and kept:
        print("  The query string is deleted before the extractor runs, so the")
        print("  key that lives in the query can never be emitted and the key")
        print("  that lives in the path always can. One of two keys still")
        print("  fires, which is why nothing looks broken.")
    else:
        print("\n  RESOLVED 2026-09-05. The composition read above still comes")
        print("  back empty, and that is now the CORRECT answer rather than the")
        print("  defect: absolute_url still deletes the query, and the caller")
        print("  no longer asks it to. Extracting a key from a string and")
        print("  publishing that string are different acts, and only the second")
        print("  was ever the risk -- 2 of the 7 query strings on the tracked")
        print("  fixture carry a content urn, which is what the strip protects.")
        print("  The pinned form of this reading is now")
        print("  tests/test_notification_handles.py, whose cases run through")
        print("  parse_notification rather than calling the extractor directly.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
