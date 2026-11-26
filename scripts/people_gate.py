"""PEOPLE-GATE v2: may a live capture KEEP the raw page it is about to write?

WHO CALLS IT. The live lane's runner (gitignored, ``_state/live-runner/``)
keeps a SKELETON of every page it loads, and on an S+R line the RAW page too,
but only when this gate says ``keep-raw``. A raw page that draws other people
is never kept. Lane infra26 built it, 2026-11-26, and its record is
``_audit/2026-11-26-infra26.md`` section 4.

WHY v2. Session 11's gate (v1) counted ``/in/<slug>`` links in the LIVE DOM
and kept a raw page at zero. Two of its kept raws held people anyway, and the
orchestrator deleted both copies of each:

* the unfollowed list drew 44 members by name, with no profile link
  (UNFOLLOWED-RAW-DELETED, PEOPLE-GATE-COUNTS-NAME-SLOTS);
* a company's events page drew members by urn, by photo, by a picture's
  accessible text and in social-proof lines, plus speakers in free event text
  (the 14:05 entry: rawsweep26's report).

THE RULES. The orchestrator's six, from the 14:05 entry, are kept in its
order. Each fires on the HTML STRING, and each firing is a reason the verdict
names:

  R1  member-ids     a member urn or member id that is not his, anywhere in
                     the string, payloads included
  R2  member-photos  a profile-display asset id that is not his, in a DOM
                     ``<img>``, anywhere in the string, or in a payload
                     vectorImage
  R3  photo-a11y     a PhotoFilterPicture's ``a11yText`` that holds a name
                     other than his
  R4  social-proof   a link-less social-proof line naming someone: "<name>
                     and N others ...", "<name> & N other connections work
                     here", "<name> works here", "<name> is hiring"
  R5  events-class   an events page is SKELETON-ONLY by page class: its
                     address has an ``events`` segment, or its payload carries
                     an event entity. Free-text speakers cannot be caught by
                     shape.
  R6  the string     the verdict is about the exact string judged, and it
                     carries that string's digest (``Verdict.covers``). Judge
                     the string you WRITE, never the live DOM before
                     ``page.content()``.

Two more are kept from v1 and from PEOPLE-GATE-COUNTS-NAME-SLOTS:

  L1  member-links   a ``/in/<slug>`` link that is not his: v1's own rule,
                     now read off the string, not the DOM
  N1  name-slots     a value in a person slot the repo's fixture guard reads
                     (``tests/test_fixtures_hold_only_synthetic_people.
                     candidates_in``, imported, never copied), or in a profile
                     card's name element, that is neither his nor reduced
                     to shape

HIS OWN IDENTITY is learned at runtime, held only as one-way digests, and
never printed. The learning ports rawsweep26's Identity.learn, and it has two
sources: the navigation bar's own photo (its alt is his name, its src his
photo asset), and the payload entity whose ``publicIdentifier`` is his slug
(his member urn, his full name, his photo). A page that draws neither, which
is every server-driven page measured, cannot teach it. So ``own_cache`` keeps
what earlier pages taught, as digests tied to his slug's digest, in the
gitignored file the caller names. That file is this module's only write.
Only FULL name forms count as his. A first name alone is somebody else's,
because "<first name> & N other connections work here" names a connection.

FAIL CLOSED. Anything this cannot establish counts AGAINST keeping the raw:
an id it cannot tie to him is "not his"; a name-slot reader that fails to
import withholds; a page it cannot parse withholds. A withheld raw costs one
offline reading (the skeleton is always kept). A kept raw with a person in
it cannot be taken back once another lane has read it.

WHAT THIS CANNOT SEE: a name in free prose that matches no slot or template,
on a page that is not an events page. That is R5's whole argument, and the
reason the hard rule stays a rule and not this file's promise.

Every reason is a closed sentence with counts. No value from the page
(name, id, slug, link, text) is ever in a reason, a count key or a repr.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping, Optional
from urllib.parse import unquote, urlsplit

KEEP = "keep-raw"
WITHHOLD = "withhold-raw"

#: The rule ids, in the order the verdict reports them.
RULES = ("R1", "R2", "R3", "R4", "R5", "L1", "N1", "PARSE")

# ---------------------------------------------------------------------------
# Shapes (ported from rawsweep26 sweep.py; each one has a planted control in
# tests/test_people_gate.py)
# ---------------------------------------------------------------------------

#: Member urns, in any of the four types LinkedIn draws, plain or
#: percent-encoded. The id is group 2.
MEMBER_URN = re.compile(
    r"urn(?::|%3A)li(?::|%3A)(fsd_profile|fs_miniProfile|fs_profile|member)(?::|%3A)"
    r"([A-Za-z0-9_-]+)")
#: A bare encoded member id. NO WORD BOUNDARY: ``%3AACoAA`` must match (the
#: identity guard learned this the hard way, tests/test_no_committed_identity).
MEMBER_TOKEN = re.compile(r"ACoAA[A-Za-z0-9_-]{10,}")
#: A media asset in a url: its id and the kind segment after it.
MEDIA_ASSET = re.compile(r"dms/image/(?:v2/)?(?P<id>[A-Za-z0-9_-]{8,})/(?P<kind>[a-z][a-z-]*?)"
                         r"(?:-shrink|-crop|-scale|_\d|/|\?|$)")
#: The kind half of a vectorImage artifact's path segment.
SEGMENT_KIND = re.compile(r"^(?:\d+_\d+/)?(?P<kind>[a-z][a-z-]*?)(?:-shrink|-crop|-scale|_\d|/|$)")
MEMBER_LINK = re.compile(r"^(?:https?://(?:www\.)?linkedin\.com)?/in/([^/?#]+)", re.IGNORECASE)
#: A profile card's name element (the unfollowed list's measured slot;
#: linkedin_server/unfollowed_list.NAME_SELECTOR).
NAME_SLOT_ATTRS = ("data-test-profile-card-name",)

_P = r"[^\s,;:!?()|\u00b7\u2022\"<>{}\[\]]"
_Q = r"[^,;:!?()|\u00b7\u2022\"<>{}\[\]]"
_PL = r"[^\s;:!?()|\u00b7\u2022\"<>{}\[\]]"
_QL = r"[^;:!?()|\u00b7\u2022\"<>{}\[\]]"
_N = "(?P<name>" + _P + _Q + "{0,78}?)"
_NL = "(?P<name>" + _PL + _QL + "{0,160}?)"
_COUNT = r"(?:\d[\d,.]*[KkMm]?|one|two|three|four|five|six|seven|eight|nine|ten)"

#: R4's templates: (closed label, pattern, whether the capture is a list).
SOCIAL_PROOF = (
    ("and-n-others", re.compile("^" + _NL + r"\s+(?:and|&)\s+" + _COUNT + r"\s+others?\b"), True),
    ("works-here", re.compile("^" + _NL + r"\s+(?:works|worked|work|is working|used to work)"
                              r" (?:here|at)\b"), True),
    ("is-hiring", re.compile("^" + _N + r"\s+is (?:hiring|recruiting)\b"), False),
)
_SPLIT_LIST = re.compile(r",\s+|\s+and\s+|\s*&\s*")

UI_WORDS = frozenset("""Status Filter Sort Date Recently Newly Just Your Their His Her Its Our This
That These Those Someone Somebody Anyone Everyone Member Members People Person User Users Viewer
Viewers LinkedIn Premium Company Page Group Event Job Jobs All Who Everybody Nobody Connection
Connections Follower Followers Others Unknown Undefined Null None Close Dismiss Show Hide Search
Messaging Notifications Home Network Me More Menu Clicked Saved Applied Archived Interview Offer
Learning Help Settings Privacy Ad Ads Experience Skills Media Image Video Document Photo Picture
Profile Logo Banner Cover Status""".split())
_UI_LOWER = frozenset(w.lower() for w in UI_WORDS) | {"you", "your", "yourself", "me", "my"}
ORG_SUFFIX = re.compile(
    r"\b(?:Inc|Ltd|LLC|LLP|PLC|GmbH|Pvt|Private|Limited|Corp|Corporation|Company|Co|Technologies|"
    r"Technology|Tech|Solutions|Systems|Services|Software|Labs|Group|Holdings|Consulting|Consultancy|"
    r"Ventures|Partners|Capital|Media|Networks|Network|Foundation|Global|Bank|University|College|"
    r"School|Institute|Academy|Analytics|Digital|Infotech|Infosystems|Industries|International|"
    r"Enterprises|Studio|Studios|AI|Cloud|Data|Health|Healthcare|Pharma|Motors|Energy|Logistics|"
    r"Retail|Finance|Financial|Insurance|Club|Association|Society|Council|Agency|Hub|Community|"
    r"Platform|Platforms|Innovations|Innovation)\b\.?")
_ORG_TYPES = (".Company", ".School", ".OrganizationalPage", ".Organization", ".Showcase")
_EVENT_TYPES = (".ProfessionalEvent",)

_VOID = frozenset("area base br col embed hr img input link meta param source track wbr".split())
_UNREAD = frozenset({"script", "style", "template", "noscript"})
_LABEL_ATTRS = ("aria-label", "alt", "title", "placeholder", "aria-description")


def norm(value: str) -> str:
    return " ".join(str(value).split()).strip(" .,'\u2019\"")


def is_reduced_to_shape(value: str) -> bool:
    """Every letter X or x: a skeleton's shaped text, which names nobody."""
    letters = [c for c in value if c.isalpha()]
    return bool(letters) and all(c in "Xx" for c in letters)


# ---------------------------------------------------------------------------
# One pass over the string
# ---------------------------------------------------------------------------


class _Page(HTMLParser):
    """Texts, labels, payload blocks, images and links of one document."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, bool]] = []          # (tag, unread)
        self.texts: list[str] = []                       # visible and hidden text nodes
        self.labels: list[str] = []                      # label attribute values
        self.code: list[str] = []                        # <code> payload blocks
        self._code: Optional[list[str]] = None
        self.img_srcs: list[str] = []
        self.me_alts: list[str] = []
        self.me_srcs: list[str] = []
        self.member_slugs: list[str] = []
        self.org_texts: set[str] = set()
        self.name_slots: list[str] = []
        self._slot_depth: Optional[int] = None
        self._slot_text: list[str] = []
        self._org_link_depth: Optional[int] = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        a = {k: (v or "") for k, v in attrs}
        unread = tag in _UNREAD or (bool(self.stack) and self.stack[-1][1])
        for attr in _LABEL_ATTRS:
            v = " ".join(a.get(attr, "").split())
            if v:
                self.labels.append(v)
        if tag == "img":
            src = a.get("src", "") or a.get("data-delayed-url", "")
            self.img_srcs.append(src)
            if "global-nav__me-photo" in a.get("class", "").split():
                if a.get("alt"):
                    self.me_alts.append(" ".join(a["alt"].split()))
                self.me_srcs.append(src)
            m = re.match(r"^(?P<org>.+?) logo$", " ".join(a.get("alt", "").split()))
            if m:
                self.org_texts.add(norm(m.group("org")).lower())
        if tag == "a":
            href = a.get("href", "")
            m = MEMBER_LINK.match(href)
            if m:
                self.member_slugs.append(unquote(m.group(1)).lower())
            if any(k in href for k in ("/company/", "/school/", "/showcase/")):
                self._org_link_depth = len(self.stack)
        if any(k in a for k in NAME_SLOT_ATTRS) and self._slot_depth is None:
            self._slot_depth = len(self.stack)
            self._slot_text = []
        if tag == "code":
            self._code = []
        if tag not in _VOID:
            self.stack.append((tag, unread))

    def handle_endtag(self, tag: str) -> None:
        if tag == "code" and self._code is not None:
            self.code.append("".join(self._code))
            self._code = None
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break
        if self._slot_depth is not None and len(self.stack) <= self._slot_depth:
            text = norm(" ".join(self._slot_text))
            if text:
                self.name_slots.append(text)
            self._slot_depth = None
        if self._org_link_depth is not None and len(self.stack) <= self._org_link_depth:
            self._org_link_depth = None

    def handle_data(self, data: str) -> None:
        if self._code is not None:
            self._code.append(data)
            return
        if self.stack and self.stack[-1][1]:
            return
        text = " ".join(data.split())
        if not text:
            return
        self.texts.append(text)
        if self._slot_depth is not None:
            self._slot_text.append(text)
        if self._org_link_depth is not None:
            self.org_texts.add(norm(text).lower())


def _json_blocks(blocks: Iterable[str]) -> list[Any]:
    out = []
    for blob in blocks:
        b = blob.strip()
        if b[:1] in ("{", "["):
            try:
                out.append(json.loads(b))
            except ValueError:
                continue
    return out


def _dicts(obj: Any) -> Iterator[dict]:
    stack = [obj]
    while stack:
        cur = stack.pop()
        if isinstance(cur, dict):
            yield cur
            stack.extend(cur.values())
        elif isinstance(cur, list):
            stack.extend(cur)


def _strings(obj: Any) -> Iterator[str]:
    stack = [obj]
    while stack:
        cur = stack.pop()
        if isinstance(cur, dict):
            stack.extend(cur.values())
        elif isinstance(cur, list):
            stack.extend(cur)
        elif isinstance(cur, str):
            s = " ".join(cur.split())
            if s and not s.startswith(("urn:", "http", "/", "com.linkedin")) and len(s) <= 400:
                yield s


def _vector_assets(d: dict) -> list[tuple[str, str]]:
    """(asset id, kind) of every vectorImage under one dict."""
    found = []
    for sub in _dicts(d):
        root = sub.get("rootUrl")
        if isinstance(root, str) and "dms/image" in root:
            m = re.search(r"dms/image/(?:v2/)?([A-Za-z0-9_-]{8,})", root)
            kinds = set()
            for art in sub.get("artifacts") or []:
                seg = art.get("fileIdentifyingUrlPathSegment") if isinstance(art, dict) else None
                k = SEGMENT_KIND.match(seg or "")
                if k:
                    kinds.add(k.group("kind"))
            if m:
                found.extend((m.group(1), k) for k in (kinds or {"unknown"}))
    return found


def _type_of(d: dict) -> str:
    t = d.get("$type")
    return t if isinstance(t, str) else ""


# ---------------------------------------------------------------------------
# His own identity, learned at runtime
# ---------------------------------------------------------------------------


#: An encoded member id is a fixed 39 characters. LinkedIn's server-driven
#: pages glue a section name straight onto it in component keys (measured on
#: session 11's own experience page: his id followed by letters, no
#: separator), so a longer run is read as the id and what follows it, and the
#: rest is searched for a further id.
MEMBER_TOKEN_LENGTH = 39


def _h(value: str) -> str:
    """The one-way form every identity value is held in, in memory and on
    disk: his identity is compared, never kept in the clear."""
    return "sha256:" + hashlib.sha256(value.encode("utf-8", "surrogatepass")).hexdigest()


def member_ids_in(text: str) -> set:
    """Every member id in a string: urn ids of the four member types (plain or
    percent-encoded), and bare encoded tokens, each split at the fixed id
    length so a glued suffix is never part of an id and a glued SECOND id is
    found as one."""
    raw = [m.group(2) for m in MEMBER_URN.finditer(text)]
    raw += [m.group(0) for m in MEMBER_TOKEN.finditer(text)]
    ids = set()
    for value in raw:
        if not value.startswith("ACoAA"):
            ids.add(value)                      # a numeric member id, whole
            continue
        rest = value
        while rest.startswith("ACoAA"):
            ids.add(rest[:MEMBER_TOKEN_LENGTH])
            rest = rest[MEMBER_TOKEN_LENGTH:]
            at = rest.find("ACoAA")
            rest = rest[at:] if at >= 0 else ""
    return ids


@dataclass(frozen=True)
class Own:
    """What is HIS: one-way digests of his slug, member ids, photo asset ids
    and FULL name forms (two words or more). Never printed: the repr says how
    much was learned, never what. A first name alone is not his: the
    social-proof line "<first name> & N other connections work here" names a
    CONNECTION, so his first name there is somebody else's."""

    slug: str = ""
    member_ids: frozenset = frozenset()
    photo_ids: frozenset = frozenset()
    names: frozenset = frozenset()

    def __repr__(self) -> str:
        return "Own(slug=%s, member_ids=%d, photo_ids=%d, names=%d)" % (
            "set" if self.slug else "absent", len(self.member_ids), len(self.photo_ids),
            len(self.names))

    def has_id(self, value: str) -> bool:
        return _h(value) in self.member_ids

    def has_photo(self, value: str) -> bool:
        return _h(value) in self.photo_ids

    def has_name(self, value: str) -> bool:
        return _h(norm(value).lower()) in self.names

    def to_json(self) -> dict:
        return {"slug": _h(self.slug) if self.slug else "", "member_ids": sorted(self.member_ids),
                "photo_ids": sorted(self.photo_ids), "names": sorted(self.names)}


def _full_name(value: str) -> Optional[str]:
    v = norm(value).lower()
    return v if len(v.split()) >= 2 else None


def learn_own(page: _Page, objs: list[Any], slug: str, *, member_ids: Iterable[str] = (),
              photo_ids: Iterable[str] = (), names: Iterable[str] = (),
              known: Optional[Own] = None) -> Own:
    """His identity from what this page draws of him, plus what is known.

    Two sources only, both his by construction: the navigation bar's own
    photo (``img.global-nav__me-photo``: its alt is his name, its src his
    asset) and the payload entity whose ``publicIdentifier`` is his slug.
    ``known`` is what earlier pages taught (see ``own_cache`` on
    :func:`judge`); it counts only when it was learned for this same slug."""
    slug = (slug or "").strip().lower()
    ids = {_h(i) for v in member_ids for i in member_ids_in(str(v)) | {str(v)}}
    photos = {_h(str(v)) for v in photo_ids}
    forms = {_h(f) for f in map(_full_name, names) if f}
    if known is not None and known.slug == slug and slug:
        ids |= known.member_ids
        photos |= known.photo_ids
        forms |= known.names
    for alt in page.me_alts:
        if _full_name(alt):
            forms.add(_h(_full_name(alt)))
    for src in page.me_srcs:
        m = MEDIA_ASSET.search(src)
        if m:
            photos.add(_h(m.group("id")))
    if slug:
        for o in objs:
            for d in _dicts(o):
                if str(d.get("publicIdentifier") or "").lower() != slug:
                    continue
                fn, ln = d.get("firstName"), d.get("lastName")
                if isinstance(fn, str) and isinstance(ln, str) and _full_name(fn + " " + ln):
                    forms.add(_h(_full_name(fn + " " + ln)))
                for k in ("entityUrn", "objectUrn", "dashEntityUrn", "*profile", "profileUrn"):
                    ids |= {_h(i) for i in member_ids_in(str(d.get(k) or ""))}
                for pid, kind in _vector_assets(d):
                    if kind.startswith("profile-display"):
                        photos.add(_h(pid))
    return Own(slug, frozenset(ids), frozenset(photos), frozenset(forms))


def read_own_cache(path: Any, slug: str) -> Optional[Own]:
    """What earlier pages taught about him, or None (no file, unreadable, or
    learned for another slug: an identity that cannot be tied to THIS slug
    clears nothing)."""
    if path is None or not slug:
        return None
    try:
        with open(str(path), encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return None
    slug = slug.strip().lower()
    if not isinstance(data, dict) or data.get("slug") != _h(slug):
        return None
    def digests(key: str) -> frozenset:
        values = data.get(key)
        return frozenset(v for v in values if isinstance(v, str) and v.startswith("sha256:"))             if isinstance(values, list) else frozenset()
    return Own(slug, digests("member_ids"), digests("photo_ids"), digests("names"))


def write_own_cache(path: Any, own: Own) -> bool:
    """Persist what was learned: digests only, to the ONE path the caller
    named, atomically. The only write in this module."""
    if path is None or not own.slug:
        return False
    target = str(path)
    tmp = target + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(own.to_json(), fh, indent=1, sort_keys=True)
    Path(tmp).replace(target)
    return True


# ---------------------------------------------------------------------------
# The verdict
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Verdict:
    """keep-raw or withhold-raw, why, and for which string."""

    word: str
    reasons: tuple = ()
    counts: Mapping[str, int] = field(default_factory=dict)
    digest: str = ""
    own: str = ""

    @property
    def keep_raw(self) -> bool:
        return self.word == KEEP

    def covers(self, text: str) -> bool:
        """R6: is ``text`` exactly the string this verdict judged?"""
        return bool(self.digest) and _digest(text) == self.digest

    def __str__(self) -> str:
        return self.word + (": " + "; ".join(self.reasons) if self.reasons else "")


def _digest(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8", "surrogatepass")).hexdigest()


def page_class(url: str = "", key: str = "") -> str:
    """``events`` when the address has an ``events`` path segment, or the
    capture key names one; ``other`` otherwise. By CLASS, so a page is
    skeleton-only before anything on it is read."""
    try:
        segments = [s.lower() for s in urlsplit(url or "").path.split("/") if s]
    except ValueError:
        segments = []
    if "events" in segments or "event" in segments or re.search(r"(?:^|[_-])events?(?:$|[_-])",
                                                                 (key or "").lower()):
        return "events"
    return "other"


def _classify(value: str, own: Own, orgs: set) -> str:
    """Ported from rawsweep26's classify(): who a captured value could be."""
    v = norm(value)
    if not v:
        return "empty"
    lv = v.lower()
    if own.has_name(v):
        return "his"
    if v in UI_WORDS or lv in _UI_LOWER:
        return "interface"
    if lv in orgs or ORG_SUFFIX.search(v):
        return "organisation"
    if any(ch.isdigit() for ch in v):
        return "not-a-name"
    toks = v.split()
    if len(toks) > 5:
        return "prose"
    if all((t[:1].isupper() or not t[:1].isalpha()) for t in toks) or not v.isascii():
        return "person"
    return "lowercase"


def _as_self_links(html: str, slug: str) -> str:
    """His own profile links spelled as the self alias ``/in/me/``, which the
    fixture guard does not read for a link's text: a link to HIM is a self
    link whatever its spelling, and its text ("View profile") names nobody.
    With no slug nothing is rewritten, so nothing is cleared."""
    if not slug:
        return html
    return re.sub(r"(href=[\"'](?:https?://(?:www\.)?linkedin\.com)?/in/)" + re.escape(slug)
                  + r"(?=[/?#\"'])", r"\1me", html, flags=re.IGNORECASE)


def _name_slot_values(html: str, slug: str) -> Optional[list[str]]:
    """The repo guard's person-slot values, or None when it cannot be read."""
    try:
        from tests.test_fixtures_hold_only_synthetic_people import candidates_in
    except Exception:  # noqa: BLE001 - an unreadable slot reader withholds
        return None
    try:
        return [c.value for c in candidates_in(_as_self_links(html, slug))]
    except Exception:  # noqa: BLE001 - a page the guard cannot parse withholds
        return None


def judge(html: str, *, slug: str = "", page_url: str = "", page_key: str = "",
          member_ids: Iterable[str] = (), photo_ids: Iterable[str] = (),
          names: Iterable[str] = (), own_cache: Any = None) -> Verdict:
    """The verdict on ONE string: the one the caller is about to write (R6).

    ``own_cache``: a gitignored path where what this page teaches about HIM
    is kept, as digests, for the pages after it. MEASURED on session 11's
    five clean raws: four are server-driven pages that draw no navigation
    photo class and no payload, so they cannot teach his identity
    themselves. Judged alone, his own avatar on each counted as somebody
    else's and all four were withheld. Taught by the one page that carries his
    entity, all five were kept. Learning stays tied to his slug, so a cache
    from another slug teaches nothing."""
    counts = {rule: 0 for rule in RULES}
    reasons: list[str] = []
    try:
        page = _Page()
        page.feed(html)
        page.close()
    except Exception:  # noqa: BLE001 - a page that cannot be parsed withholds
        counts["PARSE"] = 1
        return Verdict(WITHHOLD, ("PARSE: the page could not be parsed",), counts, _digest(html))
    objs = _json_blocks(page.code)
    known = read_own_cache(own_cache, slug)
    own = learn_own(page, objs, slug, member_ids=member_ids, photo_ids=photo_ids, names=names,
                    known=known)
    learned = own.member_ids or own.photo_ids or own.names
    if own_cache is not None and own.slug and learned and (
            known is None or (own.member_ids, own.photo_ids, own.names)
            != (known.member_ids, known.photo_ids, known.names)):
        write_own_cache(own_cache, own)       # a page that taught nothing writes nothing

    # R1: member urns and bare member tokens, anywhere in the string.
    counts["R1"] = sum(1 for i in member_ids_in(html) if not own.has_id(i))

    # R2: profile-display assets in DOM images, the string, and payloads.
    photos = set()
    for src in page.img_srcs:
        m = MEDIA_ASSET.search(src or "")
        if m and m.group("kind").startswith("profile-display"):
            photos.add(m.group("id"))
    for m in MEDIA_ASSET.finditer(html):
        if m.group("kind").startswith("profile-display"):
            photos.add(m.group("id"))
    for o in objs:
        for pid, kind in _vector_assets(o):
            if kind.startswith("profile-display"):
                photos.add(pid)
    counts["R2"] = sum(1 for pid in photos if not own.has_photo(pid))

    # R3: a PhotoFilterPicture's accessible text holding someone else's name.
    a11y = 0
    for o in objs:
        for d in _dicts(o):
            if _type_of(d).endswith(".PhotoFilterPicture"):
                v = d.get("a11yText")
                if isinstance(v, str) and norm(v) and not own.has_name(v)                         and not is_reduced_to_shape(v):
                    a11y += 1
    counts["R3"] = a11y

    # R4: link-less social-proof lines, in text, labels and payload strings.
    orgs = set(page.org_texts)
    for o in objs:
        for d in _dicts(o):
            if _type_of(d).endswith(_ORG_TYPES) and isinstance(d.get("name"), str):
                orgs.add(norm(d["name"]).lower())
    sources = list(page.texts) + list(page.labels)
    for o in objs:
        sources.extend(_strings(o))
    proof = 0
    for text in sources:
        named = set()                     # one line two templates match is one line
        for _label, rx, is_list in SOCIAL_PROOF:
            m = rx.search(text)
            if not m:
                continue
            parts = _SPLIT_LIST.split(m.group("name")) if is_list else [m.group("name")]
            named |= {norm(p).lower() for p in parts if p and p.strip()
                      and _classify(p, own, orgs) == "person" and not is_reduced_to_shape(p)}
        proof += len(named)
    counts["R4"] = proof

    # R5: an events page by class, or a payload carrying an event entity.
    by_address = page_class(page_url, page_key) == "events"
    by_payload = any(_type_of(d).endswith(_EVENT_TYPES) for o in objs for d in _dicts(o))
    counts["R5"] = int(by_address) + int(by_payload)

    # L1: member links that are not his (v1's rule, on the string).
    counts["L1"] = len({s for s in page.member_slugs if s not in ("me", own.slug)})

    # N1: the repo guard's person slots and profile-card name slots.
    slot_values = _name_slot_values(html, own.slug)
    if slot_values is None:
        counts["N1"] = 1
        reasons.append("N1 name-slots: the fixture guard's slot reader could not run, so "
                       "nothing was cleared")
    else:
        counts["N1"] = sum(1 for v in list(slot_values) + page.name_slots
                           if norm(v) and not own.has_name(v) and not is_reduced_to_shape(v))

    sentences = {
        "R1": "R1 member-ids: %d member id(s) on the page are not his",
        "R2": "R2 member-photos: %d profile photo asset(s) on the page are not his",
        "R3": "R3 photo-a11y: %d picture label(s) hold a name that is not his",
        "R4": "R4 social-proof: %d name(s) in link-less social-proof lines",
        "L1": "L1 member-links: %d profile link(s) to other members",
    }
    for rule in ("R1", "R2", "R3", "R4"):
        if counts[rule]:
            reasons.append(sentences[rule] % counts[rule])
    if counts["R5"]:
        reasons.append("R5 events-class: an events page is skeleton-only (%s)" % " and ".join(
            w for w, on in (("by its address", by_address), ("by its payload", by_payload)) if on))
    if counts["L1"]:
        reasons.append(sentences["L1"] % counts["L1"])
    if slot_values is not None and counts["N1"]:
        reasons.append("N1 name-slots: %d value(s) in person slots are not his" % counts["N1"])
    word = WITHHOLD if any(counts.values()) else KEEP
    return Verdict(word, tuple(reasons), counts, _digest(html), repr(own))
