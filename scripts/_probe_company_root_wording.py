"""MEASURE THE WORDING LINKEDIN ACTUALLY DRAWS BESIDE THESE TWO COUNTS.

``company_root.COUNT_PHRASES`` shipped as an UNMEASURED GUESS and says so in
its own comment -- *these are the shapes LinkedIn's own help pages use; no
capture in this repository holds a company Page, so the first live fire is what
settles them.* The first live fire ran on 2026-09-21 and split:

    connections_following_page   count_read        6 of 6 Pages
    connections_at_organisation  count_read        2 of 6 Pages
                                 phrase_not_drawn  4 of 6 Pages

``phrase_not_drawn`` is NOT a count of zero, and it has TWO causes that the
reading cannot separate on its own:

    (a) the shipped words are wrong, or
    (b) this account genuinely has nobody working at that employer, so
        LinkedIn draws no such line at all.

**WIDENING THE PHRASE LIST UNTIL A ROW BANKS WOULD ANSWER NEITHER.** It would
convert (b) into a false positive and leave (a) undiagnosed, and a row banked
that way rests on a guess that happened to match. So this probe measures the
page instead, in two independent ways that answer different halves:

**HALF ONE -- IS A SHIPPED PHRASE THERE AT ALL?** Each of the six shipped
phrases is tested for PRESENCE in the page's own normalised text. It costs no
judgement and it is decisive in one direction: a phrase that IS present on a
page the reader called ``phrase_not_drawn`` convicts the READER, not the
wording.

**HALF TWO -- WHAT DOES LINKEDIN SAY INSTEAD?** Every short text run carrying
``connection`` or ``follow`` is normalised, its digit runs replaced by a
marker, and then only runs made ENTIRELY of tokens from the closed
:data:`INTERFACE_TOKENS` vocabulary are published. Everything else is counted
and withheld.

**THE FIRST VERSION OF THIS FILTER WAS WRONG AND IT IS WORTH WRITING DOWN WHY,
BECAUSE THE REASONING WAS PLAUSIBLE.** It published any run appearing on three
or more different Pages, on the argument that *LinkedIn's boilerplate repeats
across Pages and a third party's name does not*. Run on 2026-09-21 that filter
published a run carrying a real connection's given name **on all six Pages** --
because this surface's line is *"<a connection> and N other connections follow
this page"*, LinkedIn picks ONE of the account's own connections to name, and
the same person follows many Pages. So the name repeated for exactly the
reason the boilerplate does, and a frequency filter cannot tell them apart on
this surface AT ANY THRESHOLD.

**A CLOSED ALLOWLIST CAN**, and it is the same shape the readers themselves
use -- ship a vocabulary in, let nothing else out. A token this package did not
write down is withheld whether it is a name, a brand, a city or a word nobody
anticipated, and the withheld COUNT is published so the filter cannot hide how
much it is dropping.

A run is additionally dropped if it is longer than :data:`MAX_TOKENS` tokens,
because a long run is a sentence rather than a label and is where a name rides.

## WHAT IS AND IS NOT WRITTEN DOWN

**THE RAW HTML OF EVERY PAGE IS A CAPTURE OF OTHER PEOPLE.** It is written
under the gitignored ``_state/`` and nowhere else. Nothing derived from a
single page reaches stdout: the terminal gets booleans per shipped phrase,
integers, and the cross-page intersection.

**NO IDENTIFIER IS PRINTED.** Not an organisation id, not a slug, not a landed
url. The ids are re-derived every run from ``linkedin_followed_companies``,
exactly as ``scripts/_probe_the_three_fires.py`` derives its own.

## BOUNDS

ATTACH ONLY; reads only; one navigation per Page through ``BROWSER.goto``,
which holds the shipped minimum interval. Nothing is pressed.

USAGE::

    set LINKEDIN_CDP_ATTACH=1
    <python> scripts/_probe_company_root_wording.py --orgs 6
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from linkedin_server import company_page, company_root, config, dom  # noqa: E402
from linkedin_server.server import mcp  # noqa: E402

#: A text run longer than this is a sentence, not a label, and a sentence is
#: where a name rides. Twelve is comfortably longer than every shipped phrase
#: (the longest is four tokens) and shorter than a paragraph.
MAX_TOKENS = 12

#: KEPT AS A REPORTED NUMBER, NOT AS THE FILTER. See the module docstring: a
#: frequency threshold was MEASURED not to separate a name from boilerplate on
#: this surface, so it no longer decides anything. It is still printed beside
#: each published run because how many Pages drew a phrase is the evidence that
#: the phrase is LinkedIn's rather than one Page's.
MIN_PAGES = 1

#: THE CLOSED VOCABULARY. A run is published only if EVERY one of its tokens is
#: in here. Every entry is an interface word this package or LinkedIn's own
#: count lines use; there is no name, no brand, no place and no employer in it,
#: and one cannot be added by accident because the list is written out rather
#: than derived from a page.
#:
#: ``n`` IS THE DIGIT MARKER that :func:`marked` substitutes, and ``amp`` is
#: what ``&`` normalises to -- both are artefacts of this probe's own
#: transforms rather than page words.
INTERFACE_TOKENS: frozenset[str] = frozenset(
    """
    a all also amp and are as at be by can company connection connections
    current employee employees first follow followed follower followers
    following follows for from has have here in is it its member members
    more n network of on one only or other others out page pages past
    people person school see school second see show showing that the their
    there these they third this to view viewed we where which who with
    work worked working works you your
    """.split()
)

#: The words that make a run interesting. Both are LinkedIn's, not a person's.
NEEDLES = ("connection", "follow")

EXERCISED = (
    "linkedin_server/company_root.py",
    "linkedin_server/company_page.py",
    "linkedin_server/dom.py",
)

_TAGS = re.compile(r"<[^>]+>")
_DROP_SUBTREES = re.compile(
    r"<(script|style|template|noscript|svg)\b.*?</\1>", re.DOTALL | re.IGNORECASE
)
_DIGITS = re.compile(r"[0-9]+")


def provenance() -> dict[str, Any]:
    try:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(REPO),
            capture_output=True,
            text=True,
            timeout=30,
        ).stdout.strip()
    except Exception as exc:  # noqa: BLE001
        head = "unavailable:" + type(exc).__name__
    shas = {}
    for relative in EXERCISED:
        try:
            shas[relative] = hashlib.sha256(
                (REPO / relative).read_bytes()
            ).hexdigest()
        except Exception as exc:  # noqa: BLE001
            shas[relative] = "unavailable:" + type(exc).__name__
    return {"git_head": head, "sha256": shas}


def text_runs(html: str) -> list[str]:
    """The page's text, split at element boundaries. NORMALISED IN PLACE.

    ``company_root.normalised`` is reused rather than re-implemented -- it is
    the Python mirror of the comparison ``dom.COUNT_LINES_JS`` does inside the
    page, and a second normaliser here would be the two-guards-that-drift
    failure this repository has paid for twice.
    """
    body = _DROP_SUBTREES.sub(" ", html)
    runs: list[str] = []
    for piece in _TAGS.split(body):
        normalised = company_root.normalised(piece)
        if normalised:
            runs.append(normalised)
    return runs


def marked(run: str) -> str:
    """Digit runs replaced by a marker, so a COUNT never becomes a phrase."""
    return _DIGITS.sub("n", run)


def interesting(run: str) -> bool:
    if len(run.split()) > MAX_TOKENS:
        return False
    return any(needle in run for needle in NEEDLES)


def publishable(run: str) -> bool:
    """Every token in the closed vocabulary, or it does not leave this process.

    THE DIRECTION MATTERS. This asks whether each token is one this package
    WROTE DOWN, never whether it looks like a name -- a filter that hunts for
    names has to anticipate them, and the one that shipped before this did
    exactly that and let a real given name through on all six Pages.
    """
    tokens = run.split()
    return bool(tokens) and all(token in INTERFACE_TOKENS for token in tokens)


def shipped_phrase_occurrences(runs: list[str]) -> dict[str, int]:
    """HOW MANY TIMES each shipped phrase occurs in this page's own text.

    **PRESENCE WAS THE WRONG QUESTION AND THIS IS THE RIGHT ONE.** A company
    Page root does not draw these lines once. It draws one per recommended
    organisation card as well as for the subject Page -- measured 2026-09-21
    at 7, 6, 5, 8, 2 and 5 occurrences of `connections follow this page` on six
    Pages -- and every one of them names a DIFFERENT organisation.

    ``dom.COUNT_LINES_JS`` keeps ONE best match per phrase, decided by "carries
    a number" and then by shortest container, and publishes it with no record
    that anything competed. So the number that comes back cannot be attributed
    to the organisation whose Page was opened. A COUNT of the candidates is the
    cheapest thing that makes that visible, and it is an integer, so it costs
    nothing to publish.

    ``company_root._verdict_for``'s ``disagreement`` state cannot cover this:
    it fires when two DIFFERENT PHRASE POSITIONS of one kind disagree, and the
    collapse here happens between occurrences of the SAME phrase, inside the
    page, below the guard.
    """
    joined = " | ".join(runs)
    return {
        phrase: joined.count(phrase)
        for phrase in company_root.phrases_shipped()
    }


def shipped_phrase_presence(runs: list[str]) -> dict[str, bool]:
    """Is each SHIPPED phrase present in this page's own normalised text?

    A phrase present here on a page the reader called ``phrase_not_drawn``
    convicts the reader. A phrase absent everywhere convicts the wording, or
    says the line is genuinely not on the page -- which is what half two is
    for.
    """
    joined = " | ".join(runs)
    return {phrase: (phrase in joined) for phrase in company_root.phrases_shipped()}


async def fire(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    result = await mcp.call_tool(name, arguments)
    payload = getattr(result, "structured_content", None) or result
    if isinstance(payload, dict) and "result" in payload:
        payload = payload["result"]
    return payload if isinstance(payload, dict) else {"ok": False}


def digits_only(values: Any) -> list[str]:
    out = []
    for value in list(values or []):
        text = str(value).strip()
        if text and set(text) <= set("0123456789") and len(text) <= 20:
            out.append(text)
    return out


async def run(wanted: int, keep_raw: bool) -> dict[str, Any]:
    from linkedin_server.browser import BROWSER

    if not config.CDP_ATTACH:
        raise SystemExit("REFUSING TO RUN. Set LINKEDIN_CDP_ATTACH=1 first.")

    # THE TAB IS GIVEN BACK AT THE END -- see
    # ``_probe_control_paths_live.run`` for what an abandoned one costs the
    # next probe's attach.
    try:
        return await _measure(BROWSER, wanted, keep_raw)
    finally:
        try:
            await BROWSER.stop()
        except Exception as exc:  # noqa: BLE001 - teardown noise, never fatal
            print("teardown raised " + type(exc).__name__)


async def _measure(BROWSER: Any, wanted: int, keep_raw: bool) -> dict[str, Any]:
    followed = await fire("linkedin_followed_companies", {"limit": 50})
    rows = followed.get("pages")
    rows = list(rows) if isinstance(rows, (list, tuple)) else []
    candidates: list[str] = []
    for row in rows:
        if isinstance(row, dict):
            found = digits_only([row.get("id")])
            if found:
                candidates.append(found[0])
    seen: set[str] = set()
    ids = [i for i in candidates if not (i in seen or seen.add(i))][:wanted]

    raw_dir = REPO / "_state" / "company-root-wording"
    raw_dir.mkdir(parents=True, exist_ok=True)

    per_page: list[dict[str, Any]] = []
    run_pages: dict[str, int] = {}

    for position, identifier in enumerate(ids):
        address = company_page.company_page_url(identifier)
        if not address.get("built"):
            per_page.append({"index": position, "built": False})
            continue
        async with BROWSER.session() as page:
            try:
                landed = await BROWSER.goto(page, address["url"])
                reading = await company_root.read_company_root(page)
                html = await page.content()
            finally:
                # CLOSE THE PAGE, NEVER THE CONTEXT. The context is the
                # operator's own signed-in Chrome; the page is the tab this
                # process opened. ``tests/test_a_probe_closes_its_own_tab.py``
                # counts the scripts that skip this, and the leak is not
                # cosmetic: ``connect_over_cdp`` enumerates every target on
                # attach, and abandoned tabs put a handshake over its ceiling
                # earlier in this very wave.
                if not page.is_closed():
                    await page.close()

        # THE RAW CAPTURE IS A LIST OF OTHER PEOPLE. Gitignored, always.
        if keep_raw:
            (raw_dir / ("page-%02d.html" % position)).write_text(
                html, encoding="utf-8"
            )

        runs = text_runs(html)
        candidates_here = sorted({marked(r) for r in runs if interesting(r)})
        for candidate in candidates_here:
            run_pages[candidate] = run_pages.get(candidate, 0) + 1

        matches = reading.get("matches") or []
        positions = sorted(
            {
                int(entry.get("phrase"))
                for entry in matches
                if isinstance(entry, dict)
                and isinstance(entry.get("phrase"), int)
            }
        )
        per_page.append(
            {
                "index": position,
                "built": True,
                # A BOOLEAN, NEVER THE LANDING.
                "landed_where_it_was_sent": (
                    str(landed).rstrip("/") == address["url"].rstrip("/")
                ),
                "elements": reading.get("elements"),
                "chunks": reading.get("chunks"),
                "hidden_subtrees_skipped": reading.get("hidden_subtrees_skipped"),
                "non_content_skipped": reading.get("non_content_skipped"),
                "matched_phrase_positions": positions,
                "matched_phrase_kinds": sorted(
                    {company_root.kind_for(p) for p in positions}
                ),
                "shipped_phrase_present": shipped_phrase_presence(runs),
                "shipped_phrase_occurrences": shipped_phrase_occurrences(runs),
                "interesting_runs_here": len(candidates_here),
                # HOW MANY SCREEN-READER SUBTREES THIS SURFACE DRAWS AT ALL.
                # hidden_subtrees_skipped read 0 on every live Page while the
                # control fixture skips 2, and "the walk missed them" and
                # "this surface draws none" are different findings.
                "hidden_selector_class_hits": sum(
                    html.count(token.strip().lstrip("."))
                    for token in dom.CARD_HIDDEN_SELECTOR.split(",")
                ),
            }
        )

    return {
        "provenance": provenance(),
        "pages_read": len([p for p in per_page if p.get("built")]),
        "per_page": per_page,
        "shipped_phrases": company_root.phrases_shipped(),
        **partition(run_pages),
        "_ids": ids,
    }


def partition(run_pages: dict[str, int]) -> dict[str, Any]:
    """Split the runs into PUBLISHED and WITHHELD by the closed vocabulary.

    The withheld ones are counted and never rendered, not even truncated: a
    truncation is still a publication of a prefix, and a given name is short.
    """
    published = {
        run_text: count
        for run_text, count in sorted(run_pages.items())
        if publishable(run_text)
    }
    withheld = {
        run_text: count
        for run_text, count in run_pages.items()
        if not publishable(run_text)
    }
    return {
        "cross_page_runs": published,
        "runs_withheld_out_of_vocabulary": len(withheld),
        "withheld_page_hits_total": sum(withheld.values()),
        "min_pages_to_publish": MIN_PAGES,
    }


def from_raw(raw_dir: Path) -> dict[str, Any]:
    """Re-derive half two from captures already on disk. ZERO PAGE LOADS.

    The filter above replaced one that had already run, and re-running the
    NAVIGATIONS to re-apply a filter would spend six page loads to learn
    nothing new about LinkedIn. The captures are the measurement; the filter
    is a function of them.
    """
    run_pages: dict[str, int] = {}
    files = sorted(raw_dir.glob("page-*.html"))
    phrase_presence: list[dict[str, bool]] = []
    for path in files:
        html = path.read_text(encoding="utf-8", errors="replace")
        runs = text_runs(html)
        phrase_presence.append(
            (shipped_phrase_presence(runs), shipped_phrase_occurrences(runs))
        )
        for candidate in {marked(r) for r in runs if interesting(r)}:
            run_pages[candidate] = run_pages.get(candidate, 0) + 1
    per_page = [
        {
            "index": index,
            "built": True,
            "shipped_phrase_present": presence,
            "shipped_phrase_occurrences": occurrences,
            "matched_phrase_positions": [],
            "matched_phrase_kinds": [],
            "hidden_subtrees_skipped": None,
            "hidden_selector_class_hits": None,
        }
        for index, (presence, occurrences) in enumerate(phrase_presence)
    ]
    return {
        "provenance": provenance(),
        "pages_read": len(files),
        "per_page": per_page,
        "shipped_phrases": company_root.phrases_shipped(),
        **partition(run_pages),
        "derived_from": "captures already under the gitignored _state/",
    }


def summarise(result: dict[str, Any]) -> int:
    print("")
    print("WHAT LINKEDIN ACTUALLY DRAWS BESIDE THESE COUNTS")
    print("=" * 78)
    print("pages read: %d" % result["pages_read"])
    print("")
    print("HALF ONE -- IS EACH SHIPPED PHRASE PRESENT IN THE PAGE TEXT?")
    for phrase in result["shipped_phrases"]:
        hits = sum(
            1
            for page in result["per_page"]
            if page.get("built")
            and page.get("shipped_phrase_present", {}).get(phrase)
        )
        counts = [
            page.get("shipped_phrase_occurrences", {}).get(phrase, 0)
            for page in result["per_page"]
            if page.get("built")
        ]
        print(
            "  %-42s present on %d of %d   occurrences per page: %s"
            % (phrase, hits, result["pages_read"], counts)
        )
    print("")
    print("  **OCCURRENCES ABOVE 1 ARE THE FINDING.** A company Page draws")
    print("  this line once per RECOMMENDED ORGANISATION as well as for the")
    print("  subject Page, and each names a different organisation.")
    print("  dom.COUNT_LINES_JS keeps ONE best match per phrase -- shortest")
    print("  container wins -- and publishes it with no record that anything")
    print("  competed. company_root's `disagreement` state cannot see this:")
    print("  it compares different PHRASE POSITIONS, and the collapse here is")
    print("  between occurrences of the SAME phrase, inside the page.")
    print("")
    print("  per page: matched phrase positions / hidden-class hits")
    for page in result["per_page"]:
        if not page.get("built"):
            continue
        print(
            "    page %02d  positions=%-12s kinds=%-46s hidden_skipped=%-3s "
            "hidden_class_hits=%s"
            % (
                page["index"],
                page["matched_phrase_positions"],
                ",".join(page["matched_phrase_kinds"]) or "-",
                page["hidden_subtrees_skipped"],
                page["hidden_selector_class_hits"],
            )
        )
    print("")
    print("HALF TWO -- RUNS CARRYING 'connection' OR 'follow'")
    print("")
    print("  **NOT PRINTED HERE, AND THE SUITE IS WHY.**")
    print("  tests/test_page_text_is_never_printed.py flagged the first")
    print("  version of this function: a vocabulary-clean run is STILL")
    print("  something LinkedIn wrote, and that guard's own red says to emit")
    print("  a count, a relation or a marker rather than to widen its")
    print("  inventory. It is right. The runs go to the gitignored json and")
    print("  a reader who needs the wording opens that, deliberately, rather")
    print("  than receiving it in a terminal they did not choose.")
    print("")
    counts = sorted(result["cross_page_runs"].values(), reverse=True)
    print("  vocabulary-clean distinct runs: %d" % len(result["cross_page_runs"]))
    print("  their page-hit counts:          %s" % (counts or "[]"))
    print(
        "  WITHHELD: %d distinct run(s), %d page-hits, carrying at least one "
        "token this package never wrote down."
        % (
            result["runs_withheld_out_of_vocabulary"],
            result["withheld_page_hits_total"],
        )
    )
    print("=" * 78)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--orgs", type=int, default=6)
    parser.add_argument(
        "--no-raw",
        action="store_true",
        help="do not keep the raw html (it is gitignored either way)",
    )
    parser.add_argument("--out", default=None)
    parser.add_argument(
        "--from-raw",
        action="store_true",
        help=(
            "re-derive from captures already under _state/, at zero page "
            "loads. Use this to re-apply a changed filter."
        ),
    )
    args = parser.parse_args()

    destination = Path(args.out or (REPO / "_state" / "company-root-wording.json"))
    if args.from_raw:
        result = from_raw(REPO / "_state" / "company-root-wording")
    else:
        result = asyncio.run(run(args.orgs, not args.no_raw))
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    code = summarise(result)
    print("")
    print("git head: " + str(result["provenance"]["git_head"]))
    print("raw json: " + destination.name + " (gitignored _state/)")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
