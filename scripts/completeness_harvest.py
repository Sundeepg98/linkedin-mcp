"""THE COMPLETENESS PROBE -- what LinkedIn drew that the census never wrote down.

THE QUESTION. ``scripts/census_completion.py`` says, plainly, that it cannot
find a capability nobody enumerated: every figure it prints is a fraction of
rows somebody wrote. On 2026-09-03 twenty-three unenumerated gaps were found by
ACCIDENT -- people search had no address at all. Completeness had never been
measured. This measures it, from the only side that does not start from our own
wording: what LinkedIn itself rendered on pages this repository already paid to
capture.

    what LinkedIn drew          every <a href>, every <form action>, every
                                interactive control and its accessible name,
                                on every capture on disk, bundles stripped
    reduced to a SHAPE          ids, slugs, query values and tracking values
                                gone; only the route survives
    diffed against the census   every address-shaped token in every census
                                file, reduced by the same reducer
    what is left                CANDIDATE gaps -- evidence, never rows

TAKE THE NEEDLE FROM THE SYSTEM. Nothing here is brainstormed. A candidate is a
route LinkedIn drew on a real page and the census does not carry. The one list
this file authors is a SAFETY list (families whose next segment is content, not
route), and it can only ever make the output say LESS.

## THE CLASSES, AND WHERE THE LINE IS DRAWN

    ROW      a census capability row carries the pattern exactly
    PROSE    only census prose, or a census table's note, carries it
    FAMILY   no exact match, but a census address is a segment-prefix of the
             pattern, or the pattern of one -- the census knows the family,
             not this route
    NEW      no census address shares even the first segment

CANDIDATES are PROSE + FAMILY + NEW. They are printed by class so a reader can
draw the line somewhere else; drawing it silently is how a count becomes a
quotation.

A census placeholder segment -- ``<id>``, ``{id}``, ``<slug>``, ``NUMERIC-ID``,
anything carrying ``placeholder`` -- is driven through the same reducer, so it
becomes ``<entity>`` or ``<opaque>`` exactly as a real id does. A placeholder
then matches a harvested placeholder and NOTHING ELSE: a census cell that writes
``<name>`` knows a family and enumerated none of its members, so it never
credits a literal route (``seg_match`` says why the first version did). A census
literal never matches a harvested id either.

## TWO DISCIPLINES IMPORTED, NOT RE-WRITTEN

**A NEEDLE IN THE SOURCE IS NOT A NEEDLE ON THE PAGE.** Bundles are removed with
``drawn_route_corpus.strip_bundles`` and anchors are taken with
``drawn_route_corpus.anchor_hrefs``: the same rule that corpus is built on.

**NO NAME LEAVES THE REDUCER.** Addresses are reduced by
``_probe_premium_surfaces_shape.shape_path``, whose first version leaked a slug
and whose rule is therefore to replace the segment after a member-bearing
prefix UNCONDITIONALLY. It is imported. This file adds five content-bearing
prefixes on top and never removes one.

## WHAT LEAVES THIS PROCESS

Route shapes; query parameter NAMES (never values); integers; capture LABELS
derived from file names and checked against the same rules; and control
TEMPLATES in which a word survives only if the census slice files themselves
use it AND it is the label's first word or written in lowercase; every other
word is ``<X>`` (``census_vocabulary`` records why a rule about capitals was
not enough). Everything that
leaves is vetoed against the exact-value identity wordlist when the key is on
disk (it reaches across a worktree the way ``tests/repo_paths.py`` does), and
against the committed-identity SHAPE rules always. **A vetoed pattern is not
printed; it is COUNTED, and the count is printed.** No raw capture path, no
href, no page text, no accessible name leaves verbatim.

## THE BLIND SPOTS, SAID BEFORE THE OUTPUT

* The segment directly after a member-bearing prefix is ``<entity>`` on BOTH
  sides, so ``/groups/discover`` and a real group page are one shape. A new
  route in exactly that position is invisible here.
* Only DRAWN addresses count. A control that navigates by script leaves no
  address; it appears as a control template or not at all.
* A zero is a fact about the captures. A surface nobody captured contributes
  nothing, which is what the discovery curve is for.
* Control matching is a CO-OCCURRENCE test over census rows (every content word
  of the template appears in one row), not a semantic one. Synonyms miss;
  coincidences hit. Its candidates are a lower-confidence axis and are reported
  apart from addresses.

## USAGE

    ./venv/Scripts/python.exe scripts/completeness_harvest.py               # report
    ./venv/Scripts/python.exe scripts/completeness_harvest.py --write       # + TSV
    ./venv/Scripts/python.exe scripts/completeness_harvest.py --control     # controls
    ./venv/Scripts/python.exe scripts/completeness_harvest.py --check       # fixed point
    ... --captured-before 2026-09-23T00:00:00                              # the corpus

THE ADJUDICATED CORPUS. The committed table records ONE corpus: the 71
captures taken before 2026-09-23T00:00:00 UTC, whose every app-scope candidate
lane Y2 gave a verdict (``VERDICTS``). Captures keep arriving, so regenerate
and check the committed table WITH that cutoff; a run without it is a
re-harvest, and its new candidates are read before anything is written.
``--check`` exits 1 unless the committed table is exactly what ``--write``
would write over the named corpus AND the verdict layer holds
(``verdict_problems``, which needs no capture and is what the test suite runs).

``--state-root`` names the checkout that holds the gitignored captures; by
default it is the MAIN checkout, found with ``git rev-parse --git-common-dir``,
because a linked worktree carries no ``_state/``. **NO DIRECTORY WHOSE NAME
STARTS WITH ``chrome-profile`` IS EVER ENTERED**: captures are found by explicit,
shallow globs, never by walking a tree.

Opens no browser. Navigates nothing. Loads no page. Shown failing:
``tests/test_completeness_harvest.py`` and ``--control``.
"""

from __future__ import annotations

import argparse
import collections
import dataclasses
import hashlib
import html
import html.parser
import importlib.util
import itertools
import random
import re
import subprocess
import sys
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import count_census_states as ccs  # noqa: E402
import drawn_route_corpus as drc  # noqa: E402

CENSUS = ROOT / "_audit" / "_census"
OUT_TSV = CENSUS / "completeness-candidates.tsv"
ANNOTATIONS = CENSUS / "completeness-annotations.tsv"

#: FILES THIS INSTRUMENT WRITES OR READS AS ITS OWN JUDGEMENT. They sit in the
#: census directory and are NEVER read as census: a second run would otherwise
#: find every candidate of the first run "recorded" in the candidates table and
#: report zero -- a completeness probe measuring its own output.
OWN_FILES = frozenset({OUT_TSV.name, ANNOTATIONS.name})

#: THIS INSTRUMENT'S OWN REPORTS, by a fragment of their file names. They name
#: every candidate they adjudicate, so reading them as "somebody else knows this
#: address" would make the ``known_elsewhere`` column measure the instrument's
#: own paperwork -- the same circularity ``OWN_FILES`` closes for the census.
OWN_DOCS = ("completeness-probe", "lane-y2-admission")

#: THE VERDICT LAYER, lane Y2 (2026-09-24). Every APP-scope candidate gets ONE
#: of these, written in the annotations file's ``verdict`` column:
#:
#:     ADMIT     a user capability no census row carried -- a new GAP row now
#:               carries it, named in ``verdict_rows``
#:     RECORDED  a census row already carried the capability in words; that row
#:               gained the address or control as evidence, named likewise
#:     OUT       not a user capability (chrome, a promo, a label, a pure
#:               navigation), with its one-line reason in ``verdict_basis``
#:
#: An ADMIT or RECORDED route leaves the candidate set BECAUSE a census row now
#: carries it, so a table line still holding one is a verdict the census does
#: not bear out -- :func:`verdict_problems` says so, by name.
VERDICTS = ("ADMIT", "RECORDED", "OUT")

#: The four capability slices, plus the inward inventory of tools.
SLICE_FILES = dict(ccs.SLICES)
SLICE_FILES["I"] = "mcp-inventory.md"

#: Depth a route is kept to. ``drawn_route_corpus.DEPTH`` argues for six.
DEPTH = drc.DEPTH

#: SAFETY LIST, AND THE ONE LIST THIS FILE AUTHORS. Families whose next segment
#: is CONTENT -- a product name, an article title, a hashtag -- rather than a
#: route word. Adding a prefix here can only make the output say less.
CONTENT_BEARING = frozenset({"products", "pulse", "posts", "hashtag", "topics"})

#: Placeholder spellings the census uses for a variable segment.
_CENSUS_PLACEHOLDER = re.compile(
    r"[<>{}*]|^NUMERIC-ID$|placeholder|someone|^x+$|^n$|^id$|^\.\.\.$", re.I)

#: Tokens the reducer emits for a variable segment.
REDUCED = ("<entity>", "<opaque>")

#: A segment that may stand literally in a published pattern. Anything else is
#: reduced to <seg> and counted.
_LITERAL_SEGMENT = re.compile(r"^[A-Za-z][A-Za-z0-9_.\-]{0,40}$")

#: Query parameter NAMES that may be printed.
_QUERY_KEY = re.compile(r"^[A-Za-z_][A-Za-z0-9_.\-]{0,40}$")

#: Roles that make an element an interactive control.
CONTROL_ROLES = frozenset({
    "button", "menuitem", "menuitemradio", "menuitemcheckbox", "tab", "option",
    "switch", "checkbox", "radio", "combobox", "searchbox", "textbox", "link",
    "slider", "spinbutton"})
CONTROL_TAGS = frozenset({"button", "select", "textarea"})
_VOID = frozenset({"area", "base", "br", "col", "embed", "hr", "img", "input",
                   "link", "meta", "source", "track", "wbr"})

#: Words that carry no capability. A template made only of these is
#: UNCLASSIFIABLE, which is counted, never called a candidate.
STOPWORDS = frozenset("""
a an the to for of on in with and or your my this that these those is are be
by at from as it its you me we our us up out off all more less new see show
view open close click here there now not no yes any some into about per via
what which who whom whose how when where why can will may just
""".split())

#: Path segments that mark an address as an EDITOR or a CREATION flow: the page
#: exists to change something. Evidence for W; the absence of one is not R.
WRITE_SEGMENTS = frozenset({"edit", "new", "create", "compose", "apply",
                            "delete", "remove", "withdraw", "report", "start",
                            "setup", "post"})

#: Typographic punctuation folded to ASCII before a label is templated. Code
#: points, not literals: this file is strict ASCII.
_PUNCT_FOLD = {
    chr(0x2018): "'", chr(0x2019): "'", chr(0x201C): '"', chr(0x201D): '"',
    chr(0x2026): "...", chr(0x00B7): "-", chr(0x2013): "-", chr(0x2014): "-",
    chr(0x00A0): " ", chr(0x200B): "", chr(0x2022): "-",
}


# ---------------------------------------------------------------------------
# the shipped reducer, imported
# ---------------------------------------------------------------------------

def _shipped_reducer():
    """``shape_path`` and nothing re-written."""
    spec = importlib.util.spec_from_file_location(
        "_premium_surfaces_shape",
        ROOT / "scripts" / "_probe_premium_surfaces_shape.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_REDUCER = None


def reducer():
    global _REDUCER
    if _REDUCER is None:
        _REDUCER = _shipped_reducer()
    return _REDUCER


# ---------------------------------------------------------------------------
# identity vetoes
# ---------------------------------------------------------------------------

class Veto:
    """The exact-value wordlist (when present) and the committed SHAPE rules.

    ``armed`` says whether the exact-value half could run. It is printed on
    every report: a veto that silently did not run is indistinguishable from
    one that found nothing.
    """

    def __init__(self, load_wordlist: bool = True) -> None:
        self.values: list[str] = []
        self.armed = False
        self.why = "not attempted"
        self.hits = collections.Counter()
        if load_wordlist:
            self._load()
        try:
            from tests.test_no_committed_identity import hits_in  # noqa: WPS433
            self._hits_in = hits_in
        except Exception as exc:  # noqa: BLE001
            self._hits_in = None
            self.why += "; shape rules unavailable: %s" % type(exc).__name__

    def _load(self) -> None:
        try:
            import sweep_tracked_for_identity as sweep  # noqa: WPS433
            words = sweep.load_wordlist()
        except SystemExit:
            self.why = "the identity key is not on disk (gitignored)"
            return
        except Exception as exc:  # noqa: BLE001
            self.why = "the wordlist could not load: %s" % type(exc).__name__
            return
        flat = set()
        for spellings in words.values():
            flat |= {s.casefold() for s in spellings}
        self.values = sorted(flat)
        self.armed = bool(self.values)
        self.why = "armed" if self.armed else "the key held no values"

    def clean(self, text: str, what: str) -> bool:
        """True when ``text`` may be printed. A refusal is counted by kind."""
        low = text.casefold()
        if any(v in low for v in self.values):
            self.hits["exact-value:" + what] += 1
            return False
        if self._hits_in is not None and self._hits_in(text):
            self.hits["shape:" + what] += 1
            return False
        return True


# ---------------------------------------------------------------------------
# captures
# ---------------------------------------------------------------------------

@dataclasses.dataclass(frozen=True)
class Capture:
    """One capture. ``label`` is what may be printed; ``path`` never is."""
    path: Path
    label: str
    tier: str
    when: str
    digest: str


def main_checkout(start: Path) -> Path:
    """The checkout that holds the gitignored captures. See tests/repo_paths.py."""
    try:
        from tests.repo_paths import main_checkout as shipped  # noqa: WPS433
        return shipped(start)
    except Exception:  # noqa: BLE001
        return start


def _declares_synthetic(head: str) -> bool:
    """A fixture whose own header says LinkedIn did not serve it."""
    up = head.upper()
    return any(word in up for word in (
        "NOT A CAPTURE", "IS NOT A CAPTURE", "DERIVED.", "INVENTED",
        "LINKEDIN DID NOT SERVE"))


def _mtime(path: Path) -> str:
    stamp = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return stamp.strftime("%Y-%m-%dT%H:%M:%S")


def _git_added(repo: Path, rel: str) -> str | None:
    """When a tracked file was first committed -- a fixture's only date.

    None when git cannot answer (no git on PATH, a shallow clone that lacks the
    adding commit), NEVER an empty string: a blank date sorts before every real
    one and would put the fixture at the head of the discovery curve as if it
    were the oldest capture -- an outage filed as a reading. The caller falls
    back to the file's own mtime and the curve says which it used.
    """
    try:
        proc = subprocess.run(
            ["git", "log", "--diff-filter=A", "--format=%at", "--", rel],
            cwd=str(repo), capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    stamps = [s for s in proc.stdout.split() if s.isdigit()]
    if not stamps:
        return None
    stamp = datetime.fromtimestamp(int(stamps[-1]), tz=timezone.utc)
    return stamp.strftime("%Y-%m-%dT%H:%M:%S")


def _safe_label(text: str) -> str:
    """A capture label is printed, so it obeys the segment rule."""
    parts = [p for p in re.split(r"[/\\]", text) if p]
    out = []
    for part in parts:
        part = re.sub(r"\.html?$", "", part)
        out.append(part if re.fullmatch(r"[a-z0-9][a-z0-9_\-]{0,48}", part)
                   else "<capture>")
    return "/".join(out)


def _shallow_html(directory: Path) -> list[Path]:
    """``*.html`` directly inside ``directory``, and one level below it.

    Explicit and shallow on purpose. A ``chrome-profile*`` directory is never
    listed, let alone entered.
    """
    found: list[Path] = []
    if not directory.is_dir():
        return found
    found.extend(sorted(p for p in directory.glob("*.html") if p.is_file()))
    for sub in sorted(directory.iterdir()):
        if not sub.is_dir() or sub.name.lower().startswith("chrome-profile"):
            continue
        if sub.name.startswith((".", "__")):
            continue
        found.extend(sorted(p for p in sub.glob("*.html") if p.is_file()))
    return found


def discover(state_root: Path, *, worktrees: bool = True,
             fixtures: bool = True) -> tuple[list[Capture], dict]:
    """Every capture on disk, byte-identical copies folded into one.

    Returns the captures in CAPTURE-TIME order and a dict of what was set aside
    and why, so an exclusion is a printed number rather than a silence.
    """
    candidates: list[tuple[Path, str, str, str]] = []
    for path in _shallow_html(state_root / "_state"):
        rel = path.relative_to(state_root / "_state")
        candidates.append((path, "state", _safe_label(str(rel)), _mtime(path)))
    audit = state_root / "_audit"
    if audit.is_dir():
        for path in sorted(list(audit.glob("_probe-*.html"))
                           + list(audit.glob("*_raw.html"))):
            candidates.append((path, "audit-probe",
                               _safe_label(path.name.lstrip("_")), _mtime(path)))
    if worktrees:
        wt_root = state_root / ".claude" / "worktrees"
        if wt_root.is_dir():
            for wt in sorted(wt_root.iterdir()):
                if not wt.is_dir():
                    continue
                for path in _shallow_html(wt / "_state"):
                    rel = path.relative_to(wt / "_state")
                    candidates.append((path, "worktree-state",
                                       _safe_label(str(rel)), _mtime(path)))
                wt_audit = wt / "_audit"
                if wt_audit.is_dir():
                    for path in sorted(wt_audit.glob("_probe-*.html")):
                        candidates.append((path, "worktree-audit-probe",
                                           _safe_label(path.name.lstrip("_")),
                                           _mtime(path)))
    set_aside: dict[str, list[str]] = collections.defaultdict(list)
    if fixtures:
        fixture_dir = ROOT / "tests" / "fixtures"
        for path in sorted(fixture_dir.glob("*.html")):
            head = path.read_text(encoding="utf-8", errors="replace")[:3000]
            label = _safe_label("fixture/" + path.name)
            if "synthetic" in path.name.lower() or _declares_synthetic(head):
                set_aside["fixture declares itself not a capture"].append(label)
                continue
            rel = path.relative_to(ROOT).as_posix()
            candidates.append((path, "fixture", label,
                               _git_added(ROOT, rel) or _mtime(path)))

    seen: dict[str, Capture] = {}
    for path, tier, label, when in candidates:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest in seen:
            prior = seen[digest]
            keep, drop = (prior, (path, tier, label, when))
            if when < prior.when:
                keep = Capture(path, label, tier, when, digest)
                drop = (prior.path, prior.tier, prior.label, prior.when)
            seen[digest] = keep
            set_aside["byte-identical to another capture"].append(drop[2])
            continue
        seen[digest] = Capture(path, label, tier, when, digest)
    ordered = sorted(seen.values(), key=lambda c: (c.when, c.label))
    return ordered, dict(set_aside)


def surface_of(capture: Capture) -> str:
    """The SURFACE a capture is of, so a re-capture folds into its first one.

    Derived from the label by dropping the variant words capture scripts add
    (hydration, timing, repeat index, captions). Two captures of one page are
    one surface; the curve counts surfaces.
    """
    label = capture.label.split("/")[-1] if "/" in capture.label else capture.label
    group = capture.label.split("/")[0] if "/" in capture.label else ""
    base = re.sub(r"^(cap|probe)-", "", label)
    # A "control-" PREFIX is a re-capture of the named surface. A "-control"
    # SUFFIX is not: cap-roleplay-control is the PREMIUM HUB, captured as the
    # control arm of the role-play experiment, and stripping the suffix merged
    # the role-play page into it.
    base = re.sub(r"^control-", "", base)
    base = re.sub(r"-(hyd|hydrated|captions|t\d+|target|capture-\d+)$", "", base)
    base = re.sub(r"_hydrated$", "", base)
    base = base.replace("in_progress", "inprogress").replace("in-progress", "inprogress")
    if group in ("company-root-wording", "group-feed-permalinks"):
        return group
    if group == "how-you-match":
        return "how-you-match"
    if group == "fixture":
        base = re.sub(r"_(hydrated|shell|salary|following)$", "", base)
        base = re.sub(r"_(hydrated)$", "", base)
        return "fixture:" + base
    return base


# ---------------------------------------------------------------------------
# harvest
# ---------------------------------------------------------------------------

@dataclasses.dataclass
class Harvest:
    anchors: list[tuple[str, str, str]]     # (href, drawn text, landmark regions)
    forms: list[tuple[str, str, str]]       # (action, method, aria-label)
    controls: list[tuple[str, str, str]]    # (tag, role, accessible name)
    external: int = 0                       # anchors to a non-LinkedIn host


#: LinkedIn's own LANDMARKS, by tag or by role. Where an address is drawn is
#: evidence of what it is: a route drawn only inside the footer is site chrome,
#: not a member capability, and that is LinkedIn's classification, not ours.
_LANDMARK_TAGS = {"footer": "footer", "header": "header", "nav": "nav",
                  "aside": "aside", "main": "main", "dialog": "dialog"}
_LANDMARK_ROLES = {"contentinfo": "footer", "banner": "header",
                   "navigation": "nav", "complementary": "aside", "main": "main",
                   "dialog": "dialog", "alertdialog": "dialog", "menu": "menu"}
#: Elements that scope a <footer>/<header> to themselves (HTML-AAM).
_SECTIONING = frozenset({"article", "aside", "main", "nav", "section"})


class _Collector(html.parser.HTMLParser):
    """Anchors with their text and landmark, forms, and controls with their names."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.open: list[list] = []   # [kind, tag, role, label, parts, depth, href, region]
        self.landmarks: list[tuple[int, str]] = []
        self.sections: list[tuple[int, str]] = []
        self.anchors: list[tuple[str, str, str]] = []
        self.forms: list[tuple[str, str, str]] = []
        self.controls: list[tuple[str, str, str]] = []

    def _region(self) -> str:
        """The footer and the header win over anything nested inside them.

        LinkedIn draws its footer links inside a ``<nav>`` inside the footer;
        the innermost landmark would call them navigation. What matters for a
        completeness question is that they are SITE CHROME, so the outermost
        of those two is reported.
        """
        regions = [r for _d, r in self.landmarks]
        for outer in ("footer", "header"):
            if outer in regions:
                return outer
        return regions[-1] if regions else "none"

    def handle_starttag(self, tag, attrs):
        attr = {k: (v or "") for k, v in attrs}
        role = attr.get("role", "").strip().lower()
        label = (attr.get("aria-label") or "").strip()
        region = _LANDMARK_ROLES.get(role) or _LANDMARK_TAGS.get(tag)
        # HTML-AAM: a <footer> or <header> is the SITE's contentinfo or banner
        # only when no sectioning element encloses it. LinkedIn wraps a card's
        # "Show all" link in the card's own <footer>, and calling that chrome
        # filed a My Network list under the site footer on the first run.
        if not role and tag in ("footer", "header") and any(
                t in _SECTIONING for _d, t in self.sections):
            region = "section-" + tag
        if tag in _SECTIONING and tag not in _VOID:
            self.sections.append((self.depth, tag))
        if region and tag not in _VOID:
            self.landmarks.append((self.depth, region))
        if tag == "form":
            self.forms.append((attr.get("action", ""), attr.get("method", ""), label))
        kind = None
        if tag == "a" and attr.get("href"):
            kind = "a"
        elif tag in CONTROL_TAGS or role in CONTROL_ROLES:
            kind = "c"
        elif tag == "input" and attr.get("type", "text").lower() != "hidden":
            kind = "c"
        if kind == "c" and not label:
            label = (attr.get("title") or attr.get("placeholder") or "").strip()
        if kind and tag in _VOID:
            if kind == "c":
                self.controls.append((tag, role, label))
        elif kind:
            self.open.append([kind, tag, role, label, [], self.depth,
                              attr.get("href", ""), self._region()])
        if tag not in _VOID:
            self.depth += 1

    def _emit(self, item) -> None:
        kind, otag, role, label, parts, _d, href, region = item
        text = re.sub(r"\s+", " ", " ".join(parts)).strip()
        if kind == "a":
            self.anchors.append((href, label or text, region))
        else:
            self.controls.append((otag, role, label or text))

    def handle_endtag(self, tag):
        if tag in _VOID:
            return
        self.depth = max(0, self.depth - 1)
        while self.open and self.open[-1][5] >= self.depth:
            item = self.open.pop()
            self._emit(item)
            if self.open:
                self.open[-1][4].extend(item[4])
        while self.landmarks and self.landmarks[-1][0] >= self.depth:
            self.landmarks.pop()
        while self.sections and self.sections[-1][0] >= self.depth:
            self.sections.pop()

    def handle_data(self, data):
        if self.open:
            self.open[-1][4].append(data)

    def close_all(self):
        while self.open:
            self._emit(self.open.pop())


def harvest_document(markup: str) -> Harvest:
    """What one page DREW. Bundles are stripped with the shipped stripper first.

    The anchor SET is the shipped ``anchor_hrefs`` rule; the collector only
    pairs each of those hrefs with the text it was drawn with.
    """
    stripped = drc.strip_bundles(markup)
    # The parser hands attribute values back UNESCAPED; the shipped rule returns
    # them as written. Both sides are compared unescaped.
    drawn = {html.unescape(h) for h in drc.anchor_hrefs(stripped)}
    external = 0
    for href in re.findall(r'<a\b[^>]*\bhref="([^"]{1,400})"', stripped, flags=re.I):
        if href.startswith("http") and "linkedin.com" not in href:
            external += 1
    collector = _Collector()
    try:
        collector.feed(stripped)
        collector.close()
    except Exception:  # noqa: BLE001 -- a malformed tail keeps what parsed
        pass
    collector.close_all()
    texts: dict[str, str] = {}
    regions: dict[str, set[str]] = collections.defaultdict(set)
    for href, text, region in collector.anchors:
        if href in drawn:
            texts.setdefault(href, text)
            regions[href].add(region)
    anchors = [(href, texts.get(href, ""), "+".join(sorted(regions.get(href) or {"none"})))
               for href in sorted(drawn)]
    return Harvest(anchors, collector.forms, collector.controls, external)


# ---------------------------------------------------------------------------
# addresses -> patterns
# ---------------------------------------------------------------------------

@dataclasses.dataclass(frozen=True)
class Pattern:
    host: str      # "" for www.linkedin.com
    segments: tuple[str, ...]

    def shape(self) -> str:
        path = "/" + "/".join(self.segments) if self.segments else "/"
        return (self.host + path) if self.host else path


def split_address(raw: str) -> tuple[str, str, list[str]]:
    """(host, path, query keys) of an href or a census token. Values dropped."""
    href = html.unescape(raw).strip()
    host = "www.linkedin.com"
    m = re.match(r"^(?:https?:)?//([^/?#]+)", href, flags=re.I)
    if m:
        host = m.group(1).lower()
        href = href[m.end():]
    path, _, rest = href.partition("?")
    path = path.split("#")[0]
    if m and not path:
        path = "/"   # an absolute address with no path is the site root
    query = rest.split("#")[0]
    keys = []
    for part in query.split("&"):
        key = part.split("=")[0]
        key = urllib.parse.unquote(key)
        if key and _QUERY_KEY.match(key):
            keys.append(key)
    return host, path, sorted(set(keys))


def reduce_path(host: str, path: str, veto: Veto | None = None,
                census: bool = False) -> Pattern | None:
    """A path reduced to a SHAPE by the shipped reducer, then hardened.

    ``census=True`` first turns a census placeholder segment into a digit run,
    so the reducer maps it to ``<opaque>`` (or ``<entity>`` after a
    member-bearing prefix) exactly as it maps a real id.
    """
    segs = [s for s in path.split("/") if s]
    if census:
        segs = ["1234567890" if _CENSUS_PLACEHOLDER.search(s) else s for s in segs]
    shaped = reducer().shape_path("/" + "/".join(segs), depth=DEPTH)
    out: list[str] = []
    parts = [s for s in shaped.split("/") if s]
    for i, seg in enumerate(parts):
        if seg in REDUCED:
            out.append(seg)
        elif i > 0 and parts[i - 1].lower() in CONTENT_BEARING:
            out.append("<entity>")
        elif _LITERAL_SEGMENT.match(seg):
            out.append(seg)
        else:
            out.append("<seg>")
    host = host.lower()
    if host in ("www.linkedin.com", "linkedin.com"):
        host = ""
    elif not host.endswith("linkedin.com"):
        return None
    pattern = Pattern(host, tuple(out))
    if veto is not None and not veto.clean(pattern.shape(), "pattern"):
        return None
    return pattern


def is_placeholder(seg: str) -> bool:
    return seg in REDUCED or seg == "<seg>"


def seg_match(census_seg: str, harvested_seg: str) -> bool:
    """A placeholder matches a placeholder; a literal matches itself.

    STRICT ON PURPOSE. A census cell that writes ``/mypreferences/d/categories/<name>``
    knows the FAMILY and enumerated none of its members, so it must not credit
    ``/mypreferences/d/categories/account`` as recorded. The first version let
    a census placeholder match any literal, and a single generic
    ``/in/<member>/<x>`` token then covered every profile sub-route LinkedIn
    draws -- the probe was measuring the looseness of our own placeholders.
    """
    if is_placeholder(census_seg):
        return is_placeholder(harvested_seg)
    return census_seg.lower() == harvested_seg.lower()


def exact(census: Pattern, harvested: Pattern) -> bool:
    return (census.host == harvested.host
            and len(census.segments) == len(harvested.segments)
            and all(seg_match(c, h) for c, h in zip(census.segments, harvested.segments)))


def prefix_relation(census: Pattern, harvested: Pattern) -> str:
    """'child-of' / 'parent-of' when one is a segment-prefix of the other."""
    if census.host != harvested.host:
        return ""
    c, h = census.segments, harvested.segments
    if not c or not h:
        return ""
    # A family is only a family if it shares at least one LITERAL segment.
    if is_placeholder(c[0]):
        return ""
    n = min(len(c), len(h))
    if not all(seg_match(c[i], h[i]) for i in range(n)):
        return ""
    if len(c) < len(h):
        return "child-of"
    if len(c) > len(h):
        return "parent-of"
    return ""


# ---------------------------------------------------------------------------
# the census side
# ---------------------------------------------------------------------------

_URL_TOKEN = re.compile(
    r"https?://((?:[a-z0-9-]+\.)*linkedin\.com)(/[^\s`'\"()|\]\\]*)?", re.I)
_PATH_TOKEN = re.compile(
    r"(?<![A-Za-z0-9_.\-/~:])(/[A-Za-z][A-Za-z0-9_\-.%:<>{}*]*"
    r"(?:/[A-Za-z0-9_\-.%:<>{}*]*)*(?:\?[A-Za-z0-9_=&%.\-<>{}]*)?)")
_FILE_SUFFIX = re.compile(r"\.(py|md|tsv|json|html?|txt|ps1|sh|yml|yaml|toml|ini|cfg|log)$", re.I)


@dataclasses.dataclass(frozen=True)
class CensusAddress:
    pattern: Pattern
    source: str      # file name
    row: str         # "J 42" style, or "" for prose
    line: int
    level: str       # "row" or "prose"


def address_tokens(text: str) -> list[tuple[str, str]]:
    """(host, path) for every address-shaped token in a run of census text."""
    found: list[tuple[str, str]] = []
    spans: list[tuple[int, int]] = []
    for m in _URL_TOKEN.finditer(text):
        path = (m.group(2) or "/").rstrip(".,;:)*")
        found.append((m.group(1).lower(), path))
        spans.append(m.span())
    for m in _PATH_TOKEN.finditer(text):
        if any(a <= m.start() < b for a, b in spans):
            continue
        token = m.group(1).rstrip(".,;:)*")
        bare = token.split("?")[0]
        if _FILE_SUFFIX.search(bare):
            continue
        found.append(("www.linkedin.com", token))
    return found


def _row_id(slice_letter: str, cells: list[str]) -> str:
    rid = cells[0].strip("`* ").strip()
    if not rid or rid.lower() in ccs.HEADERS or set(rid) <= set("-: "):
        return ""
    return "%s %s" % (slice_letter, rid)


def census_index(census_dir: Path = CENSUS) -> list[CensusAddress]:
    """Every address the census records, with where it records it.

    A line of a slice file that parses as a capability table row (the shipped
    ``count_census_states.ROW`` and ``cells``) is ROW-level evidence keyed by
    its row id; every other line of every census file is PROSE-level. A TSV
    line with a row-id column is ROW-level under that id.
    """
    out: list[CensusAddress] = []
    missing = [n for n in ccs.SLICES.values() if not (census_dir / n).exists()]
    if missing:
        raise SystemExit(
            "census slice file(s) absent under %s: %s -- refusing to diff "
            "against a census that is not there, because every harvested "
            "pattern would come back NEW and read as a finding"
            % (census_dir, ", ".join(sorted(missing))))
    letter_of = {name: letter for letter, name in SLICE_FILES.items()}
    for path in sorted(census_dir.iterdir()):
        if not path.is_file() or path.name in OWN_FILES:
            continue
        if path.suffix not in (".md", ".tsv"):
            continue
        letter = letter_of.get(path.name, "")
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        header: list[str] = []
        for lineno, line in enumerate(lines, 1):
            row, level = "", "prose"
            if path.suffix == ".md" and letter and ccs.ROW.match(line):
                cells = ccs.cells(line)
                if len(cells) >= 3:
                    row = _row_id(letter, cells)
                    level = "row" if row else "prose"
            elif path.suffix == ".tsv" and not line.startswith(("#", ">")):
                cells = line.split("\t")
                if not header:
                    header = [c.strip().lower() for c in cells]
                    continue
                cols = dict(zip(header, cells))
                if cols.get("row_id"):
                    row, level = cols["row_id"].strip(), "row"
                elif cols.get("slice") and cols.get("row"):
                    row, level = "%s %s" % (cols["slice"].strip(), cols["row"].strip()), "row"
            for host, token in address_tokens(line):
                hostpart, pathpart, _keys = split_address(
                    token if token.startswith("http") else "//" + host + token)
                pattern = reduce_path(hostpart, pathpart, census=True)
                if pattern is None or not pattern.segments:
                    continue
                out.append(CensusAddress(pattern, path.name, row, lineno, level))
    return out


def elsewhere_index() -> dict[Pattern, set[str]]:
    """Addresses the repository names OUTSIDE the census, by kind of source.

    ``audit`` (a dated document), ``code`` (the shipped package), ``script``
    and ``test``. Used only to annotate a candidate; it never moves one out of
    the candidate set -- somebody having WRITTEN an address down somewhere is
    not the census carrying it. The drawn-route corpus is deliberately NOT a
    source: it is a harvest of six captures, not anybody's knowledge, and
    counting it would make every drawn route "known". This instrument's own
    record is excluded for the reason its TSV is.
    """
    out: dict[Pattern, set[str]] = collections.defaultdict(set)
    sources: list[tuple[str, Path]] = []
    sources += [("audit", p) for p in (ROOT / "_audit").glob("*.md")
                if not any(own in p.name for own in OWN_DOCS)]
    sources += [("code", p) for p in (ROOT / "linkedin_server").rglob("*.py")]
    sources += [("script", p) for p in (ROOT / "scripts").glob("*.py")
                if p.name != Path(__file__).name]
    sources += [("test", p) for p in (ROOT / "tests").glob("*.py")
                if "completeness_harvest" not in p.name]
    sources += [("audit", ROOT / "README.md")]
    for kind, path in sources:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for host, token in address_tokens(text):
            hostpart, pathpart, _keys = split_address(
                token if token.startswith("http") else "//" + host + token)
            pattern = reduce_path(hostpart, pathpart, census=True)
            if pattern is not None and pattern.segments:
                out[pattern].add(kind)
    return dict(out)


# ---------------------------------------------------------------------------
# classification
# ---------------------------------------------------------------------------

@dataclasses.dataclass
class Verdict:
    klass: str               # ROW | PROSE | FAMILY | NEW
    relation: str            # exact / child-of / parent-of / -
    nearest: str             # the census pattern it is nearest to
    rows: list[str]          # census row ids carrying it or its family
    slice: str               # J / P / M / N / I / ?


def classify(pattern: Pattern, census: list[CensusAddress]) -> Verdict:
    """ROW, PROSE, FAMILY or NEW -- see the module docstring."""
    exact_rows = [c for c in census if c.level == "row" and exact(c.pattern, pattern)]
    if exact_rows:
        rows = sorted({c.row for c in exact_rows})
        return Verdict("ROW", "exact", exact_rows[0].pattern.shape(), rows,
                       _slice_of(rows))
    exact_prose = [c for c in census if exact(c.pattern, pattern)]
    if exact_prose:
        return Verdict("PROSE", "exact", exact_prose[0].pattern.shape(),
                       sorted({"%s:%d" % (c.source, c.line) for c in exact_prose})[:3],
                       _slice_by_source(exact_prose))
    related = []
    for c in census:
        rel = prefix_relation(c.pattern, pattern)
        if rel:
            shared = min(len(c.pattern.segments), len(pattern.segments))
            related.append((shared, rel, c))
    if related:
        best = max(shared for shared, _r, _c in related)
        top = [(r, c) for shared, r, c in related if shared == best]
        rel = "child-of" if any(r == "child-of" for r, _c in top) else "parent-of"
        chosen = [c for r, c in top if r == rel]
        rows = sorted({c.row for c in chosen if c.row})
        return Verdict("FAMILY", rel, chosen[0].pattern.shape(), rows[:6],
                       _slice_of(rows) if rows else _slice_by_source(chosen))
    def common(c: CensusAddress) -> int:
        n = 0
        for a, b in zip(c.pattern.segments, pattern.segments):
            if is_placeholder(a) or a.lower() != b.lower():
                break
            n += 1
        return n

    same_host = [c for c in census if c.pattern.host == pattern.host]
    best = max((common(c) for c in same_host), default=0)
    if best:  # shares a literal prefix, then diverges
        nearest = [c for c in same_host if common(c) == best]
        rows = sorted({c.row for c in nearest if c.row})
        return Verdict("FAMILY", "sibling", nearest[0].pattern.shape(), rows[:6],
                       _slice_of(rows) if rows else _slice_by_source(nearest))
    return Verdict("NEW", "-", "-", [], "?")


def _slice_of(rows: list[str]) -> str:
    letters = collections.Counter(r.split(" ")[0] for r in rows if r)
    if not letters:
        return "?"
    return "/".join(sorted(letters, key=lambda k: (-letters[k], k)))


def _slice_by_source(addresses: list[CensusAddress]) -> str:
    letter_of = {name: letter for letter, name in SLICE_FILES.items()}
    letters = collections.Counter(letter_of.get(c.source, "") for c in addresses)
    letters.pop("", None)
    if not letters:
        return "?"
    return "/".join(sorted(letters, key=lambda k: (-letters[k], k)))


def rw_of(pattern: Pattern, methods: set[str]) -> tuple[str, str]:
    """('W', evidence) when the address is an editor or a creation flow."""
    if any(m.lower() == "post" for m in methods):
        return "W", "form method POST"
    hits = [s for s in pattern.segments if s.lower() in WRITE_SEGMENTS]
    if hits:
        return "W", "path segment '%s'" % hits[-1]
    return "R", "a navigable page; no write segment"


# ---------------------------------------------------------------------------
# control templates
# ---------------------------------------------------------------------------

def fold(label: str) -> str | None:
    """ASCII-fold typographic punctuation; None when non-ASCII remains."""
    text = "".join(_PUNCT_FOLD.get(ch, ch) for ch in label)
    text = re.sub(r"\s+", " ", text).strip()
    if not text or not text.isascii():
        return None
    return text


def _core(token: str) -> str:
    return token.strip(".,:;!?()[]\"'|")


#: A label longer than this is prose -- a post, a headline, a description --
#: and not a control's name. It is withheld whole rather than templated.
MAX_LABEL_WORDS = 16


def census_vocabulary(census_dir: Path = CENSUS) -> frozenset[str]:
    """Every word the census slice files use, casefolded. THE CLOSED ALPHABET.

    WHY THE CENSUS AND NOT A RULE ABOUT CAPITALS. The first version let a word
    through when it was lowercase, or when it began two or more distinct
    labels. Run over the real captures it printed the operator's own first
    name (it begins every conversation label that lists him first, and the
    identity key holds only longer spellings of it) and a third party's
    surname written in lowercase. Recurrence and case are properties of
    LinkedIn's rendering, not of whether a word is a name.

    The census slices are the most carefully identity-guarded prose in this
    repository, and they describe LinkedIn's product in LinkedIn's words --
    measured on the day this was written: none of the fixture sanitiser's
    invented names and neither of those two words occurs in them. A word the
    census never uses leaves as ``<X>``. The cost is named, not hidden: a
    control whose ONLY novelty is a word the census never uses is reported with
    that word as ``<X>``, so this axis under-reports new vocabulary.
    """
    words: set[str] = set()
    for name in SLICE_FILES.values():
        path = census_dir / name
        if path.exists():
            text = path.read_text(encoding="utf-8", errors="replace")
            words |= {w.casefold() for w in re.findall(r"[A-Za-z][A-Za-z'\-]*", text)}
    return frozenset(words)


def template_of(label: str, vocabulary: frozenset[str] | set[str]) -> str | None:
    """The name-free TEMPLATE of one accessible name, or None to withhold it.

    A word survives only if the census uses it (``vocabulary``) AND it is
    either the label's first word or written in lowercase -- a capitalised
    word mid-label is a name more often than not, whatever the census says.
    Digits become ``<n>``. The template keeps the leading literal run, one
    ``<X>`` for everything between the first and the last reduced word, and
    the trailing literal run -- so a title's middle never leaves either.
    """
    text = fold(label)
    if text is None:
        return None
    tokens = text.split(" ")
    if len(tokens) > MAX_LABEL_WORDS:
        return None
    marks: list[str] = []
    for i, tok in enumerate(tokens):
        core = _core(tok)
        if not core:
            marks.append(tok)
            continue
        known = core.casefold() in vocabulary
        if re.fullmatch(r"[\d.,:%+\-]+", core):
            marks.append("<n>")
        elif known and i == 0 and re.fullmatch(r"[A-Za-z][A-Za-z'\-]*", core):
            marks.append(tok)
        elif known and i > 0 and re.fullmatch(r"[a-z][a-z'\-]*", core):
            marks.append(tok)
        else:
            marks.append("<X>")
    reduced = [i for i, m in enumerate(marks) if m == "<X>"]
    if reduced:
        lead = marks[:reduced[0]]
        tail = marks[reduced[-1] + 1:]
        marks = lead + ["<X>"] + tail
    out = " ".join(marks).strip()
    out = re.sub(r"(<n>\s*){2,}", "<n> ", out).strip()
    if not out or not re.search(r"[A-Za-z]{2,}", out.replace("<X>", "").replace("<n>", "")):
        return None
    return out


def content_words(template: str) -> list[str]:
    words = re.findall(r"[a-z][a-z'\-]*", template.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 2 and w != "x"]


def _stem(word: str) -> str:
    for suffix in ("ings", "ing", "ers", "ies", "ed", "es", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 4:
            return word[: -len(suffix)]
    return word


def census_row_texts(census_dir: Path = CENSUS) -> list[tuple[str, str]]:
    """(row id, lowercased row text) for every capability row of every slice."""
    rows: list[tuple[str, str]] = []
    for letter, name in SLICE_FILES.items():
        path = census_dir / name
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not ccs.ROW.match(line):
                continue
            cells = ccs.cells(line)
            if len(cells) < 3:
                continue
            rid = _row_id(letter, cells)
            if rid:
                rows.append((rid, " ".join(cells[1:]).lower()))
    return rows


def rows_carrying(words: list[str], rows: list[tuple[str, str]]) -> list[str]:
    """Census row ids whose text carries EVERY word (as a word-initial stem)."""
    stems = [_stem(w) for w in words]
    return [rid for rid, text in rows
            if all(re.search(r"\b" + re.escape(s), text) for s in stems)]


def control_verdict(template: str, rows: list[tuple[str, str]]) -> tuple[str, list[str]]:
    """RECORDED (with rows) when one census row carries every content word."""
    words = content_words(template)
    if not words:
        return "UNCLASSIFIABLE", []
    hits = rows_carrying(words, rows)
    return ("RECORDED", hits[:6]) if hits else ("CANDIDATE", [])


# ---------------------------------------------------------------------------
# the run
# ---------------------------------------------------------------------------

@dataclasses.dataclass
class Seen:
    captures: set[str] = dataclasses.field(default_factory=set)
    surfaces: set[str] = dataclasses.field(default_factory=set)
    first: str = ""
    keys: set[str] = dataclasses.field(default_factory=set)
    methods: set[str] = dataclasses.field(default_factory=set)
    kinds: set[str] = dataclasses.field(default_factory=set)
    drawn_as: collections.Counter = dataclasses.field(default_factory=collections.Counter)
    regions: set[str] = dataclasses.field(default_factory=set)


def select_corpus(state_root: Path, *, worktrees: bool = True, fixtures: bool = True,
                  captured_before: str = "") -> tuple[list[Capture], dict]:
    """``discover``, then keep only captures taken BEFORE ``captured_before``.

    WHY A CUTOFF EXISTS. The committed table is the record of ONE adjudicated
    corpus. Captures keep arriving under ``_state/`` -- a live lane writes them
    every session -- so a plain ``--write`` rewrites the table over whatever is
    on disk that hour, and a candidate nobody has read lands in a tracked file.
    ``--captured-before`` names the corpus: a capture whose ``when`` (UTC, the
    same stamp the curve orders by) is on or after the cutoff is SET ASIDE, and
    the set-aside count is printed like every other exclusion -- an exclusion
    is a printed number, never a silence. An empty cutoff keeps everything.
    """
    captures, set_aside = discover(state_root, worktrees=worktrees, fixtures=fixtures)
    if not captured_before:
        return captures, set_aside
    kept = [c for c in captures if c.when < captured_before]
    later = [c.label for c in captures if c.when >= captured_before]
    if later:
        set_aside = dict(set_aside)
        set_aside["captured on or after %s (--captured-before)" % captured_before] = later
    return kept, set_aside


def run(state_root: Path, *, worktrees: bool = True, fixtures: bool = True,
        veto: Veto | None = None, census_dir: Path = CENSUS,
        captures: list[Capture] | None = None,
        set_aside: dict | None = None) -> dict:
    """Harvest every capture, diff against the census, and build the curve."""
    veto = veto or Veto()
    set_aside = dict(set_aside or {})
    if captures is None:
        captures, set_aside = discover(state_root, worktrees=worktrees, fixtures=fixtures)
    census = census_index(census_dir)
    rows = census_row_texts(census_dir)
    patterns: dict[Pattern, Seen] = {}
    control_raw: dict[str, Seen] = {}
    per_capture: list[dict] = []
    totals = collections.Counter()
    harvests = []
    for cap in captures:
        markup = cap.path.read_text(encoding="utf-8", errors="replace")
        harvests.append((cap, harvest_document(markup)))
    surfaces, folds = assign_surfaces(harvests, veto)
    for cap, got in harvests:
        totals["anchors"] += len(got.anchors)
        totals["forms"] += len(got.forms)
        totals["controls"] += len(got.controls)
        totals["external anchors (not LinkedIn, never printed)"] += got.external
        mine: set[Pattern] = set()
        mine_controls: set[str] = set()
        surface = surfaces[cap.label]
        for href, text, region in got.anchors:
            host, path, keys = split_address(href)
            if not path.startswith("/"):
                # "?x=1" or "details/x" resolves against the page it sits on,
                # whose address a capture does not carry. Counted, not guessed.
                totals["page-relative hrefs (no absolute path)"] += 1
                continue
            pattern = reduce_path(host, path, veto)
            if pattern is None:
                totals["addresses withheld or off-host"] += 1
                continue
            seen = patterns.setdefault(pattern, Seen(first=cap.label))
            seen.captures.add(cap.label)
            seen.surfaces.add(surface)
            seen.keys |= {k for k in keys if veto.clean(k, "query key")}
            seen.kinds.add("anchor")
            seen.regions |= set(region.split("+"))
            if text:
                seen.drawn_as[text] += 1
            mine.add(pattern)
        for action, method, _label in got.forms:
            if method:
                totals["forms with a method"] += 1
            if not action:
                totals["forms with no action (script-handled)"] += 1
                continue
            host, path, keys = split_address(action)
            pattern = reduce_path(host, path or "/", veto)
            if pattern is None:
                continue
            seen = patterns.setdefault(pattern, Seen(first=cap.label))
            seen.captures.add(cap.label)
            seen.surfaces.add(surface)
            seen.kinds.add("form")
            if method:
                seen.methods.add(method)
            mine.add(pattern)
        for _tag, _role, name in got.controls:
            if not name:
                totals["controls with no accessible name"] += 1
                continue
            seen = control_raw.setdefault(name, Seen(first=cap.label))
            seen.captures.add(cap.label)
            seen.surfaces.add(surface)
            mine_controls.add(name)
        per_capture.append({"capture": cap, "surface": surface, "patterns": mine,
                            "controls": mine_controls})

    verdicts = {p: classify(p, census) for p in patterns}
    candidate_set = {p for p, v in verdicts.items() if v.klass != "ROW"}

    # Templates, over the census's own closed vocabulary.
    vocabulary = census_vocabulary(census_dir)
    templates: dict[str, Seen] = {}
    raw_to_template: dict[str, str] = {}
    for name, seen in control_raw.items():
        tpl = template_of(name, vocabulary)
        if tpl is None:
            totals["control labels withheld (non-ASCII, or nothing survives)"] += 1
            continue
        if not veto.clean(tpl, "control template"):
            totals["control templates vetoed"] += 1
            continue
        raw_to_template[name] = tpl
        agg = templates.setdefault(tpl, Seen(first=seen.first))
        agg.captures |= seen.captures
        agg.surfaces |= seen.surfaces
        agg.drawn_as[name] += 1   # distinct raw labels -- COUNTED, never printed
        if seen.first < agg.first:
            agg.first = seen.first
    control_verdicts = {t: control_verdict(t, rows) for t in templates}
    control_candidates = {t for t, (v, _h) in control_verdicts.items() if v == "CANDIDATE"}
    for item in per_capture:
        item["templates"] = {raw_to_template[n] for n in item["controls"]
                             if n in raw_to_template}

    # What each address was DRAWN AS, reduced the same way; never the raw text.
    drawn_as: dict[Pattern, list[str]] = {}
    for pattern, seen in patterns.items():
        tally = collections.Counter()
        for text, n in seen.drawn_as.items():
            tpl = template_of(text, vocabulary)
            if tpl and veto.clean(tpl, "anchor text template"):
                tally[tpl] += n
        drawn_as[pattern] = [t for t, _n in tally.most_common(2)]

    curve = build_curve(per_capture, candidate_set, control_candidates)
    return {
        "captures": captures, "set_aside": set_aside, "census": census,
        "patterns": patterns, "verdicts": verdicts, "candidates": candidate_set,
        "templates": templates, "control_verdicts": control_verdicts,
        "control_candidates": control_candidates, "drawn_as": drawn_as,
        "curve": curve, "totals": totals, "veto": veto, "folds": folds,
        "surfaces": surfaces, "row_texts": rows,
    }


#: Two captures whose drawn address sets overlap at least this much are ONE
#: surface, whatever their file names say. Measured need: the same page is
#: saved under two naming schemes by different waves (a "control" capture of
#: one surface named after another), and a re-capture that stays a separate
#: surface adds zero by construction and flattens the curve for free.
SAME_SURFACE_JACCARD = 0.95


def assign_surfaces(harvests: list[tuple[Capture, Harvest]],
                    veto: Veto) -> tuple[dict[str, str], list[tuple[str, str, float]]]:
    """capture label -> surface. Name rules first, then a content fold."""
    reduced: list[tuple[Capture, set[Pattern]]] = []
    for cap, got in harvests:
        pats = set()
        for href, _text, _region in got.anchors:
            host, path, _keys = split_address(href)
            p = reduce_path(host, path or "/")
            if p is not None:
                pats.add(p)
        reduced.append((cap, pats))
    surfaces: dict[str, str] = {}
    union: dict[str, set[Pattern]] = {}
    folds: list[tuple[str, str, float]] = []
    # A NAME ONCE FOLDED STAYS FOLDED: a later re-capture saved under the same
    # name is the same surface as its namesake, whatever its drift.
    alias: dict[str, str] = {}
    for cap, pats in reduced:
        name = alias.get(surface_of(cap), surface_of(cap))
        if name in union:
            surfaces[cap.label] = name
            union[name] |= pats
            continue
        best, score = "", 0.0
        for other, opats in union.items():
            if not pats or not opats:
                continue
            j = len(pats & opats) / len(pats | opats)
            if j > score:
                best, score = other, j
        if best and score >= SAME_SURFACE_JACCARD:
            surfaces[cap.label] = best
            union[best] |= pats
            alias[name] = best
            folds.append((cap.label, best, round(score, 3)))
            continue
        surfaces[cap.label] = name
        union[name] = set(pats)
    return surfaces, folds


def build_curve(per_capture: list[dict], candidates: set[Pattern],
                control_candidates: set[str] | None = None) -> dict:
    """New patterns per capture and per SURFACE, in capture-time order."""
    control_candidates = control_candidates or set()
    seen: set[Pattern] = set()
    by_capture = []
    for item in per_capture:
        new = item["patterns"] - seen
        seen |= item["patterns"]
        by_capture.append((item["capture"].label, item["surface"], item["capture"].when,
                           len(new), len(new & candidates), len(seen)))
    surf_order: list[str] = []
    surf_patterns: dict[str, set[Pattern]] = collections.defaultdict(set)
    surf_templates: dict[str, set[str]] = collections.defaultdict(set)
    surf_when: dict[str, str] = {}
    for item in per_capture:
        s = item["surface"]
        if s not in surf_when:
            surf_order.append(s)
            surf_when[s] = item["capture"].when
        surf_patterns[s] |= item["patterns"]
        surf_templates[s] |= item.get("templates", set())
    seen = set()
    seen_t: set[str] = set()
    by_surface = []
    for s in surf_order:
        new = surf_patterns[s] - seen
        seen |= surf_patterns[s]
        new_t = (surf_templates[s] & control_candidates) - seen_t
        seen_t |= surf_templates[s] & control_candidates
        by_surface.append((s, surf_when[s], len(surf_patterns[s]), len(new),
                           len(new & candidates), len(seen & candidates),
                           len(new_t), len(seen_t)))
    last5 = [row[4] for row in by_surface[-5:]]
    flattened = len(by_surface) >= 5 and sum(last5) == 0
    # Permutation-averaged accumulation: mean candidates known after k surfaces.
    rng = random.Random(20260923)
    k_max = len(surf_order)
    sums = [0.0] * (k_max + 1)
    trials = 400
    cand_sets = [surf_patterns[s] & candidates for s in surf_order]
    for _ in range(trials):
        order = list(range(k_max))
        rng.shuffle(order)
        acc: set[Pattern] = set()
        for k, idx in enumerate(order, 1):
            acc |= cand_sets[idx]
            sums[k] += len(acc)
    mean_curve = [round(sums[k] / trials, 1) for k in range(k_max + 1)]
    freq = collections.Counter()
    for p in candidates:
        freq[sum(1 for s in surf_order if p in surf_patterns[s])] += 1
    return {"by_capture": by_capture, "by_surface": by_surface, "last5": last5,
            "flattened": flattened, "mean_curve": mean_curve,
            "singletons": freq.get(1, 0), "doubletons": freq.get(2, 0),
            "surface_frequency": dict(freq)}


# ---------------------------------------------------------------------------
# output
# ---------------------------------------------------------------------------

TSV_COLUMNS = ("kind", "pattern", "class", "scope", "relation", "nearest_census",
               "census_rows", "word_rows", "slice", "rw", "rw_basis",
               "captures", "surfaces", "first_seen", "regions", "is_read_url",
               "known_elsewhere", "query_keys", "drawn_as", "appears_to_be")


def scope_of(pattern: Pattern, regions: set[str]) -> str:
    """LinkedIn's own placement: off-app host, footer-only chrome, or the app."""
    if pattern.host:
        return "off-app"
    if regions and regions <= {"footer"}:
        return "footer"
    return "app"


def route_words(pattern: Pattern) -> list[str]:
    """The literal words of a route, for the word-level census check."""
    words: list[str] = []
    for seg in pattern.segments:
        if seg.startswith("<"):
            continue
        words += [w.lower() for w in re.split(r"[-_.]", seg) if w]
    return [w for w in words if w.isalpha() and len(w) > 2 and w not in STOPWORDS]


def load_annotations(path: Path = ANNOTATIONS) -> dict[tuple[str, str], dict]:
    """Hand judgements keyed by (kind, pattern). Absent file -> none."""
    out: dict[tuple[str, str], dict] = {}
    if not path.exists():
        return out
    header: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        cells = line.split("\t")
        if not header:
            header = cells
            continue
        row = dict(zip(header, cells))
        out[(row.get("kind", ""), row.get("pattern", ""))] = row
    return out


def _read_url(pattern: Pattern) -> str:
    """The shipped boundary's verdict on a concrete, name-free spelling."""
    if pattern.host:
        return "n/a (host)"
    try:
        from linkedin_server.readonly import is_read_url  # noqa: WPS433
    except Exception:  # noqa: BLE001
        return "unavailable"
    # The shipped substitution: <entity> -> placeholder-slug, <opaque> -> a
    # digit run. <seg> is spelled as an entity, the conservative choice.
    url = drc.concrete("/" + "/".join(
        "<entity>" if s == "<seg>" else s for s in pattern.segments))
    try:
        return "True" if is_read_url(url) else "False"
    except Exception:  # noqa: BLE001
        return "error"


def rows_for_tsv(result: dict, annotations: dict | None = None) -> list[list[str]]:
    annotations = annotations if annotations is not None else load_annotations()
    elsewhere = elsewhere_index()
    out: list[list[str]] = []
    rank = {"PROSE": 0, "FAMILY": 1, "NEW": 2}
    cands = sorted(result["candidates"],
                   key=lambda p: (rank[result["verdicts"][p].klass], p.shape()))
    row_texts = result["row_texts"]
    for pattern in cands:
        v = result["verdicts"][pattern]
        seen = result["patterns"][pattern]
        rw, why = rw_of(pattern, seen.methods)
        kinds: set[str] = set()
        for other, found in elsewhere.items():
            if exact(other, pattern):
                kinds |= found
        words = route_words(pattern)
        word_hits = rows_carrying(words, row_texts) if words else []
        note = annotations.get(("address", pattern.shape()), {})
        cell = {
            "kind": "address", "pattern": pattern.shape(), "class": v.klass,
            "scope": note.get("scope") or scope_of(pattern, seen.regions),
            "relation": v.relation, "nearest_census": v.nearest,
            "census_rows": ",".join(v.rows) or "-",
            "word_rows": (",".join(word_hits[:4]) + (" +%d" % (len(word_hits) - 4)
                          if len(word_hits) > 4 else "")) if word_hits else "-",
            "slice": note.get("slice") or v.slice,
            "rw": note.get("rw") or rw,
            "rw_basis": (why if not note.get("rw") or note["rw"] == rw
                         else "hand judgement; the path alone reads %s (%s)" % (rw, why)),
            "captures": str(len(seen.captures)), "surfaces": str(len(seen.surfaces)),
            "first_seen": seen.first,
            "regions": "+".join(sorted(seen.regions)) or "-",
            "is_read_url": _read_url(pattern),
            "known_elsewhere": "+".join(sorted(kinds)) or "no",
            "query_keys": ",".join(sorted(seen.keys)[:8]) or "-",
            "drawn_as": " | ".join(result["drawn_as"].get(pattern, [])) or "-",
            "appears_to_be": note.get("appears_to_be") or "-",
        }
        out.append([cell[c] for c in TSV_COLUMNS])
    for tpl in sorted(result["templates"]):
        verdict, _hits = result["control_verdicts"][tpl]
        if verdict != "CANDIDATE":
            continue
        seen = result["templates"][tpl]
        note = annotations.get(("control", tpl), {})
        cell = {c: "-" for c in TSV_COLUMNS}
        cell.update({
            "kind": "control", "pattern": tpl, "class": "CONTROL",
            "scope": note.get("scope") or "app",
            "slice": note.get("slice") or "?", "rw": note.get("rw") or "?",
            "rw_basis": ("hand judgement from the label" if note.get("rw")
                         else "a control; direction not evident from a label"),
            "captures": str(len(seen.captures)), "surfaces": str(len(seen.surfaces)),
            "first_seen": seen.first,
            "drawn_as": "%d distinct labels" % len(seen.drawn_as),
            "appears_to_be": note.get("appears_to_be") or "-",
        })
        out.append([cell[c] for c in TSV_COLUMNS])
    return out


def write_tsv(result: dict, path: Path = OUT_TSV) -> int:
    lines, n = tsv_lines(result)
    path.write_text("\n".join(lines) + "\n", encoding="ascii")
    return n


def tsv_lines(result: dict, annotations: dict | None = None) -> tuple[list[str], int]:
    """The table ``--write`` would write, as lines, and its data-line count.

    Split out of ``write_tsv`` so ``--check`` compares the table it WOULD
    write with the one committed, through the one function that writes it --
    a checker with its own copy of the format is a second writer that can
    disagree with the first.
    """
    body = rows_for_tsv(result, annotations)
    veto = result["veto"]
    lines = [
        "# COMPLETENESS CANDIDATES -- generated by scripts/completeness_harvest.py --write",
        "#",
        "# Every line is a route shape or a control template that LinkedIn DREW on a",
        "# page this repository captured, and that no census capability row carries.",
        "# A CANDIDATE, NOT A CENSUS ROW. Nothing here is navigated or allowlisted.",
        "#",
        "# class    PROSE   only census prose or a census table note carries it",
        "#          FAMILY  a census address is its prefix, or it is one's",
        "#                  (relation child-of / parent-of / sibling)",
        "#          NEW     no census address shares its first segment",
        "#          CONTROL a control template no census row carries every word of",
        "# scope    off-app (another linkedin host) | footer (drawn only in LinkedIn's",
        "#          footer landmark) | app | a hand annotation (docs, chrome)",
        "# word_rows  census rows carrying EVERY literal word of the route: the",
        "#          capability may be recorded in words without its address. '-' is",
        "#          the stronger signal: neither the address nor its words",
        "# captures / surfaces  how many captures, and distinct surfaces, drew it",
        "# regions  LinkedIn's own landmarks the address was drawn inside",
        "# is_read_url  the SHIPPED boundary on a name-free spelling, re-taken each run",
        "# known_elsewhere  audit / code / script / test files that name the same shape",
        "# appears_to_be / slice / rw  hand judgement where annotated, else derived",
        "#",
        "# Every variable segment is <entity>, <opaque> or <seg>; controls carry <X> and",
        "# <n>. No id, slug, name or query value is in this file. Exact-value veto: %s."
        % ("ARMED" if veto.armed else "DISARMED (%s)" % veto.why),
        "#",
        "# Method and findings: _audit/2026-09-23-completeness-probe.md",
        "# Verdicts (ADMIT / RECORDED / OUT, one per app-scope candidate) are the",
        "# verdict columns of completeness-annotations.tsv; an ADMIT or RECORDED route",
        "# is a census row now and leaves this table. _audit/2026-09-24-lane-y2-admission.md",
        "\t".join(TSV_COLUMNS),
    ]
    for row in body:
        text = "\t".join(row)
        if not text.isascii():
            raise SystemExit("refusing to write a non-ASCII line: %r" % row[1])
        lines.append(text)
    return lines, len(body)


# ---------------------------------------------------------------------------
# the verdict layer, and the table at a fixed point
# ---------------------------------------------------------------------------

def _census_row_ids(census_dir: Path = CENSUS) -> set[str]:
    """Every ``<slice> <id>`` a slice file writes as a table row, off the shipped parse."""
    ids: set[str] = set()
    for letter, name in ccs.SLICES.items():
        path = census_dir / name
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.startswith("|") or not ccs.ROW.match(line):
                continue
            cells = ccs.cells(line)
            if len(cells) < 3:
                continue
            rid = _row_id(letter, cells)
            if rid:
                ids.add(rid)
    return ids


def _table_lines(path: Path) -> list[dict]:
    """The data lines of a committed candidates table, as dicts. Absent -> []."""
    if not path.exists():
        return []
    out: list[dict] = []
    for line in path.read_text(encoding="ascii").splitlines():
        if not line or line.startswith("#") or line.startswith("kind\t"):
            continue
        out.append(dict(zip(TSV_COLUMNS, line.split("\t"))))
    return out


def verdict_problems(table: Path = OUT_TSV, annotations: Path = ANNOTATIONS,
                     census_dir: Path = CENSUS) -> list[str]:
    """Everything wrong with the verdict layer, each naming its line.

    Needs no capture, so it runs in CI. Three failures, each a way the layer
    could say more than the tree bears out:

      * an APP-scope line in the table with no verdict, or with ADMIT or
        RECORDED -- an adjudicated route that is still a candidate means the
        census row said to carry it does not;
      * a verdict off the alphabet, or ADMIT / RECORDED naming no row, or a
        row the census does not have;
      * an OUT with no reason.
    """
    problems: list[str] = []
    notes = load_annotations(annotations)
    rows = _census_row_ids(census_dir)
    for line in _table_lines(table):
        key = (line.get("kind", ""), line.get("pattern", ""))
        if line.get("scope") != "app":
            continue
        verdict = notes.get(key, {}).get("verdict", "").strip()
        if verdict in ("", "-"):
            problems.append("%s %s: an app-scope candidate with no verdict"
                            % (key[0], key[1]))
        elif verdict != "OUT":
            problems.append("%s %s: verdict %s, and the route is still a candidate "
                            "-- the row it names does not carry it"
                            % (key[0], key[1], verdict))
    for key, note in sorted(notes.items()):
        verdict = note.get("verdict", "").strip()
        if verdict in ("", "-"):
            continue
        if verdict not in VERDICTS:
            problems.append("%s %s: verdict %r is off %s" % (key[0], key[1], verdict,
                                                              VERDICTS))
            continue
        named = [r.strip() for r in note.get("verdict_rows", "").split(",")
                 if r.strip() and r.strip() != "-"]
        if verdict == "OUT":
            if len(note.get("verdict_basis", "").strip()) < 12:
                problems.append("%s %s: OUT with no reason" % key)
            continue
        if not named:
            problems.append("%s %s: %s names no census row" % (key[0], key[1], verdict))
        for rid in named:
            if rid not in rows:
                problems.append("%s %s: %s names %s, which no slice file writes as a row"
                                % (key[0], key[1], verdict, rid))
    return problems


def check(result: dict, table: Path = OUT_TSV, annotations: Path = ANNOTATIONS,
          census_dir: Path = CENSUS) -> int:
    """``--check``: the committed table is what ``--write`` would write, and the
    verdict layer holds. Exit 1 naming every difference; 0 otherwise.

    A FIXED POINT, NOT A SNAPSHOT. The table is a function of the captures, the
    census and the annotations; regenerating it over the same corpus must
    reproduce it byte for byte. A difference means one of the three moved and
    nobody regenerated -- or that the table was edited by hand.
    """
    want, _n = tsv_lines(result, load_annotations(annotations))
    have = table.read_text(encoding="ascii").splitlines() if table.exists() else []
    failures = 0
    if want != have:
        def keyed(lines):
            return {tuple(l.split("\t")[:2]): l for l in lines
                    if l and not l.startswith("#") and not l.startswith("kind\t")}
        w, h = keyed(want), keyed(have)
        print("=== FIXED POINT: the committed table is NOT what --write would write")
        for k in sorted(set(w) - set(h)):
            print("    would ADD     %s %s" % k)
        for k in sorted(set(h) - set(w)):
            print("    would REMOVE  %s %s" % k)
        changed = sorted(k for k in set(w) & set(h) if w[k] != h[k])
        for k in changed:
            print("    would CHANGE  %s %s" % k)
        header = [l for l in want if l.startswith("#")] != [l for l in have if l.startswith("#")]
        if header:
            print("    the header differs")
        failures += 1
    else:
        print("=== FIXED POINT: the committed table is exactly what --write would write")
    problems = verdict_problems(table, annotations, census_dir)
    print("=== VERDICT LAYER: %d problem(s)" % len(problems))
    for p in problems:
        print("    " + p)
    failures += bool(problems)
    return 1 if failures else 0


def report(result: dict) -> None:
    caps = result["captures"]
    veto = result["veto"]
    print("=== CAPTURES")
    tiers = collections.Counter(c.tier for c in caps)
    print("  distinct captures read : %d   %s" % (len(caps), dict(sorted(tiers.items()))))
    print("  distinct surfaces      : %d   (after the folds listed below)"
          % len(set(result["surfaces"].values())))
    for why, labels in sorted(result["set_aside"].items()):
        print("  set aside              : %d  (%s)" % (len(labels), why))
    print("  exact-value veto       : %s" % ("ARMED" if veto.armed else "DISARMED -- " + veto.why))
    print()
    print("=== HARVEST")
    for key, n in sorted(result["totals"].items()):
        print("  %-58s %6d" % (key, n))
    print("  %-58s %6d" % ("distinct address patterns", len(result["patterns"])))
    print("  %-58s %6d" % ("distinct control templates", len(result["templates"])))
    for kind, n in sorted(veto.hits.items()):
        print("  %-58s %6d" % ("VETOED " + kind, n))
    print()
    print("=== CENSUS")
    census = result["census"]
    print("  census address tokens  : %d  (row-level %d, prose-level %d)" % (
        len(census), sum(1 for c in census if c.level == "row"),
        sum(1 for c in census if c.level == "prose")))
    print("  distinct census shapes : %d" % len({c.pattern for c in census}))
    print()
    print("=== ADDRESS CLASSES")
    klass = collections.Counter(v.klass for v in result["verdicts"].values())
    for k in ("ROW", "PROSE", "FAMILY", "NEW"):
        print("  %-7s %4d" % (k, klass.get(k, 0)))
    print("  CANDIDATES (PROSE+FAMILY+NEW): %d" % len(result["candidates"]))
    by_slice = collections.Counter(result["verdicts"][p].slice for p in result["candidates"])
    print("  candidates by derived slice: %s" % dict(sorted(by_slice.items())))
    print()
    print("=== CONTROL TEMPLATES")
    cv = collections.Counter(v for v, _ in result["control_verdicts"].values())
    for k in ("RECORDED", "CANDIDATE", "UNCLASSIFIABLE"):
        print("  %-15s %4d" % (k, cv.get(k, 0)))
    print()
    curve = result["curve"]
    print("=== SURFACE FOLDS (content, Jaccard >= %.2f)" % SAME_SURFACE_JACCARD)
    for label, into, score in result["folds"]:
        print("  %-40s -> %-30s %.3f" % (label, into, score))
    print()
    print("=== DISCOVERY CURVE, BY SURFACE, CAPTURE ORDER")
    print("  %-34s %-19s %5s %5s %5s %6s %6s %6s" % (
        "surface", "first captured", "pats", "new", "newC", "cumC", "newCt", "cumCt"))
    for s, when, n, new, newc, cum, newt, cumt in curve["by_surface"]:
        print("  %-34s %-19s %5d %5d %5d %6d %6d %6d" % (
            s[:34], when, n, new, newc, cum, newt, cumt))
    print("  last five surfaces added %s new candidate patterns -> %s" % (
        curve["last5"], "FLATTENED" if curve["flattened"] else "NOT FLATTENED"))
    print("  permutation-mean candidates after k surfaces: %s" % curve["mean_curve"])
    print("  candidates drawn on exactly one surface: %d, on two: %d" % (
        curve["singletons"], curve["doubletons"]))


# ---------------------------------------------------------------------------
# controls
# ---------------------------------------------------------------------------

def _planted_document() -> str:
    """A page that draws one planted route and one the census records."""
    return (
        "<html><body>"
        "<script><a href='/zzz-bundled-only/x'>b</a></script>"
        '<a href="/zzz-planted-surface/report/?trk=abc&amp;keywords=secret">Planted</a>'
        '<a href="https://www.linkedin.com/analytics/profile-views/">Views</a>'
        '<a href="/in/placeholder-member/details/skills/">Skills</a>'
        '<button aria-label="Follow Placeholder Person">Follow</button>'
        '<button aria-label="Follow Another Placeholder">Follow</button>'
        "</body></html>")


def _planted_result(census_dir: Path = CENSUS, *, veto: Veto | None = None) -> dict:
    """``run`` over the planted document alone, against the REAL census."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "cap-planted.html"
        page.write_text(_planted_document(), encoding="utf-8")
        cap = Capture(page, "planted", "control", "2026-01-01T00:00:00",
                      hashlib.sha256(page.read_bytes()).hexdigest())
        return run(Path(tmp), veto=veto or Veto(load_wordlist=False),
                   census_dir=census_dir, captures=[cap])


def control() -> int:
    """Each control can void the run; each is then driven into its failing state."""
    failures = 0
    result = _planted_result()
    texts = {p.shape(): result["verdicts"][p] for p in result["patterns"]}

    print("=== CONTROL 1  A PLANTED ROUTE ABSENT FROM THE CENSUS IS A CANDIDATE")
    planted = texts.get("/zzz-planted-surface/report")
    print("    /zzz-planted-surface/report -> %s" % (planted.klass if planted else "NOT HARVESTED"))
    if not planted or planted.klass != "NEW":
        print("    VOID -- the planted route did not come out NEW")
        failures += 1
    else:
        print("    NEW, and a candidate.  PASS")

    print("=== CONTROL 2  A CENSUS-RECORDED ROUTE IS NOT A CANDIDATE")
    recorded = texts.get("/analytics/profile-views")
    print("    /analytics/profile-views -> %s" % (recorded.klass if recorded else "NOT HARVESTED"))
    if not recorded or recorded.klass != "ROW":
        print("    VOID -- a route the census carries in a row came out a candidate")
        failures += 1
    else:
        print("    ROW (%s), not a candidate.  PASS" % ",".join(recorded.rows[:3]))

    print("=== CONTROL 3  NO NAME, NO QUERY VALUE AND NO BUNDLED ROUTE LEAVES")
    blob = " ".join(texts) + " " + " ".join(
        k for s in result["patterns"].values() for k in s.keys)
    leaks = [n for n in ("placeholder-member", "secret", "abc", "zzz-bundled-only")
             if n in blob]
    print("    leaked needles: %d of 4" % len(leaks))
    if leaks:
        print("    VOID -- %s" % ", ".join(leaks))
        failures += 1
    else:
        print("    none.  PASS")

    print("=== CONTROL 4  A CONTROL LABEL LEAVES AS A TEMPLATE, NEVER AS A NAME")
    tpls = sorted(result["templates"])
    print("    templates: %s" % tpls)
    if any("Placeholder" in t or "Person" in t or "Another" in t for t in tpls) \
            or "Follow <X>" not in tpls:
        print("    VOID -- a name survived, or the template was not learned")
        failures += 1
    else:
        print("    two labels, one template; the census uses 'follow', the names "
              "left as <X>.  PASS")

    print("=== CONTROL 5  EACH CONTROL ABOVE, DRIVEN INTO ITS FAILING STATE")
    driven = 0
    # 1 and 2: an empty census makes the recorded route a candidate.
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        empty = Path(tmp)
        for name in ccs.SLICES.values():
            (empty / name).write_text("# emptied\n", encoding="utf-8")
        broken = _planted_result(empty)
        bt = {p.shape(): broken["verdicts"][p].klass for p in broken["patterns"]}
    print("    census emptied: /analytics/profile-views -> %s" % bt.get("/analytics/profile-views"))
    driven += bt.get("/analytics/profile-views") == "NEW"
    # 3: the shipped reducer swapped for the identity leaks the planted slug
    # through the REAL harvest, not through a string built here.
    shipped = reducer().shape_path
    try:
        reducer().shape_path = lambda href, depth=3: re.sub(
            r"^https?://[^/]+", "", href).split("?")[0].rstrip("/") or "/"
        bare = _planted_result()
        emitted = " ".join(p.shape() for p in bare["patterns"])
    finally:
        reducer().shape_path = shipped
    print("    reducer bypassed: planted slug in the output -> %s"
          % ("placeholder-member" in emitted))
    driven += "placeholder-member" in emitted
    # 4: a vocabulary widened to hold the name lets the first word through.
    loose = template_of("Placeholder Person", frozenset({"placeholder", "person"}))
    print("    vocabulary widened: 'Placeholder Person' -> %s" % loose)
    driven += bool(loose) and "Placeholder" in loose
    print("    controls that FAILED when broken: %d of 3" % driven)
    if driven != 3:
        print("    VOID -- a control could not be made to fail")
        failures += 1
    else:
        print("    every mechanism was shown load-bearing.  PASS")
    print()
    if failures:
        print("CONTROL: %d FAILED -- every number from this run is void" % failures)
        return 1
    print("control: all five passed -- a count below is a measurement")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--control", action="store_true")
    parser.add_argument("--write", action="store_true",
                        help="write _audit/_census/completeness-candidates.tsv")
    parser.add_argument("--state-root", default="",
                        help="the checkout holding _state/ (default: the main checkout)")
    parser.add_argument("--no-worktrees", action="store_true")
    parser.add_argument("--no-fixtures", action="store_true")
    parser.add_argument("--captured-before", default="",
                        help="keep only captures taken before this UTC stamp "
                             "(e.g. 2026-09-23T00:00:00): the adjudicated corpus")
    parser.add_argument("--check", action="store_true",
                        help="exit 1 unless the committed table is what --write "
                             "would write and every app-scope line has a verdict")
    args = parser.parse_args(argv)
    if args.control:
        return control()
    state_root = Path(args.state_root) if args.state_root else main_checkout(ROOT)
    captures, set_aside = select_corpus(
        state_root, worktrees=not args.no_worktrees, fixtures=not args.no_fixtures,
        captured_before=args.captured_before)
    result = run(state_root, captures=captures, set_aside=set_aside)
    if not result["captures"]:
        print("NO CAPTURES FOUND under %s. An absence is not a zero; run from a "
              "machine that holds the captures." % "the state root")
        return 2
    report(result)
    if args.check:
        print()
        return check(result)
    if args.write:
        n = write_tsv(result)
        print()
        print("wrote %s (%d lines)" % (OUT_TSV.relative_to(ROOT).as_posix(), n))
    return 0


if __name__ == "__main__":
    sys.exit(main())
