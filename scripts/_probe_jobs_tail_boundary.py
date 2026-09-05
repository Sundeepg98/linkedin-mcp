"""Measure what the boundary actually says about the six JOB-SURFACE blockers.

WHY THIS EXISTS. `_audit/2026-09-03-linkedin-gap-blockers.md` costs six job
blockers with a boundary column -- "allowlist +1", "denylist x1", "none". Those
entries were DERIVED from the row text, not measured against the shipped
predicate. This asks the predicate.

WHAT IT IS NOT. It opens nothing. There is no browser, no session and no
network call anywhere in this file. It imports `readonly` and calls the same
`assert_read_url` every reader in this package is gated by, on candidate
address strings that are LITERALS TYPED IN THIS FILE. No url here is derived
from a page, so nothing printed can carry a value this account did not choose
to type -- and none of the candidates carries a member segment of any kind.

THE CONTROL, and it must fire. Two known-answer rows run first: one address
this repo already admits and one it already refuses, with the refusing
substring named. If either disagrees with its expectation the probe raises
before printing a single measurement, because a predicate that cannot refuse
would report every candidate as reachable and look like very good news.

Run:  ./venv/Scripts/python.exe scripts/_probe_jobs_tail_boundary.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import readonly
from linkedin_server.errors import WriteAttemptError

#: (label, url, expected) for the control. `expected` is "ALLOW" or "REFUSE".
#: Both are already settled by the shipped tests, which is what makes them
#: usable as a control rather than as another measurement.
_CONTROL: tuple[tuple[str, str, str], ...] = (
    ("control-allow: the job search surface this server reads today",
     "https://www.linkedin.com/jobs/search/", "ALLOW"),
    ("control-refuse: the apply flow the forbidden tuple names first",
     "https://www.linkedin.com/jobs/application/12345/", "REFUSE"),
)

#: Candidate addresses, one block per blocker row in the ranked table.
#: Spellings are LinkedIn's public url shapes. Where a spelling is a guess it
#: says so in its label, because "the predicate refuses this string" is only
#: interesting when the string is one LinkedIn would actually serve.
_CANDIDATES: tuple[tuple[str, str], ...] = (
    # 36 JOB-ALERTS-SURFACE -- census rows J31-J36 and J41, all writes.
    ("36 alerts: the manage-alerts page (primary spelling)",
     "https://www.linkedin.com/jobs/alerts/"),
    ("36 alerts: the manage-alerts page (hyphenated spelling, unconfirmed)",
     "https://www.linkedin.com/jobs/job-alerts/"),
    ("36 alerts: alerts reached as a search-page panel",
     "https://www.linkedin.com/jobs/search/?f_AL=true"),
    ("36 alerts: a delete verb on an alert id",
     "https://www.linkedin.com/jobs/alerts/delete/1234"),
    ("36 alerts: a create verb, the spelling a toggle would post to",
     "https://www.linkedin.com/jobs/alerts/create"),
    ("36 alerts: alert settings, where frequency and channel would live",
     "https://www.linkedin.com/jobs/alerts/settings/"),

    # 61 PREMIUM-APPLY-SURFACES -- census rows J78-J83.
    ("61 premium: the premium hub this repo already names as a census key",
     "https://www.linkedin.com/premium/my-premium/"),
    ("61 premium: a premium products page (unconfirmed spelling)",
     "https://www.linkedin.com/premium/products/"),
    ("61 premium: top-choice, which spends a non-refunding monthly credit",
     "https://www.linkedin.com/jobs/view/1234567890/top-choice/"),

    # 62 TRACKER-ROW-MENU -- census rows J54-J56.
    ("62 tracker: the saved stage, already admitted",
     "https://www.linkedin.com/jobs-tracker/?stage=saved"),
    ("62 tracker: the applied stage, already admitted",
     "https://www.linkedin.com/jobs-tracker/?stage=applied"),
    ("62 tracker: a stage this pattern does not name",
     "https://www.linkedin.com/jobs-tracker/?stage=archived"),
    ("62 tracker: the tracker root with no stage",
     "https://www.linkedin.com/jobs-tracker/"),

    # 65 JOBCARD-OVERFLOW-MENU -- the menu is drawn on an admitted page.
    ("65 jobcard: the search page the card menu is drawn on",
     "https://www.linkedin.com/jobs/search/?keywords=node.js"),
    ("65 jobcard: a posting view, the other page a card menu is drawn on",
     "https://www.linkedin.com/jobs/view/1234567890/"),

    # 70 EASY-APPLY-MULTISTEP -- three forbidden spellings reach this flow.
    ("70 easyapply: the flow named as one word",
     "https://www.linkedin.com/jobs/easyapply/1234567890/"),
    ("70 easyapply: the flow named with a hyphen",
     "https://www.linkedin.com/jobs/easy-apply/1234567890/"),

    # 81 FOUND-A-JOB-FLOW -- one write, spelling unconfirmed.
    ("81 found-a-job: the flow spelled as a jobs path (unconfirmed)",
     "https://www.linkedin.com/jobs/found-a-job/"),
    ("81 found-a-job: the same flow reached from the tracker",
     "https://www.linkedin.com/jobs-tracker/?stage=applied&found=true"),
)


def _verdict(url: str) -> tuple[str, str]:
    """Return (relation, reason) for one candidate.

    The relation is one of ALLOW / REFUSE. The reason names the forbidden
    substring when one bit, because a refusal that reports only that it did not
    match is half a measurement -- this repository has lost three rounds to
    exactly that shape.
    """
    hits = [s for s in readonly._FORBIDDEN_URL_SUBSTRINGS if s in url]
    try:
        readonly.assert_read_url(url)
    except WriteAttemptError:
        if hits:
            return "REFUSE", "forbidden substring: " + ", ".join(repr(h) for h in hits)
        return "REFUSE", "no allowlist pattern matches"
    except Exception as exc:  # pragma: no cover - defensive
        return "REFUSE", "raised " + type(exc).__name__
    if hits:
        return "ALLOW", "exempted despite substring: " + ", ".join(repr(h) for h in hits)
    return "ALLOW", "matched an allowlist pattern"


def main() -> int:
    for label, url, expected in _CONTROL:
        relation, reason = _verdict(url)
        if relation != expected:
            print("CONTROL FAILED: " + label)
            print("  expected " + expected + ", predicate said " + relation)
            print("  reason: " + reason)
            print("  The predicate is not deciding. No measurement below would")
            print("  mean anything, so none was taken.")
            return 2
        print("control ok  " + expected.ljust(6) + "  " + label)

    print("")
    print("allowlist patterns: " + str(len(readonly._ALLOWED_URL_PATTERNS)))
    print("forbidden substrings: " + str(len(readonly._FORBIDDEN_URL_SUBSTRINGS)))
    print("")

    allow = 0
    refuse_substring = 0
    refuse_nopattern = 0
    for label, url in _CANDIDATES:
        relation, reason = _verdict(url)
        if relation == "ALLOW":
            allow += 1
        elif reason.startswith("forbidden"):
            refuse_substring += 1
        else:
            refuse_nopattern += 1
        print(relation.ljust(7) + label)
        print("        " + reason)

    print("")
    print("candidates: " + str(len(_CANDIDATES)))
    print("  ALLOW                          " + str(allow))
    print("  REFUSE by forbidden substring  " + str(refuse_substring))
    print("  REFUSE no pattern matches      " + str(refuse_nopattern))
    return 0


if __name__ == "__main__":
    sys.exit(main())
