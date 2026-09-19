"""Turn the captured job posting into frozen, sanitised fixtures.

Kept as the PROVENANCE of the three job_detail fixtures: it is the exact
record of what was removed from the live capture and what was renamed, which
is the thing a privacy review needs and cannot get from the output alone.

The raw captures it reads are deliberately NOT committed -- they carry the
real employer, real other employers, media urls and tracking tokens. Re-run
it only after re-capturing, and read the scrub list below before trusting it
on a page with a different shape.

Three renders are kept, and the test module says why each is there:
  job_detail_hydrated.html - the settled page as LinkedIn served it.
  job_detail.html          - the same render with LinkedIn's data-view-name
                             instrumentation removed. A parser that reads
                             structure agrees across the two; one that quietly
                             anchors on the instrumentation returns nothing
                             here, which has happened on this repo before.
  job_detail_shell.html    - the document BEFORE the content renders. Its job
                             is to prove a failed read is reported as one.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

SRC = Path("_audit")
OUT = Path("tests/fixtures")

#: THE INVENTED SIDE ONLY. The real side of both tables lives in
#: :data:`KEY_PATH`, gitignored, paired BY INDEX -- the same split as
#: ``_build_follow_fixtures.py``, for the same reason.
#:
#: THIS IS THE SECOND SANITISATION SCRIPT IN THIS REPO TO HAVE SHIPPED ITS OWN
#: KEY, and the way it was found is the point. A cold review swept every
#: tracked file against a list of real strings and did NOT flag this file --
#: not through carelessness, but because its list was built from the
#: Manage-Pages capture and a value list cannot name a value nobody has seen.
#: It was found by ``tests/test_no_committed_identity.py``, which hunts the
#: SHAPE of a key -- a table pairing fixture content with something absent
#: from every fixture -- and therefore needs to know nothing about what it is
#: looking for.
KEY_PATH = Path("_audit/_sanitisation_key.json")

SUBS_INVENTED = [
    'Ashgrove Systems',
    'ashgrove-systems',
    '4600000042',
]


#: Employers the captured page names in passing -- the "More jobs" rail and
#: the company blurb both list them. Renaming only the subject of a capture
#: leaves a fixture that is anonymous exactly where somebody remembered to
#: look.
OTHER_EMPLOYERS_INVENTED = [
    'Northwind Capital',
    'Larkspur Travel',
    'Draywood Motors',
    'Pennyfield Foods',
    'Halloway Insure',
    'Tessellate Labs',
    'Bracken Storage',
    'Windmere Software',
    'Aldermill Learning',
    'Quillon Tech',
]


def _load_key() -> dict:
    if not KEY_PATH.exists():
        raise SystemExit(
            "\n".join(
                (
                    f"the sanitisation key is missing: {KEY_PATH}",
                    "It is gitignored on purpose -- it is what reverses the",
                    "committed fixtures. Without it this script cannot say what",
                    "it removes, and a sanitiser that cannot name what it",
                    "removes passes everything.",
                )
            )
        )
    return json.loads(KEY_PATH.read_text(encoding="utf-8"))


def _pair(real: list, invented: list, what: str) -> list:
    if len(real) != len(invented):
        raise SystemExit(
            f"the {what} table has {len(invented)} invented entries and the "
            f"key has {len(real)} real ones. They are paired BY INDEX, so a "
            "mismatch means one side was edited alone."
        )
    return list(zip(real, invented))


_KEY = _load_key()
SUBS = _pair(_KEY["job_fixture_subs"], SUBS_INVENTED, "job_fixture_subs")
OTHER_EMPLOYERS = _pair(
    _KEY["job_fixture_other_employers"],
    OTHER_EMPLOYERS_INVENTED,
    "job_fixture_other_employers",
)


def cut_trailing_rail(html: str) -> str:
    """Drop LinkedIn's "More jobs" rail and everything after it.

    The rail is a list of OTHER employers' postings, decorated with facts
    about his own network ("1 connection works here", "1 school alumni works
    here"). None of it is part of the posting and nothing here reads it, so a
    committed fixture has no business carrying it. The headings ABOVE it stay
    on purpose: the description has to be shown stopping somewhere, and a
    boundary test against a fixture with no boundary in it proves nothing.
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


def region(html: str) -> str:
    """The job-detail region alone, wrapped in the <main> a reader looks for."""
    # The document title is kept with the region. It is not decoration: it is
    # the only place the page states the job title and the employer in one
    # canonical string, and it is what lets the title be recovered when the
    # title itself contains the separator ("Backend Engineer | Remote").
    title = ""
    found = re.search(r"<title>(.*?)</title>", html, re.S)
    if found:
        title = "<head><title>" + found.group(1) + "</title></head>"
    marker = html.find('data-view-name="job-detail-page"')
    if marker < 0:
        start = html.find("<main")
        end = html.find("</main>")
        body = html[start : end + 7] if start >= 0 else html
        return title + body
    open_at = html.rfind("<div", 0, marker)
    return title + '<main id="workspace">' + balanced_div(html, open_at) + "</main>"


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
    return html


def to_ascii(html: str) -> str:
    return "".join(c if ord(c) < 128 else f"&#{ord(c)};" for c in html)


def sanitise(html: str) -> str:
    for old, new in SUBS:
        html = html.replace(old, new)
    return html


def _only(matches) -> Path:
    """The single capture matching a glob, or a refusal naming the count."""
    found = sorted(matches)
    if len(found) != 1:
        raise SystemExit(
            f"expected exactly one capture, found {len(found)}: "
            f"{[p.name for p in found]}"
        )
    return found[0]


def main() -> None:
    # Globbed rather than named: the capture filenames spell the REAL job
    # id, which is one of the values this script exists to remove. A
    # sanitiser is not allowed to carry its own input's identity either.
    raw_hyd = _only(SRC.glob("_probe-job-*-hyd.html")).read_text(encoding="utf-8")
    raw_pre = _only(SRC.glob("_probe-job-*-pre.html")).read_text(encoding="utf-8")

    hyd = to_ascii(sanitise(scrub(strip(cut_trailing_rail(region(raw_hyd))))))
    shell = to_ascii(sanitise(scrub(strip(cut_trailing_rail(region(raw_pre))))))
    pre = re.sub(r' data-view-name="[^"]*"', "", hyd)

    (OUT / "job_detail_hydrated.html").write_bytes(hyd.encode("ascii"))
    (OUT / "job_detail.html").write_bytes(pre.encode("ascii"))
    (OUT / "job_detail_shell.html").write_bytes(shell.encode("ascii"))

    for name in ("job_detail.html", "job_detail_hydrated.html", "job_detail_shell.html"):
        s = (OUT / name).read_text(encoding="ascii")
        print(
            f"{name}: {len(s)} chars, view-names={s.count('data-view-name')}, "
            f"urn={len(re.findall(r'urn(?::|%3A)li(?::|%3A)', s, re.I))}, "
            f"tracking={len(re.findall(r'[Tt]rackingId=[A-Za-z0-9%+/=_-]{8,}', s))}, "
            f"leaked={[o for o, _ in SUBS if o in s]}"
        )


if __name__ == "__main__":
    # Guarded: main() WRITES tests/fixtures/, so a bare call meant that
    # importing this module rebuilt three committed fixtures.
    main()
