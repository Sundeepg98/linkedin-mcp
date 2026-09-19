"""WHAT WOULD A CANDIDATE ALLOWLIST PATTERN NEWLY ADMIT?

Built for the conditional admission at `09f9961`, which grants
`SEARCH-RESULTS-SURFACE` on condition that exactly this measurement is taken
first. **The instrument is separable from the entry**: this answers the
question for ANY candidate pattern, and the wave that owns a surface writes the
pattern.

## IT ANSWERS WITH ``is_read_url`` ON CONCRETE URLS, NEVER A GREP

**This is the whole design and the error it avoids has been paid for twice
today.** A substring search over ``_ALLOWED_URL_PATTERNS`` tells you what the
pattern SOURCE looks like, which is not the question. The question is which
ADDRESSES change verdict, and the only honest way to answer it is to run the
shipped predicate over concrete urls with the candidate installed and again
without it, then diff the two.

Two separate waves reached a wrong answer today by reading pattern text: one
reported a bare path as admitted when ``is_read_url`` matches absolute
spellings only, and one extracted "refused targets" that turned out to be regex
fragments a file uses to MATCH and never to navigate.

## WHAT IT CANNOT TELL YOU, said before the output rather than after

**A DIFF OVER A CORPUS IS A LOWER BOUND ON THE BLAST RADIUS, NEVER THE WHOLE OF
IT.** It reports what the candidate newly admits *among the addresses it was
handed*. An address nobody thought to put in the corpus is invisible here, and
its absence from the output is a fact about the corpus.

So the corpus is built from the repository's OWN recorded addresses -- every
concrete url in the forbidden roster, plus the family spellings this package
has argued about -- rather than invented, and the count of what was tested is
printed beside every result so a reader can see the denominator.

Run:  ./venv/Scripts/python.exe scripts/blast_radius.py "<candidate regex>"

Opens no browser. Navigates nothing. Reads no page.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import readonly  # noqa: E402

BASE = "https://www.linkedin.com"

#: CONCRETE ADDRESSES, every one a full url. The corpus is the denominator and
#: it is assembled from what this repository has already argued about rather
#: than from imagination.
#:
#: THE FORBIDDEN ROSTER IS THE BACKBONE: every address somebody deliberately
#: refused is exactly an address a careless pattern might re-admit, which makes
#: it the highest-value thing to test a candidate against.
def corpus() -> list[str]:
    urls: set[str] = set()

    # 1. Everything the forbidden roster names, as concrete urls.
    for substring in readonly._FORBIDDEN_URL_SUBSTRINGS:
        if substring.startswith("http"):
            urls.add(substring)
        else:
            urls.add(BASE + "/" + substring.strip("/") + "/")

    # 2. Family spellings this package has ruled on, both sides of each line.
    urls.update({
        f"{BASE}/feed/",
        f"{BASE}/in/me/",
        f"{BASE}/in/me/details/skills/",
        # RENAMED FROM a PLAUSIBLE-SLUG SPELLING, 2026-09-19 12:49. The
        # identity guard fired on it -- 3 unallowed hits, 0 declared -- and a
        # red there means UNDECLARED, never real. Renaming is the first
        # remedy and declaring the second, because a declaration spends the
        # guard's precision to keep a string nothing needed. "someone-else"
        # carries the sanctioned token "someone" and is the spelling
        # tests/test_search_admission_blast_radius.py already uses. The
        # VERDICTS ARE UNCHANGED, measured before and after: all three refuse
        # under the shipped predicate either way -- see the commit message.
        f"{BASE}/in/someone-else/",
        f"{BASE}/in/someone-else/details/skills/",
        f"{BASE}/in/someone-else/recent-activity/all/",
        f"{BASE}/mypreferences/d/",
        f"{BASE}/mypreferences/d/change-password",
        f"{BASE}/mypreferences/d/two-factor-authentication",
        f"{BASE}/public-profile/settings",
        f"{BASE}/public-profile/settings/",
        f"{BASE}/uas/login",
        f"{BASE}/mwlite/settings",
        f"{BASE}/jobs/search/",
        f"{BASE}/jobs/view/1234567890/",
        f"{BASE}/jobs-tracker/?stage=draft",
        f"{BASE}/jobs-tracker/",
        f"{BASE}/messaging/",
        f"{BASE}/messaging/compose/",
        f"{BASE}/messaging/thread/abc123/",
        f"{BASE}/article/new/",
        f"{BASE}/pulse/drafts/",
        f"{BASE}/my-items/saved-posts/",
        f"{BASE}/notifications/",
        f"{BASE}/analytics/profile-views/",
        f"{BASE}/search/results/all/?keywords=x",
        f"{BASE}/search/results/people/?keywords=x",
        f"{BASE}/company/a-company/",
        f"{BASE}/groups/12345678/",
        f"{BASE}/events/12345678/",
        f"{BASE}/settings/",
        f"{BASE}/badges/profile/create",
        # SPELLINGS A FAMILY WILDCARD WOULD REACH THAT NOTHING REFUSES.
        # The boundary trap names this class: a settings-family pattern
        # admits several account-ending addresses, some defended by nothing
        # but the absence of a rule. A corpus without them would report a
        # wildcard as harmless.
        f"{BASE}/psettings/member-data",
        f"{BASE}/psettings/account-management",
        f"{BASE}/mypreferences/d/manage-account",
        f"{BASE}/mypreferences/d/settings-hibernate",
        f"{BASE}/help/linkedin/answer/settings",
    })
    return sorted(urls)


def newly_admitted(candidate: str, urls: list[str] | None = None) -> dict:
    """Which addresses change verdict when ``candidate`` is added?

    **MEASURED BY RUNNING THE SHIPPED PREDICATE, TWICE.** The candidate is
    installed onto the real tuple, ``is_read_url`` is re-run over every url,
    and the tuple is restored in a ``finally`` -- so a crash mid-measurement
    cannot leave a widened boundary behind in the process.

    Returns the newly-admitted set, the newly-refused set (which should be
    EMPTY -- adding an allowlist pattern cannot refuse more, and a non-empty
    one means the candidate broke something rather than widened it), and the
    denominator.
    """
    addresses = list(urls if urls is not None else corpus())
    before = {url: readonly.is_read_url(url) for url in addresses}

    original = readonly._ALLOWED_URL_PATTERNS
    try:
        readonly._ALLOWED_URL_PATTERNS = original + (re.compile(candidate),)
        after = {url: readonly.is_read_url(url) for url in addresses}
    finally:
        readonly._ALLOWED_URL_PATTERNS = original

    gained = sorted(u for u in addresses if after[u] and not before[u])
    lost = sorted(u for u in addresses if before[u] and not after[u])
    return {
        "candidate": candidate,
        "tested": len(addresses),
        "already_admitted": sum(1 for u in addresses if before[u]),
        "newly_admitted": gained,
        "newly_refused": lost,
        # **THE HALF A REVIEWER ACTUALLY CARES ABOUT, and the first version
        # of this field had it backwards.** It reported which newly-admitted
        # addresses were on the FORBIDDEN ROSTER -- a set that is structurally
        # almost always empty, because `assert_read_url` checks the denylist
        # BEFORE the allowlist, so an allowlist pattern cannot re-admit a
        # refused address at all. A field that cannot fire certifies nothing.
        #
        # THE REAL HAZARD IS THE OPPOSITE ONE: an address the candidate admits
        # that NOTHING ELSE WAS REFUSING. Those are the ones this repository's
        # boundary trap names -- a settings-family pattern would have admitted
        # six account-ending spellings, "three of them defended by nothing but
        # the absence of a rule". The denylist bounds a wildcard's blast
        # radius; what it does not bound is what the wildcard reaches that
        # nobody had thought to forbid.
        "newly_admitted_and_defended_by_nothing": sorted(
            u for u in gained
            if not any(s in u for s in readonly._FORBIDDEN_URL_SUBSTRINGS)
        ),
    }


def _report(result: dict) -> None:
    print("candidate: %s" % result["candidate"])
    print("  addresses tested        %d" % result["tested"])
    print("  already admitted        %d" % result["already_admitted"])
    print("  NEWLY ADMITTED          %d" % len(result["newly_admitted"]))
    for url in result["newly_admitted"]:
        print("      + %s" % url)
    undefended = result["newly_admitted_and_defended_by_nothing"]
    if undefended:
        print("  *** %d OF THOSE WERE DEFENDED BY NOTHING BUT THE ABSENCE OF"
              % len(undefended))
        print("      A RULE -- no denylist entry refused them before ***")
        for url in undefended:
            print("      !!! %s" % url)
    if result["newly_refused"]:
        print("  NEWLY REFUSED (unexpected -- an allowlist entry should not")
        print("  refuse anything; this means the candidate broke a pattern)")
        for url in result["newly_refused"]:
            print("      - %s" % url)
    print()
    print("  THE DENOMINATOR IS THE POINT. This is a LOWER BOUND: it reports")
    print("  what the candidate admits AMONG THESE %d ADDRESSES. An address"
          % result["tested"])
    print("  nobody put in the corpus is invisible here, and its absence from")
    print("  this output is a fact about the corpus and not about the pattern.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(
            'usage: python scripts/blast_radius.py "<candidate regex>"'
        )
    _report(newly_admitted(sys.argv[1]))
