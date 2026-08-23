"""Turn the captured follow surfaces into frozen, sanitised fixtures.

Kept as the PROVENANCE of the four "following" fixtures, the same way
``_build_job_fixtures.py`` is the provenance of the job_detail ones: it is
the exact record of what was removed from the live capture and what was
renamed, which is the thing a privacy review needs and cannot get from the
output alone.

The raw captures it reads are deliberately NOT committed -- they carry his
name, the real Pages he follows, the real employer of the posting, media
urls, member ids and tracking tokens. Re-run it only after re-capturing, and
read the tables below before trusting it on a page with a different shape.

Four renders are kept, and each one is here to pin a different claim:
  manage_pages_following.html          - "Manage Pages" caught BEFORE the list
                                         settled. It renders 10 of the rows.
  manage_pages_following_hydrated.html - the same page settled: 20 rows.
                                         The 10-vs-20 gap is the whole point
                                         of the pair and is NOT normalised.
                                         A reader that takes the first render
                                         as the answer reports "he does not
                                         follow X" about eight companies he
                                         does follow, and reports it with no
                                         error, which is the failure this
                                         pair exists to make reproducible.
  job_detail_following.html            - a posting from a company he follows,
                                         caught BEFORE settling. The follow
                                         state is simply ABSENT here: there is
                                         a Save button and no Following
                                         button. That absence is preserved on
                                         purpose -- a reader must report "not
                                         known yet", never "not following".
  job_detail_following_hydrated.html   - the same posting settled, where the
                                         Following button does exist.

WHAT SURVIVES ON PURPOSE. The accessible names are the anchors a parser is
meant to read, so they are kept byte-identical apart from the company name
inside them: ``aria-label="Click to stop following <Company>"``,
``aria-label="Following"``, ``aria-label="Save the job"``, each with its
class attribute untouched. So is the ``/company/<id>/`` link in every row,
because that is what says WHICH Page the row is about, and the document
<title>.

WHAT DOES NOT SURVIVE. His name and vanity, the 20 real Pages, their real
company ids and slugs, the posting's real employer / title / id, the other
employers the posting names in passing, urns, member ids, tracking tokens,
media urls, and every non-ASCII byte.

FOLLOWER COUNTS ARE NEUTRALISED, and the reasoning is worth keeping because
the obvious argument points the wrong way. The instinct is consistency: the
already-committed ``job_detail_hydrated.html`` carries "5,288,656 followers",
so redacting only these four looks like an inconsistent bar. It is not the
same axis. The risk here is not per-item, it is in the SET. One count on one
page is a weak identifier with nothing to cross it against; twenty exact
counts standing together -- 1,730,001 and 4,594,604 and 6,541,445 and 988 and
404 among them -- are a JOINT KEY that reconstructs the real follow list even
with every name replaced, which is precisely the thing this sanitisation
exists to hide. So ``scrub()`` replaces the digits with a fixed placeholder
and keeps the word, because the line's presence is part of the row structure
a parser reads; and ``check`` asserts ZERO real counts rather than reporting
them as a residual.

The older job_detail fixtures still carry one count each. That was DECIDED,
not overlooked: they are frozen, other tests assert against them, and a lone
count is the weak-identifier case this ruling explicitly distinguishes.

WHAT IS STILL CARRIED, named so it is not mistaken for an oversight: the
posting's company blurb and its employee counts ("14,704 Total employees")
survive in the two job fixtures. Those are the ITEM case -- one already-renamed
company on one page -- and they match what the committed job_detail fixtures
carry.

Usage:
    python scripts/_build_follow_fixtures.py            # build, then check
    python scripts/_build_follow_fixtures.py FILE...    # check FILEs only

The second form is what makes the check falsifiable: it runs the identical
code path against any file, including a raw capture, and a raw capture must
fail it.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SRC = Path("_audit")
OUT = Path("tests/fixtures")


#: The Pages he actually follows, and the invented Pages that replace them.
#: (real name, invented name, real company id, invented company id).
#: The list is consumed LONGEST-REAL-NAME-FIRST -- "Codeharbor.com" and
#: "Kestrel Software Services" share a word and "Norvale" is five characters, so a
#: careless order leaves half-substituted wreckage rather than a clean rename.
#: ``_assert_substitution_is_safe`` proves the order is enough instead of
#: assuming it.
FOLLOWED_PAGES = [
    ("Marrowfield Media - A Creator Marketing Platform Co.",
     "Marrowfield Media - A Creator Marketing Platform Co.", "5820114", "5820114"),
    ("Thornbury Management Consultants", "Thornbury Management Consultants", "4471905", "4471905"),
    ("Kestrel Software Services", "Kestrel Software Services", "27419063", "27419063"),
    ("Fernhollow Technology", "Fernhollow Technology", "26105338", "26105338"),
    ("Bastionwood Ventures", "Bastionwood Ventures", "27553102", "27553102"),
    ("Codeharbor.com", "Codeharbor.com", "84120775", "84120775"),
    ("Lanternfly Media", "Lanternfly Media", "61903442", "61903442"),
    # The trademark sign is part of the captured accessible name, so the entry
    # carries it and is applied before the bare spelling. Dropping it here is
    # what leaves a stray non-ASCII byte for the encoder to choke on later.
    ("Coinferry\u2122", "Coinferry", "20387164", "20387164"),
    ("Farfield Labs", "Farfield Labs", "43902517", "43902517"),
    ("Keelstone", "Keelstone", "88410926", "88410926"),
    ("Gridwell", "Gridwell", "902611", "902611"),
    ("Verityne", "Verityne", "66208431", "66208431"),
    ("Talentcove", "Talentcove", "29604118", "29604118"),
    ("Wayfarely", "Wayfarely", "508933", "508933"),
    ("Vantagara", "Vantagara", "87332095", "87332095"),
    ("Vantrex Systems", "Vantrex Systems", "610427", "610427"),
    ("Brightloom", "Brightloom", "28871450", "28871450"),
    ("GitHub", "Forgevault", "3067452", "3067452"),
    ("Recruix", "Recruix", "80215647", "80215647"),
    ("Norvale", "Norvale", "79004613", "79004613"),
    ("Coinferry", "Coinferry", "20387164", "20387164"),
]


#: Vanity slugs. The rows themselves link by numeric id, but the posting links
#: its employer by slug (/company/vantrex-systems/life/) and the logo urls spell the
#: slug out, so the slug is a second, quieter spelling of the same name.
#: fernhollow-technology is not in the brief's list; it is in the capture, and a
#: slug that names a Page he follows belongs here whether or not it was named.
SLUGS = [
    ("brightloom-labs", "brightloom-labs"),
    ("veritynelabs", "veritynelabs"),
    ("thelanternflymedia", "thelanternflymedia"),
    ("fernhollow-technology", "fernhollow-technology"),
    ("gridwell-com", "gridwell-com"),
    ("codeharborcom", "codeharborcom"),
    ("keelstone", "keelstone"),
    ("vantrex-systems", "vantrex-systems"),
    ("recruixinc", "recruixinc"),
    ("brightmoor-consulting", "brightmoor-consulting"),
    ("hollingsworth-global", "hollingsworth-global"),
    ("redlark-digital", "redlark-digital"),
    ("github", "forgevault"),
]


#: Him. None of these survive in the extracted regions today -- the nav that
#: carries his name sits outside <main> -- but they stay in the table because
#: "the region happened not to include it" is a property of one capture, not
#: a property of the script.
OPERATOR = [
    ("alex-rivera-8c21", "alex-rivera-8c21"),
    ("Alex Rivera", "Alex Rivera"),
    ("Rivera", "Rivera"),
    ("Alex R", "Alex R"),
    ("Sundeep", "Alex"),
]


#: The posting itself: employer is handled by FOLLOWED_PAGES (its employer is
#: one of the Pages he follows, which is exactly why this posting was picked),
#: so what is left is the title and the job id.
POSTING = [
    # The ATS apply link spells the title with hyphens for spaces and carries
    # the employer's own requisition id. Both are the REAL posting and both
    # survived a check that reported 69/69 forbidden strings absent, because
    # the list held only the spaced spelling. Kept ABOVE the spaced entries so
    # the longest form is consumed first.
    ("Settlement-Platform-Analyst---Card-Rails--Terminals---Digital-Wallets",
     "Settlement-Platform-Analyst---Card-Rails--Terminals---Digital-Wallets"),
    ("JR9900001", "JR9900001"),
    ("VantrexSystemsCareers", "VantrexSystemsCareers"),
    ("Settlement Platform Analyst", "Settlement Platform Analyst"),
    ("Card Rails, Terminals &amp; Digital Wallets",
     "Card Rails, Terminals &amp; Digital Wallets"),
    ("Platform Analyst", "Platform Analyst"),
    ("4600000117", "4600000117"),
]


#: His real city, in both spellings the capture uses: the posting's metadata
#: line and the ATS apply path, where it is glued to the employer's real
#: office campus. The replacement keeps the SHAPE -- city, region, country --
#: because the location is part of the structure the posting parser reads, and
#: it borrows the invented geography the committed profile fixtures already
#: use rather than inventing a second one.
LOCATION = [
    ("Riverton, Fairhaven, United States", "Riverton, Fairhaven, United States"),
    ("Riverton---North-Gateway-campus", "Riverton---North-Gateway-campus"),
]


#: Real employers the captured posting names in passing -- the competitor
#: paragraph in the company insights lists them. Same reasoning as the job
#: fixtures: renaming only the subject of the capture leaves a fixture that is
#: anonymous exactly where somebody remembered to look.
OTHER_EMPLOYERS = [
    ("Hollingsworth Global", "Hollingsworth Global"),
    ("Brightmoor Consulting", "Brightmoor Consulting"),
    ("Redlark Digital", "Redlark Digital"),
]


#: The posting's diversity statement renders the employer with its first
#: letter in its own <em>, so "SANTREX SYSTEMS'S" is split across tags and a plain
#: name replacement walks straight past it. The repair is spelled out as the
#: exact captured bytes rather than as a clever regex, because the only thing
#: that makes it correct is that it matches this capture.
SPLIT_CAPS = [
    ("<strong><em>S </em></strong><strong><em>ANTREX SYSTEMS\u2019S",
     "<strong><em>V </em></strong><strong><em>ANTREX SYSTEMS\u2019S"),
]


#: What a follower count is replaced with. Fixed, not shape-preserving:
#: rendering "404" as "NNN" and "6,541,445" as "N,NNN,NNN" would leak the
#: magnitude, and an order of magnitude is itself a partial key across twenty
#: rows. The comma is kept so the string still looks like the number a parser
#: expects to find there.
FOLLOWER_PLACEHOLDER = "NNN,NNN followers"


def cut_trailing_rail(html: str) -> str:
    """Drop LinkedIn's "More jobs" rail and everything after it.

    The rail is a list of OTHER employers' postings, decorated with facts
    about his own network. None of it is part of the posting and nothing here
    reads it, so a committed fixture has no business carrying it. On this
    capture the rail also happens to sit BELOW the Following button, so the
    cut is safe -- ``check`` counts that button rather than trusting the
    sentence you just read.
    """
    marker = html.find(">More jobs<")
    if marker < 0:
        return html
    open_at = html.rfind("<div", 0, marker)
    # Chromium repairs the unbalanced tail on set_content; the closing main is
    # spelled out so the reader still finds the element it selects on.
    return html[:open_at] + "</main>"


def balanced_div(html: str, start: int) -> str:
    """Return the whole <div> that begins at ``start``, tags balanced."""
    depth, i = 0, start
    for m in re.finditer(r"<(/?)div\b[^>]*?(/?)>", html[start:]):
        if m.group(2) == "/":
            continue
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return html[start : start + m.end()]
    return html[start : start + 200_000]


def title_of(html: str) -> str:
    """The document title, wrapped in the <head> a reader looks for."""
    found = re.search(r"<title>(.*?)</title>", html, re.S)
    return "<head><title>" + found.group(1) + "</title></head>" if found else ""


def region(html: str) -> str:
    """The job-detail region alone, wrapped in the <main> a reader looks for.

    Copied from ``_build_job_fixtures.py``. Note that THESE two captures carry
    no ``data-view-name`` at all -- LinkedIn served this posting without the
    instrumentation -- so this always takes the <main> fallback here. That is
    checked, not assumed: both buttons the fixtures exist for were confirmed
    to sit inside <main> before the fallback was accepted, and ``check``
    re-confirms it on every build.
    """
    marker = html.find('data-view-name="job-detail-page"')
    if marker < 0:
        start = html.find("<main")
        end = html.find("</main>")
        body = html[start : end + 7] if start >= 0 else html
        return title_of(html) + body
    open_at = html.rfind("<div", 0, marker)
    return title_of(html) + '<main id="workspace">' + balanced_div(html, open_at) + "</main>"


def pages_region(html: str) -> str:
    """The Manage Pages list alone: the <main> that holds the follow rows.

    The rows, the "N Pages" heading above them and the pager below them all
    live inside a single <main>, and the rest of the 1.5 MB document is the
    global nav, the notification tray and LinkedIn's inline data payload --
    all of which carry his name and none of which any reader here touches.
    """
    start = html.find("<main")
    end = html.find("</main>")
    body = html[start : end + 7] if start >= 0 else html
    return title_of(html) + body


def strip(html: str) -> str:
    for tag in ("script", "style", "svg", "noscript"):
        html = re.sub(rf"<{tag}\b.*?</{tag}>", "", html, flags=re.S | re.I)
    html = re.sub(r"<img\b[^>]*>", "", html, flags=re.I)
    return html


def scrub(html: str) -> str:
    """Remove every opaque identifier. The guards match SHAPES, so must this."""
    html = re.sub(r"https://media\.licdn\.com/[^\"'\s]*", "", html)
    # Tracking tokens: the parameter is dropped entirely rather than given a
    # placeholder, because a placeholder long enough to read still matches the
    # guard's shape -- and a fixture that needs an exemption to pass a privacy
    # check is a fixture that should not carry the thing.
    html = re.sub(r"[?&][Tt]rackingId=[^\"'&\s]*", "", html)
    html = re.sub(r"[Tt]rackingId=[^\"'&\s]*", "", html)
    # The external-apply redirect carries two more opaque values under names
    # the trackingId rule does not know: a signed MAC (mt=, ~100 chars) and a
    # short url hash. Same treatment as trackingId -- dropped outright, not
    # placeholdered. The lookbehind stops "mt=" matching inside a longer name.
    html = re.sub(r"(?<![A-Za-z0-9])mt=[^\x22\x27&\s]*", "", html)
    html = re.sub(r"(?<![A-Za-z0-9])urlhash=[^\x22\x27&\s]*", "", html)
    html = re.sub(r"urn(?::|%3A)li(?::|%3A)[A-Za-z0-9_%():,.-]*", "URN-REMOVED", html)
    html = re.sub(r"\bACoAA[A-Za-z0-9_-]{20,}", "MEMBER-ID-REMOVED", html)
    for real, invented in OTHER_EMPLOYERS:
        html = html.replace(real, invented)
    # Relationship counts are facts about HIS network, not about the posting.
    html = re.sub(
        r"\d+ (connection|school alumni|colleague)s? works? here",
        "connections work here",
        html,
    )
    # Follower counts, for the set reason in the module docstring. The word is
    # kept and only the digits go, so the element a parser walks is unchanged.
    html = re.sub(r"[\d,]+ followers", FOLLOWER_PLACEHOLDER, html)
    return html


def to_ascii(html: str) -> str:
    return "".join(c if ord(c) < 128 else f"&#{ord(c)};" for c in html)


def sanitise(html: str) -> str:
    for old, new in SPLIT_CAPS:
        html = html.replace(old, new)
    for old, new in OPERATOR:
        html = html.replace(old, new)
    for old, new in POSTING:
        html = html.replace(old, new)
    for old, new in LOCATION:
        html = html.replace(old, new)
    for real, invented, real_id, invented_id in FOLLOWED_PAGES:
        html = html.replace(real, invented)
        html = html.replace(real_id, invented_id)
    for old, new in SLUGS:
        html = html.replace(old, new)
    return html


# --------------------------------------------------------------------------
# The check. It is the deliverable, not the files alone.
# --------------------------------------------------------------------------

#: The token list enforced by tests/test_sdui_surfaces_fixture.py, verbatim.
#: If that test's list grows, this one must grow with it.
BANNED_BY_THE_FIXTURE_TEST = [
    "sundeep", "redacted", "redacted", "redacted", "redacted", "redacted",
    "redacted", "redacted", "redacted", "redacted", "redacted", "redacted",
    "redacted",
]


#: Everything that must be absent from a sanitised file. Searched
#: case-insensitively, because "Github" and "github" are the same leak.
FORBIDDEN = (
    [real for real, _, _, _ in FOLLOWED_PAGES]
    + [real_id for _, _, real_id, _ in FOLLOWED_PAGES]
    + [slug for slug, _ in SLUGS]
    + [old for old, _ in OPERATOR]
    + [old for old, _ in POSTING]
    + [real for real, _ in OTHER_EMPLOYERS]
    + [old for old, _ in LOCATION]
    + ["ANTREX SYSTEMS", "Fairhaven"]
    # Verbatim from tests/test_sdui_surfaces_fixture.py, which parametrises
    # over EVERY file in tests/fixtures/ and therefore over these four. It is
    # copied rather than referenced so this script stays standalone, and it is
    # here PERMANENTLY so this check is a SUPERSET of that test rather than a
    # second opinion beside it. That separation is the actual defect this
    # round found: 69 strings here and 13 there were two independent lists,
    # and the one this script did not know about is the one that failed.
    + BANNED_BY_THE_FIXTURE_TEST
)
# De-duplicated, order preserved: the Coinferry entry appears twice in
# FOLLOWED_PAGES (with and without its trademark sign) and shares a company id
# with itself, so without this the denominator counts one string twice and the
# "N/N absent" line quietly overstates what was checked.
FORBIDDEN = list(dict.fromkeys(FORBIDDEN))

#: Spelled as constants so the check compares the EXACT accessible name,
#: quotes included, rather than a regex that would also match a longer label.
FOLLOWING_LABEL = 'aria-label="Following"'
SAVE_LABEL = 'aria-label="Save the job"'

EXPECTED_ROWS = {
    "manage_pages_following.html": 10,
    "manage_pages_following_hydrated.html": 20,
}


def variants(needle: str) -> set[str]:
    """The URL and slug spellings of ``needle`` that mean the same thing.

    A committed fixture leaked the real job title for exactly this reason: the
    forbidden list held "Settlement Platform Analyst" and the ATS apply link
    spelled it "Acquiring-Solution-Designer---Merchant-Payments--...". The
    check said 69/69 absent and was telling the truth about the wrong strings.

    Short results are dropped: two-character fragments match everything and
    would turn the sweep into noise nobody reads.
    """
    out = {needle}
    for sep in ("-", "--", "---", "%20", "+", "_", ""):
        out.add(needle.replace(" ", sep))
    out.add(needle.replace(".", "%2E"))
    out.add(needle.replace(",", "%2C"))
    out.add(needle.replace("&", "%26"))
    return {v for v in out if len(v) >= 5}


def _assert_substitution_is_safe() -> None:
    """No invented value may contain a real one.

    Longest-first ordering only helps if the REPLACEMENTS are clean too: an
    invented company id that happened to contain a real one would be
    re-substituted by a later pass and silently corrupted. Cheaper to prove
    than to debug in a diff.
    """
    reals = [r for r, _, _, _ in FOLLOWED_PAGES] + [i for _, _, i, _ in FOLLOWED_PAGES]
    reals += [s for s, _ in SLUGS] + [o for o, _ in OPERATOR]
    reals += [o for o, _ in POSTING] + [o for o, _ in OTHER_EMPLOYERS]
    invented = [i for _, i, _, _ in FOLLOWED_PAGES] + [i for _, _, _, i in FOLLOWED_PAGES]
    invented += [s for _, s in SLUGS] + [n for _, n in OPERATOR]
    invented += [n for _, n in POSTING] + [n for _, n in OTHER_EMPLOYERS]
    bad = [(inv, real) for inv in invented for real in reals if real in inv]
    if bad:
        raise SystemExit("substitution table is not safe: " + ascii(bad))


def check(paths: list[Path]) -> bool:
    """Print the sanitisation report for ``paths``. Return True if all pass.

    Run it against a RAW capture and it must fail; a check that has only ever
    passed certifies nothing.
    """
    ok = True
    for path in paths:
        raw = path.read_bytes()
        try:
            text = raw.decode("ascii")
            pure_ascii = True
        except UnicodeDecodeError:
            text = raw.decode("utf-8", "replace")
            pure_ascii = False
        low = text.lower()

        print("=" * 72)
        print(f"FILE  {path}")
        print(f"      {len(raw)} bytes   pure ASCII: {'yes' if pure_ascii else 'NO'}")
        if not pure_ascii:
            ok = False

        rows = len(re.findall(r'aria-label="Click to stop following ', text))
        print(f"      aria-label=\"Click to stop following ...\" : {rows}")
        print(f"      aria-label=\"Following\"                   : "
              f"{text.count(FOLLOWING_LABEL)}")
        print(f"      aria-label=\"Save the job\"                : "
              f"{text.count(SAVE_LABEL)}")
        # The row's company link is what says WHICH Page the row is about, so
        # it is counted next to the button rather than left to inspection.
        print(f"      /company/ links (row identity)           : "
              f"{len(re.findall(r'/company/[A-Za-z0-9._-]+', text))}")
        print(f"      data-view-name                          : {text.count('data-view-name')}")
        print(f"      urn:li                                  : "
              f"{len(re.findall(r'urn(?::|%3A)li(?::|%3A)', text, re.I))}")
        print(f"      trackingId                              : "
              f"{len(re.findall(r'[Tt]rackingId=', text))}")
        print(f"      media.licdn.com                         : {low.count('media.licdn.com')}")
        print(f"      ACoAA member ids                        : "
              f"{len(re.findall(r'ACoAA[A-Za-z0-9_-]{10,}', text))}")

        expected = EXPECTED_ROWS.get(path.name)
        if expected is not None:
            verdict = "PASS" if rows == expected else "FAIL"
            if rows != expected:
                ok = False
            print(f"      ROW COUNT {verdict}: expected {expected}, found {rows}")

        # ascii() not repr(): one of the forbidden strings carries a
        # trademark sign, and this report is itself committed ASCII.
        print("      -- forbidden strings (case-insensitive) --")
        failed = 0
        for needle in FORBIDDEN:
            hits = low.count(needle.lower())
            if hits:
                failed += 1
                ok = False
                print(f"         FAIL  {ascii(needle)}  x{hits}")
        print(f"      {len(FORBIDDEN) - failed}/{len(FORBIDDEN)} forbidden strings absent"
              f"  ->  {'PASS' if failed == 0 else str(failed) + ' FAILED'}")

        # Same list again, in every URL and slug spelling of itself. This is
        # the pass that would have caught the hyphenated job title, and it is
        # reported separately so a regression here is not hidden inside the
        # literal count.
        variant_hits = []
        checked = 0
        for needle in FORBIDDEN:
            for spelling in variants(needle):
                checked += 1
                if spelling.lower() == needle.lower():
                    continue  # already covered by the literal pass above
                if spelling.lower() in low:
                    variant_hits.append((needle, spelling))
        if variant_hits:
            ok = False
            for needle, spelling in variant_hits:
                print(f"         FAIL  {ascii(needle)} spelled {ascii(spelling)}")
            print(f"      VARIANT SWEEP FAIL: {len(variant_hits)} of {checked} "
                  f"spellings present")
        else:
            print(f"      VARIANT SWEEP PASS: 0 of {checked} url/slug spellings "
                  f"present")

        # Follower counts are neutralised, so the assertion is ZERO. This is
        # the line a raw capture has to fail on: it is the only check here
        # that would still pass if scrub() silently stopped doing this.
        leaked = re.findall(r"[\d,]{3,} followers", text)
        placeholders = text.count(FOLLOWER_PLACEHOLDER)
        if leaked:
            ok = False
            print(f"      FOLLOWER COUNTS FAIL: {len(leaked)} real count(s) present, "
                  f"e.g. {ascii(leaked[0])}")
        else:
            # Printed even when the render carries no count at all: a line that
            # silently disappears is indistinguishable from a check that did
            # not run.
            print(f"      FOLLOWER COUNTS PASS: 0 real, "
                  f"{placeholders} neutralised to {ascii(FOLLOWER_PLACEHOLDER)}")
    print("=" * 72)
    print(f"OVERALL: {'PASS' if ok else 'FAIL'}")
    return ok


def main() -> None:
    _assert_substitution_is_safe()

    # A non-zero exit is what lets this be wired into anything. It also makes
    # the deliberate-failure demo checkable by exit code rather than by
    # reading the prose.
    if len(sys.argv) > 1:
        raise SystemExit(0 if check([Path(a) for a in sys.argv[1:]]) else 1)

    builds = [
        ("_probe-manage-pages-pre.html", "manage_pages_following.html", pages_region),
        ("_probe-manage-pages-hyd.html", "manage_pages_following_hydrated.html", pages_region),
        ("_probe-job-followed-company-pre.html", "job_detail_following.html", region),
        ("_probe-job-followed-company-hyd.html", "job_detail_following_hydrated.html", region),
    ]
    out_paths = []
    for src, dest, extract in builds:
        raw = (SRC / src).read_text(encoding="utf-8")
        body = extract(raw)
        if extract is region:
            body = cut_trailing_rail(body)
        # encode("ascii") is the last gate on purpose: if it raises, something
        # was not substituted, and the fix is the substitution -- never a
        # wider encoder.
        (OUT / dest).write_bytes(to_ascii(sanitise(scrub(strip(body)))).encode("ascii"))
        out_paths.append(OUT / dest)

    if not check(out_paths):
        raise SystemExit(1)


main()
