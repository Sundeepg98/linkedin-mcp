"""BLAST RADIUS FOR THE SEARCH-RESULTS ADMISSION -- condition 3, taken BEFORE
any pattern lands.

The ruling at `569dc5e` section 6 grants `SEARCH-RESULTS-SURFACE` in principle
on five binding conditions. Condition 3 is that **the blast radius is measured
before the pattern lands, with the guard shown failing on what it must still
refuse**, answered with `is_read_url` on concrete urls and **never** with a
substring grep over the pattern list.

**NO PATTERN IS INSTALLED ON DISK BY THIS FILE.** `linkedin_server/readonly.py`
is not edited, not imported for mutation, not touched. Every candidate below
lives only inside `blast_radius.newly_admitted`, which installs it on the
in-process tuple and restores it in a `finally`. Run this, then run
`git diff --stat linkedin_server/readonly.py` -- it is empty.

## IT IMPORTS THE SHIPPED INSTRUMENT

`scripts/blast_radius.py` was built for exactly this admission and it is the
answer to the grep-instead-of-parse error. This file adds ONE thing the shipped
instrument cannot have: a `/search/`-family corpus. The shipped corpus carries
two search addresses, and the shipped instrument says so itself -- "an address
nobody put in the corpus is invisible here, and its absence from this output is
a fact about the corpus and not about the pattern." So the corpus is the
contribution; the predicate is imported.

## THE EVIDENCE CLASS OF THE CORPUS, STATED BEFORE THE OUTPUT

Every `/search/` address below is **CONSTRUCTED from spellings this repository
has already written down**, not verified live. That is not laziness: section 4
of the same ruling forbids a discovery probe from navigating to a refused
address even to find out whether it should be admitted, and every one of these
is refused today. The four this repo has recorded in prose or code --
`/search/results/people/`, `/search/results/all/`, `/search/results/groups/`,
`/search/results/events/`, `/search/results/content/` -- are marked RECORDED;
the rest are marked PLAUSIBLE and are in the corpus precisely because a wildcard
would reach them whether or not anybody has confirmed they exist.

## THE TRAVERSAL SPELLINGS ARE NOT DECORATION

`assert_read_url` matches the string it is handed. A browser normalises `..`
segments BEFORE it issues a request. So a pattern that is anchored only at its
LEFT edge admits a string whose normalised form is a completely different page,
and the three traversal rows below are how that is shown rather than argued.
One of them lands on an account-ending address that **no forbidden substring
names** -- the standing `close-account` example, reached from the search family.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from linkedin_server import readonly  # noqa: E402
from scripts.blast_radius import corpus as shipped_corpus  # noqa: E402
from scripts.blast_radius import newly_admitted  # noqa: E402

BASE = "https://www.linkedin.com"

#: (url, why it is here). The second field is the denominator's audit trail.
SEARCH_FAMILY: tuple[tuple[str, str], ...] = (
    # --- what the 20 rows need -------------------------------------------
    (f"{BASE}/search/results/people/", "RECORDED -- the 16 people rows"),
    (f"{BASE}/search/results/people/?keywords=x", "RECORDED -- keyword search"),
    (
        f"{BASE}/search/results/people/?keywords=x&network=%5B%22F%22%5D"
        f"&geoUrn=%5B%22000%22%5D",
        "RECORDED shape -- the 13 filters and multi-location arrive as query",
    ),
    (f"{BASE}/search/results/all/?keywords=x", "RECORDED -- the blended tab"),
    (f"{BASE}/search/results/groups/?keywords=x", "RECORDED -- N 161, M C70"),
    (f"{BASE}/search/results/events/?keywords=x", "RECORDED -- N 179"),
    (
        f"{BASE}/search/results/content/?keywords=%23hiring",
        "RECORDED -- N 194's candidate route, itself unsettled",
    ),
    (
        f"{BASE}/search/results/companies/?keywords=x",
        "RECORDED spelling, NO ASSIGNED ROW -- N 104 appears nowhere in "
        "blocker-assignments.tsv, at HEAD or in the working tree (12:43)",
    ),
    # --- the rest of the family, which a wildcard cannot help admitting ---
    (f"{BASE}/search/", "PLAUSIBLE -- family root"),
    (f"{BASE}/search/results/", "PLAUSIBLE -- family index"),
    (f"{BASE}/search/results/schools/?keywords=x", "PLAUSIBLE vertical"),
    (f"{BASE}/search/results/services/?keywords=x", "PLAUSIBLE vertical"),
    (f"{BASE}/search/results/courses/?keywords=x", "PLAUSIBLE vertical"),
    (f"{BASE}/search/results/products/?keywords=x", "PLAUSIBLE vertical"),
    (f"{BASE}/search/results/jobs/?keywords=x", "PLAUSIBLE vertical"),
    # --- the neighbourhood a family pattern drags in ----------------------
    (
        f"{BASE}/search/results/people/../../mypreferences/d/close-account",
        "TRAVERSAL -- normalises to an account-ending address NO substring names",
    ),
    (
        f"{BASE}/search/results/people/../../psettings/close-account",
        "TRAVERSAL -- normalises to an address /psettings/ does name",
    ),
    (
        f"{BASE}/search/results/people/../../mynetwork/invite-connect/"
        f"invitations/",
        "TRAVERSAL -- normalises onto the invitation surface",
    ),
    (
        f"{BASE}/mypreferences/d/search-history",
        "A DIFFERENT BLOCKER -- SEARCH-HISTORY-SURFACE, 1R/1W, not this ruling",
    ),
    (
        f"{BASE}/psettings/search-history",
        "A DIFFERENT BLOCKER -- second spelling of the same",
    ),
    # --- keywords that trip the denylist: the admission's OTHER edge ------
    (
        f"{BASE}/search/results/people/?keywords=invitation",
        "FALSE-REFUSAL PROBE -- an ordinary keyword on the forbidden roster",
    ),
    (
        f"{BASE}/search/results/people/?keywords=password",
        "FALSE-REFUSAL PROBE -- same",
    ),
    (
        f"{BASE}/search/results/people/?keywords=verification",
        "FALSE-REFUSAL PROBE -- same",
    ),
    # --- what separates an open query from a structured one ---------------
    (
        f"{BASE}/search/results/people/?next=/mypreferences/d/close-account",
        "DISCRIMINATOR -- a query value carrying a whole other path",
    ),
    (
        f"{BASE}/search/results/people/?keywords",
        "DISCRIMINATOR -- a query with no key=value shape at all",
    ),
)

#: The candidate spellings. NAMED, NOT CHOSEN -- this wave produces the input to
#: a decision. The two wildcards are counterfactuals carried so the instrument
#: can be shown speaking in the other direction; neither is proposed.
CANDIDATES: tuple[tuple[str, str], ...] = (
    (
        "S1-people-only",
        r"^https://www\.linkedin\.com/search/results/people/?(\?[^#]*)?$",
    ),
    (
        "S2-four-verticals",
        r"^https://www\.linkedin\.com/search/results/"
        r"(people|companies|groups|events)/?(\?[^#]*)?$",
    ),
    (
        # THE SAME IDEA, TRIMMED TO WHAT THE ROWS ACTUALLY ASK FOR. `companies`
        # serves no assigned row, so S2 pays blast radius for nothing; these
        # three cover 19 of the 20 reads.
        "S2b-three-verticals-that-have-rows",
        r"^https://www\.linkedin\.com/search/results/"
        r"(people|groups|events)/?(\?[^#]*)?$",
    ),
    (
        "S3-people-structured-query",
        r"^https://www\.linkedin\.com/search/results/people/?"
        r"(\?[a-zA-Z]{1,40}=[^&#/]{0,200}(&[a-zA-Z]{1,40}=[^&#/]{0,200}){0,15})?$",
    ),
    (
        "W1-family-wildcard-ANCHORED (counterfactual, NOT proposed)",
        r"^https://www\.linkedin\.com/search/.*$",
    ),
    (
        "W2-family-prefix-UNANCHORED (counterfactual, NOT proposed)",
        r"^https://www\.linkedin\.com/search/",
    ),
)

#: A candidate that can match no url at all. The instrument must report an
#: EMPTY newly-admitted set for it, which is how "this reported nothing" is
#: distinguished from "this cannot report anything".
NULL_CANDIDATE = r"^THIS-MATCHES-NOTHING$"


def full_corpus() -> list[str]:
    urls = set(shipped_corpus())
    urls.update(url for url, _ in SEARCH_FAMILY)
    return sorted(urls)


def _run(label: str, pattern: str, urls: list[str]) -> dict:
    result = newly_admitted(pattern, urls)
    print("=" * 70)
    print("CANDIDATE  %s" % label)
    print("  pattern  %s" % pattern)
    print("  tested %d urls; %d were already admitted"
          % (result["tested"], result["already_admitted"]))
    print("  NEWLY ADMITTED: %d" % len(result["newly_admitted"]))
    for url in result["newly_admitted"]:
        print("      + %s" % url)
    undefended = result["newly_admitted_and_defended_by_nothing"]
    print("  OF THOSE, DEFENDED BY NOTHING BUT THE ABSENCE OF A RULE: %d"
          % len(undefended))
    for url in undefended:
        print("      !!! %s" % url)
    if result["newly_refused"]:
        print("  NEWLY REFUSED (should never happen for an allowlist add):")
        for url in result["newly_refused"]:
            print("      - %s" % url)
    print()
    return result


def main() -> int:
    urls = full_corpus()
    print("corpus: %d addresses (%d from the shipped instrument, %d added here)"
          % (len(urls), len(shipped_corpus()), len(SEARCH_FAMILY)))
    print("readonly.py patterns on disk: %d   forbidden substrings: %d"
          % (len(readonly._ALLOWED_URL_PATTERNS),
             len(readonly._FORBIDDEN_URL_SUBSTRINGS)))
    print()

    results = {label: _run(label, pattern, urls)
               for label, pattern in CANDIDATES}

    print("=" * 70)
    print("CONTROLS -- an instrument that cannot fail certifies nothing")
    failures: list[str] = []

    null_result = newly_admitted(NULL_CANDIDATE, urls)
    if null_result["newly_admitted"]:
        failures.append(
            "the null candidate admitted %d urls; it can match none"
            % len(null_result["newly_admitted"]))
    print("  [ok] a candidate matching nothing admits nothing (%d)"
          % len(null_result["newly_admitted"]))

    traversal = (
        f"{BASE}/search/results/people/../../mypreferences/d/close-account"
    )
    unanchored = results["W2-family-prefix-UNANCHORED (counterfactual, NOT proposed)"]
    if traversal not in unanchored["newly_admitted"]:
        failures.append(
            "the unanchored prefix did NOT admit the traversal spelling -- "
            "either the corpus lost it or the instrument cannot see it")
    else:
        print("  [ok] the unanchored prefix DOES admit a traversal spelling "
              "that normalises onto an account-ending address")
    if traversal not in unanchored["newly_admitted_and_defended_by_nothing"]:
        failures.append(
            "the traversal spelling was not reported as undefended, so the "
            "undefended field cannot fire and proves nothing")
    else:
        print("  [ok] and reports it as defended by nothing but the absence "
              "of a rule")

    narrow = results["S1-people-only"]
    if not narrow["newly_admitted"]:
        failures.append(
            "the narrow candidate admitted NOTHING -- it cannot serve the "
            "rows, or the corpus lost the address it is for")
    else:
        print("  [ok] the narrow candidate admits the address the rows need "
              "(%d urls)" % len(narrow["newly_admitted"]))

    print()
    if failures:
        print("CONTROLS FAILED -- the numbers above are NOT reportable:")
        for line in failures:
            print("    x %s" % line)
        return 1
    print("ALL CONTROLS PASSED. The instrument was shown speaking in both "
          "directions before its numbers were quoted.")

    assert readonly._ALLOWED_URL_PATTERNS is not None
    print("readonly.py patterns still on disk: %d (unchanged)"
          % len(readonly._ALLOWED_URL_PATTERNS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
