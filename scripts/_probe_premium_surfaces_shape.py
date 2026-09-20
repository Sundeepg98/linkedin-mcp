"""What six Premium-bearing LinkedIn surfaces actually draw, read OFFLINE.

THE PAGE LOADS ARE ALREADY PAID FOR. On 2026-09-20 a live authenticated
session captured six admitted addresses to ``_state/`` (gitignored). This
re-reads those captures for ever, with no browser, no session and no account
touched, so the next wave spends zero page loads on the same questions.

    jobs-recommended  premium-hub  newsletters
    profile-views     search-appearances  jobs-search

## THE MEASUREMENT THAT DECIDES EVERY NUMBER BELOW

**A NEEDLE IN THE SOURCE IS NOT A NEEDLE ON THE PAGE.** Three of the six
captures are about 1.4 MB, and over 99 percent of that is the Ember bundle,
the i18n dictionaries and the lix blob. Counting ``inmail`` over the raw
document returns 16 to 21 on those pages and **0 on all six once scripts,
styles and LinkedIn's ``<code>`` model payloads are stripped.** The raw count
is a fact about the bundle; only the stripped count is a fact about what was
drawn. Every census here is taken twice and BOTH are printed, because the gap
between them is the finding.

## WHAT LEAVES THIS PROCESS

Integers, booleans, route SHAPES, and needle names this file authors. No page
text, no href verbatim, no accessible name, no member id.

**THE REDUCER'S FIRST VERSION LEAKED AND THAT IS WHY IT LOOKS LIKE THIS.** It
replaced a path segment only when the segment was long or digit-bearing -- so
a member path printed verbatim, because a profile slug is neither. The rule
that works is the opposite one: the segment AFTER a member-bearing prefix is
replaced UNCONDITIONALLY, whatever it looks like. It was found by running the
first version over the real captures and reading a slug off my own stdout,
not by reading the code.

## THE CAPTURES ARE GITIGNORED AND THEIR ABSENCE IS NOT A ZERO

``_state/`` carries no files in a linked worktree, and these documents embed a
member urn inside the lix ``trackingInfo`` blob -- measured, which is the
concrete reason they may never be committed. A run that cannot find them exits
2 and tallies nothing.

Run it as::

    ./venv/Scripts/python.exe scripts/_probe_premium_surfaces_shape.py
    ./venv/Scripts/python.exe scripts/_probe_premium_surfaces_shape.py --control
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from linkedin_server.readonly import is_read_url  # noqa: E402

STATE = ROOT / "_state"

SURFACES = ("jobs-recommended", "premium-hub", "newsletters",
            "profile-views", "search-appearances", "jobs-search")

#: Prefixes whose NEXT path segment addresses a person or an organisation.
MEMBER_BEARING = frozenset({"in", "company", "school", "newsletters", "pub",
                            "profile", "organization", "groups", "showcase"})

#: Generic product vocabulary. Every one of these is a word this file authors.
NEEDLES = ("inmail", "credit", "salary", "top applicant", "applicant",
           "unlock", "upgrade", "premium", "role-play", "interview",
           "recruiter", "who viewed", "insight", "subscribe", "unsubscribe",
           "analytics", "manage", "delete", "edit")

#: An impossible needle. It must stay at 0 on every document, or the census is
#: matching something other than what it says it matches.
SILENT = "qwxzjvpremiumqwxzjv"

STRIPPED_TAGS = ("script", "style", "code", "template", "noscript")

#: Route-shape fragments that would indicate a durable RESULTS address.
RESULT_WORDS = ("history", "results", "completed", "summary", "transcript",
                "report", "score")


def visible_text(html):
    """The document with its bundles removed. LinkedIn parks model JSON in <code>."""
    for tag in STRIPPED_TAGS:
        html = re.sub(r"<%s\b.*?</%s>" % (tag, tag), " ", html, flags=re.S | re.I)
    html = re.sub(r"<!--.*?-->", " ", html, flags=re.S)
    html = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", html)


def shape_path(href, depth=3):
    """An href reduced to a route shape that names nobody."""
    path = re.sub(r"^https?://[^/]+", "", href).split("?")[0].split("#")[0]
    segs = [s for s in path.split("/") if s]
    if not segs:
        return "/"
    out = []
    for i, seg in enumerate(segs[:depth]):
        if i > 0 and segs[i - 1].lower() in MEMBER_BEARING:
            out.append("<entity>")
        elif re.search(r"\d{4,}", seg) or len(seg) > 24:
            out.append("<opaque>")
        else:
            out.append(seg)
    return "/" + "/".join(out)


def lix_treatments(raw, word):
    """Flag -> treatment for every lix key carrying ``word``.

    The treatment is LinkedIn's own enum (``control``, ``enabled``, ...), not
    page prose, and it is the only field read. ``trackingInfo`` is never
    touched: on these captures it carries a member urn.
    """
    text = raw.replace("&quot;", '"')
    pat = re.compile(
        r'"(voyager\.web\.[a-z0-9.\-]+)":\{.*?"treatment":"([^"]{0,40})"')
    found = {}
    for m in pat.finditer(text):
        found.setdefault(m.group(1), m.group(2))
    return found, dict((k, v) for k, v in found.items() if word in k)


def census(raw):
    vis = visible_text(raw)
    low_raw, low_vis = raw.lower(), vis.lower()
    print("    raw=%8d  rendered=%6d  (%.1f%% of the document is drawn text)"
          % (len(raw), len(vis), 100.0 * len(vis) / max(1, len(raw))))
    print("      %-16s %9s %9s" % ("needle", "in source", "rendered"))
    for n in NEEDLES:
        a, b = low_raw.count(n), low_vis.count(n)
        if a or b:
            flag = "   <- SOURCE ONLY" if a and not b else ""
            print("      %-16s %9d %9d%s" % (n, a, b, flag))
    absent = [n for n in NEEDLES if not low_vis.count(n)]
    print("      RENDERED-ABSENT (%d): %s" % (len(absent), ", ".join(absent)))
    print("      %-16s %9d %9d   <- must stay silent"
          % (SILENT, low_raw.count(SILENT), low_vis.count(SILENT)))


def control():
    """Every control, each capable of voiding the run."""
    print("=== CONTROL 1  THE CENSUS CAN SPEAK")
    synth = "<html><body>" + " ".join(
        "<p>%s</p>" % n for n in NEEDLES) + "</body></html>"
    vis = visible_text(synth).lower()
    missed = [n for n in NEEDLES if not vis.count(n)]
    print("    needles named on a document carrying all %d: %d"
          % (len(NEEDLES), len(NEEDLES) - len(missed)))
    if missed:
        print("    VOID -- the census cannot name: %s" % ", ".join(missed))
        return 1
    if vis.count(SILENT):
        print("    VOID -- the silent needle fired on a document without it")
        return 1
    print("    the silent needle stayed at 0.  PASS")

    print("=== CONTROL 2  THE STRIPPER REMOVES A BUNDLE")
    bundled = ("<html><script>%s</script><body><p>drawn</p></body></html>"
               % ("inmail " * 400))
    if visible_text(bundled).lower().count("inmail"):
        print("    VOID -- a needle inside a script block survived the stripper")
        return 1
    if "drawn" not in visible_text(bundled):
        print("    VOID -- the stripper ate the drawn text as well")
        return 1
    print("    a needle x400 inside a script block -> 0 rendered, and the "
          "drawn word survived.  PASS")

    print("=== CONTROL 3  THE REDUCER CHANGES A NAME")
    # EVERY SLUG HERE CARRIES A SANCTIONED SYNTHETIC_SLUG_TOKEN, and the first
    # version of this control did not -- it read `a-person-shaped-slug`, which
    # is slug-SHAPED and undeclared, so the committed-identity guard refused
    # the commit. A shape match means undeclared, never real. Renamed rather
    # than declared, because a declaration permanently widens what the guard
    # tolerates for this file and the rename costs the measurement nothing:
    # what these inputs have to be is short, hyphenated and digit-free, so
    # that the NAIVE length-and-digit rule would wave them through. They still
    # are. Control 3 driven into its failing state still reports 3 leaks.
    cases = (("/in/placeholder-slug", "placeholder-slug"),
             ("/company/example-org-slug/life", "example-org-slug"),
             ("/school/example-campus-slug", "example-campus-slug"),
             ("/jobs/view/4440100935", "4440100935"))
    leaked = [c for c, needle in cases if needle in shape_path(c)]
    for case, _needle in cases:
        print("    %-40s -> %s" % (case, shape_path(case)))
    if leaked:
        print("    VOID -- the reducer passed a name through: %d" % len(leaked))
        return 1
    print("    0 of %d inputs survived the reduction.  PASS" % len(cases))

    print("=== CONTROL 4  A TREATMENT OTHER THAN control IS REPORTABLE")
    blob = ('"voyager.web.alpha-interview-x":{"trackingInfo":null,'
            '"treatment":"enabled","testKey":"x"},'
            '"voyager.web.beta-interview-y":{"trackingInfo":null,'
            '"treatment":"control","testKey":"y"}')
    _all, iv = lix_treatments(blob, "interview")
    vals = sorted(set(iv.values()))
    print("    flags parsed: %d, distinct treatments: %s" % (len(iv), vals))
    if vals != ["control", "enabled"]:
        print("    VOID -- the parser cannot distinguish the two treatments")
        return 1
    print("    a control verdict is therefore a reading, not a default.  PASS")
    print()
    print("control: all four passed -- a zero below is a measurement")
    return 0


def main():
    ap = argparse.ArgumentParser(
        description="six Premium-bearing surfaces, offline")
    ap.add_argument("--control", action="store_true")
    ap.add_argument("--state", default=str(STATE))
    args = ap.parse_args()

    if args.control:
        return control()

    state = Path(args.state)
    caps = dict((s, state / ("cap-%s.html" % s)) for s in SURFACES)
    missing = [s for s, p in caps.items() if not p.exists()]
    if missing:
        print("CAPTURES ABSENT (%d of %d): %s"
              % (len(missing), len(SURFACES), ", ".join(missing)))
        print("An absence is not a zero. _state/ carries no files in a linked "
              "worktree; run this from the main tree.")
        return 2

    docs = dict((s, p.read_text(encoding="utf-8", errors="replace"))
                for s, p in caps.items())

    print("=== 1  WHAT EACH SURFACE DRAWS, IN SOURCE AND RENDERED")
    for s in SURFACES:
        print("  -- %s" % s)
        census(docs[s])

    print()
    print("=== 2  ROUTE SHAPES, AGAINST THE SHIPPED READ ALLOWLIST")
    routes = {}
    for s in SURFACES:
        for href in set(re.findall(r'href="([^"]{1,300})"', docs[s])):
            if href.startswith("#") or href.startswith("mailto"):
                continue
            if href.startswith("http") and "linkedin.com" not in href:
                continue
            routes.setdefault(shape_path(href), set()).add(s)
    admitted = 0
    for shape in sorted(routes):
        try:
            ok = is_read_url("https://www.linkedin.com" + shape + "/")
        except Exception:
            ok = False
        admitted += bool(ok)
        print("    %-9s %-44s %d surface(s)"
              % ("ADMITTED" if ok else "refused", shape, len(routes[shape])))
    print("    %d distinct route shapes, %d admitted, %d refused"
          % (len(routes), admitted, len(routes) - admitted))

    print()
    print("=== 3  THE INTERVIEW FLAGS, AND WHICH SIDE OF THE PRODUCT THEY GATE")
    allf, iv = lix_treatments(docs["jobs-recommended"], "interview")
    print("    lix flags parsed on jobs-recommended: %d" % len(allf))
    print("    distinct treatments across all of them: %d"
          % len(set(allf.values())))
    for k in sorted(iv):
        side = ("HIRING   (recruiter side)" if ".hiring-" in k
                else "LEARNING (member side)  " if "learning-" in k else "OTHER")
        print("      %-52s %-24s %s" % (k.replace("voyager.web.", ""), iv[k], side))
    member = [k for k in iv if "learning-" in k]
    print("    member-side interview flags: %d of %d" % (len(member), len(iv)))

    print()
    print("=== 4  IS A RESULTS ADDRESS DRAWN ANYWHERE?")
    learn = {}
    for s in SURFACES:
        for href in set(re.findall(r'href="([^"]{1,300})"', docs[s])):
            if "/learning" in href or "role-play" in href:
                learn.setdefault(shape_path(href, depth=4), set()).add(s)
    for shape in sorted(learn):
        print("      %-52s %d surface(s)" % (shape, len(learn[shape])))
    hist = [s for s in learn
            if any(w in s.lower() for w in RESULT_WORDS)]
    create = [s for s in learn if s.rstrip("/").endswith("/new")]
    print("    learning/role-play route shapes drawn: %d" % len(learn))
    print("    of those, results/history/transcript-shaped: %d" % len(hist))
    print("    of those, create-shaped (a /new segment): %d" % len(create))
    return 0


if __name__ == "__main__":
    sys.exit(main())
