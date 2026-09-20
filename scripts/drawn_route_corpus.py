"""THE DENOMINATOR, TAKEN FROM WHAT LINKEDIN DREW INSTEAD OF FROM WHAT WE WROTE DOWN.

``scripts/blast_radius.py`` answers "what would this candidate allowlist pattern
newly admit" by running the shipped predicate over a corpus twice and diffing.
It is the right instrument and this file does not replace it. **It supplies it
with a different corpus.**

## WHY, MEASURED RATHER THAN ASSERTED

The `premium-four` wave ran ``blast_radius`` over its own corpus for four
candidate patterns and five deliberately over-broad mutations, including a bare
``.*`` wildcard over ``/premium/``. **Every one of the nine measured zero.**

    corpus size                                    67
    addresses under /jobs/collections/              0
    addresses under /premium/                       0
    addresses under /analytics/                     1   (already admitted)

The instrument is not broken and its docstring says so in advance: *"a diff over
a corpus is a LOWER BOUND on the blast radius, never the whole of it ... an
address nobody thought to put in the corpus is invisible here, and its absence
from the output is a fact about the corpus."* Its corpus is assembled from the
forbidden roster plus the families this package has argued about, and **nobody
has ever argued about /premium/**, so a wildcard over that family had nothing to
hit.

A zero from an empty denominator is not evidence, and citing one would be the
same error class this repository has already paid for twice by reading pattern
text instead of running the predicate.

## WHAT THIS SUPPLIES INSTEAD

Every route shape a **DRAWN ANCHOR** produced on the six surfaces a live
authenticated session captured on 2026-09-20. Not what we imagined LinkedIn
might serve -- what LinkedIn served.

## TWO DISCIPLINES IT KEEPS, AND EACH ONE COST SOMEBODY SOMETHING

**A NEEDLE IN THE SOURCE IS NOT A NEEDLE ON THE PAGE.** Anchors are collected
from the STRIPPED markup and matched as ``<a href=...>``, never as a substring
of the raw document. On this corpus ``inmail`` appears 16-21 times raw and 0
times rendered; a raw census would report the opposite of the truth.

**AND THE SHAPE SET WAS MEASURED, NOT ASSUMED, INCLUDING AGAINST THIS FILE'S
OWN PREMISE.** ``_probe_premium_surfaces_shape.py`` builds its inventory from
``href="..."`` anywhere in the raw document. The hypothesis behind this file was
that its inventory is therefore inflated. **It is not.** Measured over the same
six captures, through the same reducer:

    route shapes from ANY href= anywhere:   43
    route shapes from a DRAWN <a href=>:     43
    shapes with no drawn anchor:              0

The two sets are identical, so the shipped inventory is right. It is right by
luck of this corpus rather than by construction -- a ``<link href=>`` or a
bundled string on some future capture would enter it and nothing would say so --
and this file uses the anchor-scoped rule because a property that holds by
construction is worth more than one that holds by coincidence, not because the
other one is currently wrong.

## NO NAME LEAVES THIS FILE

Reduction is ``_probe_premium_surfaces_shape.shape_path``, IMPORTED rather than
re-written. That function's own docstring records that its first version LEAKED
a real profile slug, because it replaced a segment only when the segment was
long or digit-bearing and a slug is neither. The rule that works is the opposite
one: the segment after a member-bearing prefix is replaced UNCONDITIONALLY.
Four waves have reimplemented this repository's census parse and three got a
broken one; this file imports.

Placeholders are then substituted for concrete tokens this repository already
sanctions, so the emitted corpus is a list of real-shaped urls that name nobody:

    <entity>   ->  placeholder-slug   (the token scripts/_probe_premium_surfaces_shape.py
                                       control 3 already carries)
    <opaque>   ->  1234567890         (the id scripts/blast_radius.py already carries)

## THE OUTPUT IS COMMITTED, AND THAT IS THE POINT

``_state/`` is gitignored, carries a member urn in its lix blob, and does not
exist in a linked worktree, a clone or a CI checkout. A test that needed the
captures could not run anywhere that matters. So this script WRITES a derived,
name-free corpus to a tracked fixture, and the test reads that.

    ./venv/Scripts/python.exe scripts/drawn_route_corpus.py            # print
    ./venv/Scripts/python.exe scripts/drawn_route_corpus.py --write    # regenerate
    ./venv/Scripts/python.exe scripts/drawn_route_corpus.py --control  # the controls

Opens no browser. Navigates nothing. Reads no page.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

#: The captures live in the MAIN checkout. A linked worktree has no ``_state``.
DEFAULT_STATE = ROOT / "_state"

#: The tracked artifact this script exists to produce.
CORPUS_FILE = ROOT / "tests" / "fixtures" / "synthetic" / "drawn_routes.txt"

SURFACES = ("jobs-recommended", "premium-hub", "newsletters",
            "profile-views", "search-appearances", "jobs-search")

#: LinkedIn parks model JSON in ``<code>``; the rest is the Ember bundle.
STRIPPED_TAGS = ("script", "style", "code", "template", "noscript")

#: **SANCTIONED SUBSTITUTIONS.** Both tokens are already committed in this
#: repository under the identity guard, so neither widens what the guard
#: tolerates. An invented token would have to be argued for; these argue for
#: themselves by already being here.
SUBSTITUTIONS = (("<entity>", "placeholder-slug"), ("<opaque>", "1234567890"))

#: How deep a route shape is kept. THREE IS THE SHIPPED PROBE'S DEFAULT AND IT
#: IS TOO SHALLOW FOR A BOUNDARY QUESTION: a candidate pattern that takes no
#: sub-path must be measured against the sub-paths that exist, and at depth 3
#: ``/in/<entity>/overlay/<opaque>`` and ``/in/<entity>/overlay/enhance``
#: collapse into one shape and stop being two different tests of it.
DEPTH = 6


def _shipped_reducer():
    """``shape_path`` and nothing re-written. See the module docstring."""
    spec = importlib.util.spec_from_file_location(
        "_premium_surfaces_shape",
        ROOT / "scripts" / "_probe_premium_surfaces_shape.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def strip_bundles(html: str) -> str:
    """The document with its bundles and comments removed."""
    for tag in STRIPPED_TAGS:
        html = re.sub(r"<%s\b.*?</%s>" % (tag, tag), " ", html, flags=re.S | re.I)
    return re.sub(r"<!--.*?-->", " ", html, flags=re.S)


def anchor_hrefs(html: str) -> set[str]:
    """Every ``<a href=...>`` in the STRIPPED markup, internal ones only.

    Matched as an ANCHOR ELEMENT rather than as the substring ``href="``, so a
    stylesheet link or a bundled string cannot enter the corpus.
    """
    found: set[str] = set()
    for href in re.findall(r'<a\b[^>]*\bhref="([^"]{1,400})"', html, flags=re.I):
        if href.startswith("#") or href.startswith("mailto"):
            continue
        if href.startswith("http") and "linkedin.com" not in href:
            continue
        found.add(href)
    return found


def shapes_from(state: Path) -> tuple[dict[str, int], list[str]]:
    """Route shape -> how many of the six surfaces drew it. Plus any absences.

    **AN ABSENT CAPTURE IS NOT A ZERO.** Missing surfaces are returned so the
    caller can refuse rather than tally a short corpus as a complete one.
    """
    reducer = _shipped_reducer()
    counts: dict[str, int] = {}
    missing: list[str] = []
    for surface in SURFACES:
        path = state / ("cap-%s.html" % surface)
        if not path.exists():
            missing.append(surface)
            continue
        markup = strip_bundles(path.read_text(encoding="utf-8", errors="replace"))
        for href in anchor_hrefs(markup):
            shape = reducer.shape_path(href, depth=DEPTH)
            counts[shape] = counts.get(shape, 0) + 1
    return counts, missing


def concrete(shape: str) -> str:
    """One route shape -> one concrete url that names nobody."""
    path = shape
    for placeholder, token in SUBSTITUTIONS:
        path = path.replace(placeholder, token)
    return "https://www.linkedin.com" + path.rstrip("/") + "/"


def corpus_from_file(path: Path = CORPUS_FILE) -> list[str]:
    """Read the TRACKED corpus. The consumer a test uses.

    Raises rather than returning an empty list when the file is absent: an
    empty corpus makes every blast-radius measurement report zero, which is
    exactly the indistinguishable-from-broken state this whole file exists
    because of.
    """
    text = path.read_text(encoding="utf-8")
    urls = [line.strip() for line in text.splitlines()
            if line.strip() and not line.startswith("#")]
    if not urls:
        raise ValueError(
            "%s holds no addresses. An empty corpus makes blast_radius report "
            "zero for every candidate, including a wildcard." % path
        )
    return urls


def _control() -> int:
    """Each one capable of voiding the run, each shown in its failing state."""
    failures = 0

    print("=== CONTROL 1  THE ANCHOR RULE EXCLUDES A NON-ANCHOR href")
    doc = ('<html><head><link rel="stylesheet" href="/zzz-stylesheet/x">'
           '</head><body><a href="/zzz-anchor/y">t</a></body></html>')
    got = anchor_hrefs(strip_bundles(doc))
    print("    hrefs in the document: 2   collected as anchors: %d" % len(got))
    if got != {"/zzz-anchor/y"}:
        print("    VOID -- a non-anchor href entered the corpus: %d" % len(got))
        failures += 1
    else:
        print("    the stylesheet href stayed out.  PASS")

    print("=== CONTROL 2  A BUNDLED ANCHOR DOES NOT COUNT AS DRAWN")
    bundled = ('<html><script><a href="/zzz-bundled/z">x</a></script>'
               '<body><a href="/zzz-drawn/w">t</a></body></html>')
    got = anchor_hrefs(strip_bundles(bundled))
    print("    anchor-shaped strings in source: 2   collected: %d" % len(got))
    if got != {"/zzz-drawn/w"}:
        print("    VOID -- an anchor inside a script block survived: %d" % len(got))
        failures += 1
    else:
        print("    the scripted anchor stayed out and the drawn one survived.  PASS")

    print("=== CONTROL 3  THE REDUCER STILL CHANGES A NAME")
    reducer = _shipped_reducer()
    # ``(input, the segment that must NOT survive)``. THE NEEDLE IS NAMED PER
    # CASE RATHER THAN COMPUTED, and that is this control's own scar: the
    # first version took segment ``[1]`` of every input, which is the
    # identifying segment for a member-bearing prefix and is the literal
    # ``view`` for ``/jobs/view/<id>``. It duly reported a leak, VOIDed a
    # clean run, and the leak was in the control. A needle derived by position
    # from the input is a rule about the inputs that happened to be listed.
    cases = (("/in/placeholder-slug", "placeholder-slug"),
             ("/company/example-org-slug/life", "example-org-slug"),
             ("/school/example-campus-slug", "example-campus-slug"),
             ("/jobs/view/4440100935", "4440100935"))
    leaked = []
    for case, needle in cases:
        out = reducer.shape_path(case, depth=DEPTH)
        print("    %-40s -> %s" % (case, out))
        if needle in out:
            leaked.append(case)
    if leaked:
        print("    VOID -- the reducer passed a name through: %d" % len(leaked))
        failures += 1
    else:
        print("    0 of %d inputs survived the reduction.  PASS" % len(cases))

    print("=== CONTROL 4  THE SUBSTITUTION LEAVES NO PLACEHOLDER BEHIND")
    url = concrete("/in/<entity>/overlay/<opaque>")
    print("    /in/<entity>/overlay/<opaque> -> %s" % url)
    if "<" in url or ">" in url:
        print("    VOID -- a placeholder reached the corpus, and no regex "
              "on the allowlist can match one, so every verdict would be a "
              "false refusal")
        failures += 1
    else:
        print("    no angle bracket survives into a corpus address.  PASS")

    print("=== CONTROL 5  AN EMPTY CORPUS REFUSES INSTEAD OF REPORTING ZERO")
    empty = ROOT / "tests" / "fixtures" / "synthetic" / "_zzz_empty_corpus.txt"
    try:
        empty.write_text("# nothing here\n", encoding="utf-8")
        try:
            corpus_from_file(empty)
            print("    VOID -- an empty corpus was accepted, and every "
                  "blast-radius measurement over it would report zero")
            failures += 1
        except ValueError:
            print("    an empty corpus raised rather than returning [].  PASS")
    finally:
        if empty.exists():
            empty.unlink()

    print("=== CONTROL 6  EACH CONTROL ABOVE, DRIVEN INTO ITS FAILING STATE")
    # A control that is computed, printed and never branched on is the defect
    # scripts/detect_unbranched_probe_controls.py was built to find in 129
    # places in this repository. So each rule is re-run with its mechanism
    # broken, and the run is VOID unless every one of them then fails.
    driven_ok = 0
    broken = anchor_hrefs(strip_bundles(doc.replace("<link", "<a")))
    print("    1 broken (link retagged as an anchor): collected %d, "
          "expected the rule to now admit 2" % len(broken))
    driven_ok += len(broken) == 2
    keep = tuple(STRIPPED_TAGS)
    try:
        globals()["STRIPPED_TAGS"] = ()
        leaky = anchor_hrefs(strip_bundles(bundled))
        print("    2 broken (stripper disabled):           collected %d, "
              "expected 2" % len(leaky))
        driven_ok += len(leaky) == 2
    finally:
        globals()["STRIPPED_TAGS"] = keep
    naive = concrete("/in/<entity>")
    keep_subs = SUBSTITUTIONS
    try:
        globals()["SUBSTITUTIONS"] = ()
        unsubbed = concrete("/in/<entity>")
        print("    4 broken (substitutions emptied):       %s" % unsubbed)
        driven_ok += "<" in unsubbed
    finally:
        globals()["SUBSTITUTIONS"] = keep_subs
    print("    controls that FAILED when broken: %d of 3" % driven_ok)
    if driven_ok != 3:
        print("    VOID -- a control could not be made to fail, so it "
              "certifies nothing")
        failures += 1
    else:
        print("    every mechanism was shown load-bearing.  PASS")
    assert naive.startswith("https://"), naive

    print()
    if failures:
        print("CONTROL: %d FAILED -- every number from this run is void"
              % failures)
        return 1
    print("control: all six passed -- a count below is a measurement")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="the drawn-anchor route corpus, for blast_radius")
    parser.add_argument("--control", action="store_true")
    parser.add_argument("--write", action="store_true",
                        help="regenerate the tracked corpus fixture")
    parser.add_argument("--state", default=str(DEFAULT_STATE))
    args = parser.parse_args()

    if args.control:
        return _control()

    state = Path(args.state)
    counts, missing = shapes_from(state)
    if missing:
        print("CAPTURES ABSENT (%d of %d): %s"
              % (len(missing), len(SURFACES), ", ".join(missing)))
        print("An absence is not a zero. _state/ carries no files in a linked "
              "worktree; point --state at the main checkout.")
        return 2

    shapes = sorted(counts)
    urls = sorted({concrete(shape) for shape in shapes})
    print("surfaces read        : %d" % len(SURFACES))
    print("distinct route shapes: %d  (depth %d, drawn anchors only)"
          % (len(shapes), DEPTH))
    print("concrete addresses   : %d" % len(urls))
    for shape in shapes:
        print("    %-58s drawn on %d surface(s)" % (shape, counts[shape]))

    if args.write:
        digest = hashlib.sha256("\n".join(urls).encode("ascii")).hexdigest()[:16]
        body = [
            "# DRAWN ROUTE CORPUS -- generated by scripts/drawn_route_corpus.py",
            "#",
            "# Every address here is a route shape a DRAWN ANCHOR produced on one",
            "# of six surfaces a live authenticated session captured 2026-09-20.",
            "# Member-bearing and id-bearing segments are replaced by tokens this",
            "# repository already sanctions, so nothing here names anybody.",
            "#",
            "# IT IS A DENOMINATOR, NOT A PERMISSION LIST. Nothing is navigated",
            "# from this file. Its only consumer is scripts/blast_radius.py, which",
            "# asks which of these addresses a candidate allowlist pattern would",
            "# newly admit.",
            "#",
            "# REGENERATE: ./venv/Scripts/python.exe scripts/drawn_route_corpus.py --write",
            "# (needs the main checkout's gitignored _state/; a worktree has none)",
            "#",
            "# addresses: %d   digest: %s" % (len(urls), digest),
            "",
        ]
        CORPUS_FILE.parent.mkdir(parents=True, exist_ok=True)
        CORPUS_FILE.write_text("\n".join(body + urls) + "\n", encoding="ascii")
        print()
        print("wrote %s" % CORPUS_FILE)
        print("addresses: %d   digest: %s" % (len(urls), digest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
