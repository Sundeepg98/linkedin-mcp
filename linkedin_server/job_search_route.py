"""Which job-search page a search LANDED on, and what may be read off it.

## THE DEFECT THIS CLOSES (lane search-fix26, 2026-11-26)

LinkedIn draws a banner over its classic ``/jobs/search/`` -- "We're gradually
retiring classic job search starting in September" -- and its replacement, the
AI search at ``/jobs/search-results/``, is server-driven UI with no
``/jobs/view/`` link anywhere on it. ``linkedin_search_jobs`` read the classic
page with ``dom.harvest_linked_cards`` keyed on ``dom.JOB_HREF`` and
``allow_empty=True``, and nothing checked where the load landed. Measured by
lane search26 (``scratch/harvest_entry.py``, the shipped harvest's entry step
emulated): **0 keyed cards on the AI page, against 7 on both classic raw
captures**. So a redirect to the AI page would have come back as an EMPTY
SHORTLIST with a note blaming the filters -- not as a failure.

EMPTY MUST BE DISTINGUISHABLE FROM BROKEN. This module is the vocabulary of the
two vetoes and the fallback that close it:

* **THE LANDING VETO.** :func:`landing_route` classifies the landed address as
  :data:`CLASSIC`, :data:`AI` or :data:`OTHER`, by WHOLE PATH SEGMENTS at fixed
  positions (``anchors.py``'s scar: never containment). Only the classic page
  goes to the classic reader. The AI page goes to the fallback. Anything else
  refuses, and the refusal names the route as a SHAPE (``landing.withheld``),
  never the address.
* **THE RENDER VETO.** A read that produced no card is refused unless the page
  drew LinkedIn's OWN empty state, matched by equality against
  :data:`CLASSIC_EMPTY_STATES` / :data:`AI_EMPTY_STATES`. **BOTH ARE EMPTY**,
  because no capture on disk shows either page with no results (lane
  search-fix26 searched every raw capture and fixture for one: none; search26
  gap G7). An empty vocabulary is not a disarmed veto: it means NO zero is
  believed until one is captured, and :func:`zero_is_believable` is shown
  believing a zero under a planted vocabulary, so the mechanism is proven to
  speak before it is relied on to stay silent.
* **THE FALLBACK** (ruling ``Q-SEARCH-ROUTE-POLICY``: classic is the PRIMARY
  route while it serves; the AI route is the FALLBACK and REFUSES every filter
  not yet measured on it). :data:`AI_ROUTE_HONOURED` is the honoured set --
  ``keywords`` only, the one parameter a capture shows the AI route serving
  (live session 11, 2026-11-26, ``/jobs/search-results/?keywords=``, relation
  SERVED). ``easy_apply`` is applied LOCALLY (ruling
  ``AI-EASY-APPLY-POST-FILTER``): :func:`easy_apply_post_filter` keeps the
  cards that draw their own Easy Apply mark and its receipt says so, and the
  page's own toggle stays unmeasured and unpressed. :func:`ai_route_refusals`
  names every other argument a call set.
  The fallback reads the page the classic request LANDED on and makes NO
  re-query, so a call still costs one search per place (ruling
  ``Q-FILTER-FIRES-SEARCH-CAP``: a filter-driven re-query would count as a
  search against ``D1-SEARCH-AS-READS``'s five a live session).

## THE AI ROUTE AS THE SEARCH'S OWN ROUTE (lane jobs7, 2026-11-27)

The classic search NO LONGER SERVES: live session 12's load 3 (``C-SRCH-1``,
the decision load, 2026-11-26) asked for ``/jobs/search/`` and was REDIRECTED
here, with no classic list, no deprecation banner and no classic anchor. So a
call whose every argument this route honours (:func:`asks_the_ai_route`)
ASKS FOR THIS ROUTE'S OWN ADDRESS (:func:`ai_search_url`, ``keywords`` and
nothing else) and is read here as the search's PRIMARY route, not as a
fallback behind a redirect. Measured on session 12's two AI loads, by keyed
shape on the live lane's own skeletons (``tests/fixtures/live12/
c_srch_1_words.html`` and ``c_srch_0b_words.html``): 25 and 18 cards, each
with the head stack below, the hiring chip on 5 and on 13, proximity on 3 and
on 3. A call that sets an argument this route has not been measured honouring
is REFUSED BEFORE ANY LOAD (:func:`retired_route_refusal`, ruling
``REFUSE-BEFORE-LOAD-ON-A-RETIRED-ROUTE``): zero loads and zero of D1's
searches, its refusal naming the arguments and the retired classic route.
That is the shipped default, :data:`CLASSIC_ROUTE_RETIRED` True. Only the
reopener -- a capture showing the classic route serving again, which sets the
constant False -- keeps such a call on its classic composition, where its
landing here refuses by name (:func:`fallback_refusal`) and a landing on the
classic page is read by the classic reader.

## THE AI READER, AND WHAT EACH FIELD IS BOUND TO

:func:`read_ai_search` reads the page's serialised HTML (``page.content()``,
one snapshot, so a page still settling cannot answer two questions
differently). Every field is bound by STRUCTURE -- an attribute LinkedIn wrote
for its own code, or an element-type relation -- never by a CSS class and
never by a line's position in the text. Measured on the one capture there is,
25 cards of 25 for every anchor (lane search-fix26 ``anchor_check.py``):

* a CARD is the OUTERMOST element keyed ``componentkey="job-card-component-ref-
  <id>"`` (50 keyed elements, 25 outermost: each card holds one inner copy);
* ``job_id`` is that key's digit run;
* the TITLE is the ``span[aria-hidden="true"]`` child of the paragraph inside
  the card's one ``[data-display-contents]`` element -- the VISIBLE copy. Its
  plain-span twin holds text on 5 cards of 25, and on 3 of those it is longer
  than the visible title (a suffix the visible copy does not draw);
* the HEAD STACK is that element's parent, and its children are, on 25 of 25,
  the title wrapper, ONE ``div`` holding one paragraph, and ONE paragraph. The
  ``div``'s paragraph is the COMPANY; the bare paragraph is the PLACE;
* ``easy_apply`` is a paragraph OUTSIDE the head stack whose whole text is
  ``Easy Apply`` (8 cards of 25);
* ``when`` is the ``aria-hidden`` twin of the one plain span reading
  ``Posted N <unit> ago`` (25 of 25; the plain copy equals "Posted " + the
  visible one on 25 of 25);
* ``proximity`` is the shipped ``shape.find_proximity`` over the card's lines
  outside the head stack: integers, never a page string;
* ``hiring`` is the hiring chips the card draws OUTSIDE the head stack, each
  a text whose WHOLE text is one of :data:`HIRING_CHIPS`'s closed words,
  returned as that table's literals (lane jobs7, census ``J 20``'s hiring
  status). Measured: session 11's raw page drew each word on 5 cards
  (search26 2.3); session 12's two loads drew ``Actively reviewing
  applicants`` on 5 and 11 cards and ``Be an early applicant`` on 0 and 3, one
  card drawing both. Omitted when none is drawn, as ``proximity`` is.

PAGE TELEMETRY, NEVER A COUNT: ``99+ results`` is read as ``{shown, capped}``
and the pager as the number of ``pagination-indicator-<n>`` test ids plus the
next control's own ``-visible`` / ``-hidden`` suffix. Neither is the number of
postings the search matched.

## WHAT EVERY STRING HERE IS

Every string this module EMITS outside a row's page fields (title, company,
location) is a literal declared below, an integer or a boolean. The rows carry
page text because a job search's product is page text -- the classic reader's
rows carry the same three fields. No refusal built here interpolates a page
string or an address.
"""

from __future__ import annotations

import re
from html.parser import HTMLParser
from typing import Any, Iterable, Optional
from urllib.parse import parse_qsl, urlencode, urlsplit

from linkedin_server.shape import find_proximity, trim

# ---------------------------------------------------------------------------
# 1. The landing
# ---------------------------------------------------------------------------

#: The three things a job-search load can land on. Closed, and every one is a
#: literal this module declares.
CLASSIC = "classic_search"
AI = "ai_search"
OTHER = "other_route"
ROUTES: tuple[str, ...] = (CLASSIC, AI, OTHER)

#: ``(route, first path segment, second path segment)``. Whole segments at
#: fixed positions, and the path must have exactly two -- ``/jobs/search/`` and
#: ``/jobs/search-results/`` are LinkedIn's spellings, measured (classic: the
#: 2026-09-20 raw captures and session 2's j107; AI: session 11's capture).
_ROUTE_SEGMENTS: tuple[tuple[str, str, str], ...] = (
    (CLASSIC, "jobs", "search"),
    (AI, "jobs", "search-results"),
)

#: The hosts this server navigates to; the same set ``landing.HOSTS`` holds.
_HOSTS: tuple[str, ...] = ("www.linkedin.com", "linkedin.com", "m.linkedin.com")


def landing_route(url: Any) -> str:
    """Classify a landed address as :data:`CLASSIC`, :data:`AI` or :data:`OTHER`.

    Returns a literal and nothing else. An address on another host, with any
    other path, or that cannot be parsed is :data:`OTHER` -- the refusing
    class, never a guess at the nearest route.
    """
    try:
        parts = urlsplit(url if isinstance(url, str) else "")
    except ValueError:
        return OTHER
    if (parts.netloc or "").lower() not in _HOSTS:
        return OTHER
    segments = [part for part in (parts.path or "").split("/") if part]
    if len(segments) != 2:
        return OTHER
    for route, first, second in _ROUTE_SEGMENTS:
        if segments[0] == first and segments[1] == second:
            return route
    return OTHER


def landed_query_matches(url: Any, keywords: str) -> bool:
    """Does the landed address carry the keywords the caller searched for?

    A BOOLEAN, compared and never returned: the fallback reads an AI page only
    when it is the search that was asked for. A landing with no ``keywords``
    key at all, or with different words, is not that search -- LinkedIn's AI
    route also serves recommendation and history views at the same path.
    Compared case- and whitespace-insensitively, because the search box is.
    """
    try:
        query = urlsplit(url if isinstance(url, str) else "").query
        pairs = parse_qsl(query, keep_blank_values=True)
    except ValueError:
        return False
    wanted = " ".join(str(keywords or "").split()).lower()
    if not wanted:
        return False
    landed = [" ".join(value.split()).lower() for key, value in pairs if key == "keywords"]
    return len(landed) == 1 and landed[0] == wanted


# ---------------------------------------------------------------------------
# 2. The fallback's argument policy (Q-SEARCH-ROUTE-POLICY)
# ---------------------------------------------------------------------------

#: THE ARGUMENTS THE AI ROUTE HONOURS. One, because one is measured: session
#: 11's capture is ``/jobs/search-results/?keywords=<generic role words>``,
#: SERVED exactly, 25 cards. ``limit`` is not here because it is not sent to
#: LinkedIn at all -- it trims the rows this process returns.
AI_ROUTE_HONOURED: tuple[str, ...] = ("keywords",)

#: ARGUMENTS APPLIED LOCALLY, NEVER SENT AS A FILTER (ruling
#: ``AI-EASY-APPLY-POST-FILTER``, the orchestrator's, 2026-11-26). One: each
#: AI card draws its own "Easy Apply" mark (8 of 25 on the one capture,
#: counted by two instruments), so ``easy_apply`` keeps the cards that draw it,
#: from the page already loaded, with no re-query and no press. The page's own
#: Easy Apply TOGGLE stays unmeasured: it is never pressed and never read as
#: applied. :func:`easy_apply_post_filter` is the one place this happens, and
#: its receipt says so in every result.
AI_ROUTE_LOCAL_FILTERS: dict[str, str] = {
    "easy_apply": "kept locally to the cards that draw their own Easy Apply mark; the page's Easy Apply toggle is unmeasured and never pressed",
}

#: The ``filter_mode`` every post-filter receipt carries, word for word.
LOCAL_POST_FILTER_MODE = "local_post_filter_on_card_mark"

#: EVERY OTHER ARGUMENT, with why it refuses on the AI route. Written from
#: search26's record (``2026-11-26-new-job-search.md`` sections 2.5 and 3.2):
#: LinkedIn's own 105 links into the AI route carry only ``f_TPR``, ``f_SAL``
#: and ``f_JIYN`` among the filters and address a place by ``geoId`` plus
#: ``distance``, never by a text ``location``; and no capture shows the route
#: honouring a filter the tool composed. A filter leaves this table only when
#: a fire shows it discriminating on the AI route, and that fire is its proof.
AI_ROUTE_UNMEASURED: dict[str, str] = {
    "location": "the AI route addresses a place by geoId and distance; a text location is unmeasured there",
    "locations": "a fan-out is one location per load, and a location is unmeasured on the AI route",
    "remote": "workplace type is a drawn pill on the AI route; its address spelling is unmeasured",
    "date_posted": "LinkedIn's own AI links spell it f_TPR, but no capture shows a composed f_TPR honoured",
    "experience_level": "experience level is a drawn pill on the AI route; its address spelling is unmeasured",
    "job_type": "employment type is a drawn pill on the AI route; its address spelling is unmeasured",
    "company_id": "no capture shows an employer-scoped search on the AI route",
    "under_ten_applicants": "no capture shows this filter on the AI route",
    "in_your_network": "the AI page draws an In my network toggle; its address spelling is unmeasured",
    "fair_chance_employer": "no capture shows this filter on the AI route",
    "sort_by": "no capture shows a sort order on the AI route",
    "start": "the AI pager is buttons with no address; how page two is addressed is unmeasured",
}


def ai_route_refusals(
    *,
    location: str = "",
    locations: str = "",
    remote: str = "any",
    date_posted: str = "any",
    experience_level: str = "",
    job_type: str = "",
    company_id: str = "",
    easy_apply: bool = False,
    under_ten_applicants: bool = False,
    in_your_network: bool = False,
    fair_chance_employer: bool = False,
    sort_by: str = "relevance",
    start: int = 0,
) -> list[str]:
    """The argument NAMES a call set that the AI route cannot honour, in table order.

    An argument at its default is not a filter and is never named. Returns
    names from :data:`AI_ROUTE_UNMEASURED`'s keys only -- the tool's
    own parameter names, never a value the caller passed. ``easy_apply`` is
    accepted and never named: it is a LOCAL filter on this route
    (:data:`AI_ROUTE_LOCAL_FILTERS`), not a refused one.
    """
    chosen = {
        "location": bool(str(location or "").strip()),
        "locations": bool(str(locations or "").strip()),
        "remote": str(remote or "").strip().lower() not in ("", "any"),
        "date_posted": str(date_posted or "").strip().lower() not in ("", "any"),
        "experience_level": bool(str(experience_level or "").strip()),
        "job_type": bool(str(job_type or "").strip()),
        "company_id": bool(str(company_id or "").strip()),
        "under_ten_applicants": bool(under_ten_applicants),
        "in_your_network": bool(in_your_network),
        "fair_chance_employer": bool(fair_chance_employer),
        "sort_by": str(sort_by or "").strip().lower() not in ("", "relevance"),
        "start": _as_int(start) > 0,
    }
    return [argument for argument in AI_ROUTE_UNMEASURED if chosen[argument]]


def _as_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


#: THE CLASSIC ROUTE IS MEASURED RETIRED: live session 12's load 3 (``C-SRCH-1``,
#: the decision load, 2026-11-26) asked for ``/jobs/search/`` and was redirected
#: here, with no classic list, no banner and no classic anchor
#: (RETIRED-ROUTE-ROWS-RETURN-ON-CAPTURE). So, by the orchestrator's ruling
#: REFUSE-BEFORE-LOAD-ON-A-RETIRED-ROUTE (2026-11-27), a call that sets an
#: argument this route refuses is refused BEFORE ANY LOAD
#: (:func:`retired_route_refusal`): zero loads, zero of D1's searches. The
#: classic composition stays for the REOPENER -- a capture showing the classic
#: route serving again sets this False -- and its tests run it that way.
CLASSIC_ROUTE_RETIRED: bool = True

#: THE AI ROUTE'S OWN ADDRESS, admitted since 2026-10-10 (``readonly``'s line
#: for ``/jobs/search-results/``, census ``J 16``) and the address session 12's
#: load 4 asked for and was SERVED exactly (``C-SRCH-0b``).
AI_SEARCH_URL = "https://www.linkedin.com/jobs/search-results/"


def asks_the_ai_route(refused: Iterable[str], *, keywords: Any) -> bool:
    """Whether a call ASKS FOR the AI route's own address (lane jobs7).

    Exactly when the call has keywords and sets no argument the AI route
    refuses (:func:`ai_route_refusals` named none): then every argument it
    sets is honoured there -- ``keywords`` on the address, ``easy_apply``
    locally, ``limit`` in this process -- and the classic address, which no
    longer serves (live session 12, load 3), would only redirect here. A call
    with any refused argument is refused BEFORE ANY LOAD by the shipped
    default (:data:`CLASSIC_ROUTE_RETIRED` True, :func:`retired_route_refusal`);
    only under the reopener (the constant set False) does it keep its classic
    composition and refuse by name on the landing.
    """
    return not list(refused or ()) and bool(" ".join(str(keywords or "").split()))


def ai_search_url(keywords: Any) -> str:
    """The AI route's own address for ONE keyword search: ``keywords`` and nothing else.

    The words are the caller's, whitespace-folded the way the search box folds
    them and urlencoded by the standard library. No filter, no place and no
    offset is ever written here: none is measured honoured on this route
    (:data:`AI_ROUTE_UNMEASURED`), and ``easy_apply`` is applied to the cards
    this page returns, never sent.
    """
    words = " ".join(str(keywords or "").split())
    return AI_SEARCH_URL + "?" + urlencode([("keywords", words)])


def easy_apply_post_filter(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Keep the AI rows whose card drew its own "Easy Apply" mark, and say so.

    LOCAL, and the receipt is part of the answer: ``filter_mode`` is
    :data:`LOCAL_POST_FILTER_MODE`, with the count ``before`` and ``after``.
    A row is kept only when its ``easy_apply`` is exactly ``True`` -- a row
    with no mark, or anything else in the field, is dropped, never guessed.
    This narrows the ONE window the load returned; it is not LinkedIn's Easy
    Apply filter, so postings outside that window are never considered.
    """
    kept = [row for row in rows if row.get("easy_apply") is True]
    return kept, {"filter_mode": LOCAL_POST_FILTER_MODE, "before": len(rows), "after": len(kept)}


# ---------------------------------------------------------------------------
# 3. The page, parsed once
# ---------------------------------------------------------------------------

_VOID = frozenset(
    {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
     "param", "source", "track", "wbr"}
)
#: Elements whose text a browser does not draw.
_UNDRAWN = frozenset({"script", "style", "template", "noscript"})


class _Node:
    __slots__ = ("tag", "attrs", "children", "parent")

    def __init__(self, tag: str, attrs: dict[str, Optional[str]], parent: Optional["_Node"]):
        self.tag = tag
        self.attrs = attrs
        self.children: list[Any] = []
        self.parent = parent


class _Tree(HTMLParser):
    """The document as nested nodes; text kept as ``str`` children."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = _Node("#root", {}, None)
        self._cur = self.root
        self._undrawn = 0

    def handle_starttag(self, tag, attrs):
        node = _Node(tag, dict(attrs), self._cur)
        self._cur.children.append(node)
        if tag in _UNDRAWN:
            self._undrawn += 1
        if tag not in _VOID:
            self._cur = node

    def handle_startendtag(self, tag, attrs):
        self._cur.children.append(_Node(tag, dict(attrs), self._cur))

    def handle_endtag(self, tag):
        walker = self._cur
        while walker is not None and walker.tag != tag:
            walker = walker.parent
        if walker is None or walker.parent is None:
            return
        if tag in _UNDRAWN:
            self._undrawn = max(0, self._undrawn - 1)
        self._cur = walker.parent

    def handle_data(self, data):
        if not self._undrawn and data.strip():
            self._cur.children.append(data)


def _parse(html: str) -> _Node:
    tree = _Tree()
    tree.feed(html if isinstance(html, str) else "")
    tree.close()
    return tree.root


def _walk(node: _Node) -> Iterable[_Node]:
    stack = [node]
    while stack:
        current = stack.pop()
        yield current
        stack.extend(
            child for child in reversed(current.children) if isinstance(child, _Node)
        )


def _elements(node: _Node) -> list[_Node]:
    return [child for child in node.children if isinstance(child, _Node)]


def _texts(node: _Node) -> list[str]:
    """Every drawn text under ``node``, one entry per text node, normalised."""
    out: list[str] = []
    stack: list[Any] = [node]
    while stack:
        current = stack.pop()
        if isinstance(current, str):
            out.append(" ".join(current.split()))
        else:
            stack.extend(reversed(current.children))
    return [text for text in out if text]


def _text(node: _Node) -> str:
    return " ".join(" ".join(_texts(node)).split())


def _inside(node: _Node, ancestor: _Node) -> bool:
    up = node.parent
    while up is not None:
        if up is ancestor:
            return True
        up = up.parent
    return False


def _hidden(node: _Node) -> bool:
    return (node.attrs.get("aria-hidden") or "").lower() == "true"


def _classes(node: _Node) -> list[str]:
    return str(node.attrs.get("class") or "").split()


# ---------------------------------------------------------------------------
# 4. The render evidence, read for a refusal and nowhere else
# ---------------------------------------------------------------------------

#: The AI page's screen id, LinkedIn's own code vocabulary (session 11: one
#: ``data-sdui-screen`` on the page, this value).
AI_SCREEN = "com.linkedin.sdui.flagshipnav.jobs.SemanticJobDetails"

#: The card key. The id is the digit run; a key of any other shape is not a card.
CARD_KEY = re.compile(r"^job-card-component-ref-(\d{6,})$")

#: The classic anchor, the same pattern as ``dom.JOB_HREF`` (copied rather
#: than imported so this module does not drag the page-reading machinery in;
#: ``tests/test_job_search_route.py`` holds the two equal).
JOB_VIEW_HREF = re.compile(r"/jobs/view/(?:[^/?#]*-)?(\d{6,})")

#: Two classic markers, used ONLY to describe a refused page, never to read a
#: field: the two-pane list LinkedIn's classic search draws its cards in, and
#: the deprecation banner it draws above them (search26 section 1.1).
CLASSIC_LIST_CLASS = "scaffold-layout__list"
CLASSIC_BANNER_CLASS = "jobs-search-cjs-deprecation-banner"

#: LINKEDIN'S OWN "NO RESULTS" WORDING, ONE PER ROUTE, AND BOTH ARE EMPTY ON
#: PURPOSE. No capture on this box shows either page with nothing found (the
#: 2026-09-20 raw captures, every live-lane skeleton and every tracked fixture
#: were searched on 2026-11-26), and a wording remembered rather than
#: measured is how a broken read gets believed. A zero is therefore refused on
#: both routes until a capture supplies the words (search26 gap G7; its spec
#: C-SRCH-3b's positive control can fetch the AI one).
CLASSIC_EMPTY_STATES: tuple[str, ...] = ()
AI_EMPTY_STATES: tuple[str, ...] = ()


def _screen_of(root: _Node) -> str:
    screens = [n.attrs.get("data-sdui-screen") for n in _walk(root) if "data-sdui-screen" in n.attrs]
    if not screens:
        return "none"
    if any(value == AI_SCREEN for value in screens):
        return "semantic_job_details"
    return "other_screen"


def _outer_cards(root: _Node) -> list[_Node]:
    keyed = [n for n in _walk(root) if CARD_KEY.match(n.attrs.get("componentkey") or "")]
    keyed_ids = {id(n) for n in keyed}
    out = []
    for node in keyed:
        up = node.parent
        nested = False
        while up is not None:
            if id(up) in keyed_ids:
                nested = True
                break
            up = up.parent
        if not nested:
            out.append(node)
    return out


def render_evidence(html: str, *, empty_states: Iterable[str] = ()) -> dict[str, Any]:
    """What the page drew, as integers, booleans and declared literals.

    Read ONLY on the branch that is about to refuse, the rule ``_read_tracker``
    follows for its own evidence: a read that succeeded has no use for it.
    ``empty_state`` is the matched entry of ``empty_states`` -- a string this
    package declared, never one the page supplied -- or ``None``.
    """
    root = _parse(html)
    wanted = tuple(empty_states or ())
    matched = None
    if wanted:
        for text in _texts(root):
            if text in wanted:
                matched = wanted[wanted.index(text)]
                break
    return {
        "html_read": bool(isinstance(html, str) and html.strip()),
        "sdui_screen": _screen_of(root),
        "ai_cards": len(_outer_cards(root)),
        "job_view_anchors": sum(
            1 for n in _walk(root)
            if n.tag == "a" and JOB_VIEW_HREF.search(n.attrs.get("href") or "")
        ),
        "classic_list": any(CLASSIC_LIST_CLASS in _classes(n) for n in _walk(root)),
        "deprecation_banner": any(CLASSIC_BANNER_CLASS in _classes(n) for n in _walk(root)),
        "empty_state": matched,
    }


def zero_is_believable(evidence: dict[str, Any]) -> bool:
    """A zero is an answer only when LinkedIn's own empty state was drawn."""
    return bool(evidence.get("empty_state"))


def empty_states_for(route: str) -> tuple[str, ...]:
    """The declared empty-state wording for a route. Empty for both today."""
    return AI_EMPTY_STATES if route == AI else CLASSIC_EMPTY_STATES


# ---------------------------------------------------------------------------
# 5. The AI reader
# ---------------------------------------------------------------------------

_AGO = re.compile(r"^\d+ (?:second|minute|hour|day|week|month|year)s? ago$")
_POSTED = re.compile(r"^(Posted|Reposted) (\d+ (?:second|minute|hour|day|week|month|year)s? ago)$")
_WORKPLACE = re.compile(r"\((Remote|Hybrid|On-site)\)")
_WORKPLACE_WORDS = {"Remote": "remote", "Hybrid": "hybrid", "On-site": "on_site"}
_TOTAL = re.compile(r"^(\d+)(\+?) results?$")
_PAGER_INDICATOR = re.compile(r"^pagination-indicator-\d+$")
EASY_APPLY_WORD = "Easy Apply"
#: The toolbar toggle's own accessible name (session 11: 2 drawn, both off).
EASY_APPLY_TOGGLE_LABEL = "Filter by Easy Apply"

#: THE HIRING CHIPS AN AI CARD DRAWS, LinkedIn's own words -> this package's
#: literals, closed and in output order (lane jobs7, census ``J 20``). Each
#: word MEASURED: on session 11's raw page by string equality (search26 2.3,
#: 5 cards each) and on session 12's two keyed skeletons by keyed shape
#: (``Actively reviewing applicants`` 5 and 11 cards, ``Be an early
#: applicant`` 0 and 3). A chip word outside this table is never read: it is
#: absent, not guessed.
HIRING_CHIPS: dict[str, str] = {
    "Actively reviewing applicants": "actively_reviewing_applicants",
    "Be an early applicant": "be_an_early_applicant",
}


def _card_hiring(card: _Node, stack: _Node) -> list[str]:
    """The card's hiring chips, as :data:`HIRING_CHIPS` literals, in table order.

    A chip is a drawn text OUTSIDE the head stack whose whole text is one of
    the table's words -- on session 12 a ``p > span`` (the first) or a ``p``
    (the second), so the text is matched and its wrapper is not. Each literal
    once, however many copies the card draws.
    """
    found: set[str] = set()
    for node in _walk(card):
        if node is stack or _inside(node, stack):
            continue
        for child in node.children:
            if isinstance(child, str):
                literal = HIRING_CHIPS.get(" ".join(child.split()))
                if literal:
                    found.add(literal)
    return [literal for literal in HIRING_CHIPS.values() if literal in found]


def _one(nodes: list[_Node]) -> Optional[_Node]:
    return nodes[0] if len(nodes) == 1 else None


def _card_title(display: _Node) -> Optional[str]:
    paragraphs = [n for n in _walk(display) if n.tag == "p"]
    paragraph = _one(paragraphs)
    if paragraph is None:
        return None
    visible = _one([k for k in _elements(paragraph) if k.tag == "span" and _hidden(k)])
    if visible is None:
        return None
    return _text(visible) or None


def _workplace(place: Optional[str]) -> Optional[str]:
    if not place:
        return None
    found = {_WORKPLACE_WORDS[m.group(1)] for m in _WORKPLACE.finditer(place)}
    return found.pop() if len(found) == 1 else None


def _card_when(card: _Node, stack: _Node) -> tuple[Optional[str], bool]:
    posted = []
    for node in _walk(card):
        if node.tag != "span" or _hidden(node) or _inside(node, stack):
            continue
        match = _POSTED.match(_text(node))
        if match:
            posted.append((node, match))
    if len(posted) != 1:
        return None, False
    node, match = posted[0]
    twins = [k for k in _elements(node.parent) if k.tag == "span" and _hidden(k)] if node.parent else []
    twin = _one(twins)
    visible = _text(twin) if twin is not None else ""
    if not _AGO.match(visible) or visible != match.group(2):
        return None, False
    return visible, match.group(1) == "Reposted"


def _read_ai_card(card: _Node) -> Optional[dict[str, Any]]:
    key = CARD_KEY.match(card.attrs.get("componentkey") or "")
    if key is None:
        return None
    display = _one([n for n in _walk(card) if "data-display-contents" in n.attrs])
    if display is None or display.parent is None:
        return None
    title = _card_title(display)
    if not title:
        return None
    stack = display.parent
    company_box = _one([k for k in _elements(stack) if k.tag == "div" and k is not display])
    company_p = (
        _one([n for n in _walk(company_box) if n.tag == "p"]) if company_box is not None else None
    )
    place_p = _one([k for k in _elements(stack) if k.tag == "p"])
    company = _text(company_p) if company_p is not None else None
    place = _text(place_p) if place_p is not None else None

    outside = [n for n in _walk(card) if not _inside(n, stack) and n is not stack]
    easy_apply = any(n.tag == "p" and _text(n) == EASY_APPLY_WORD for n in outside)
    when, reposted = _card_when(card, stack)

    lines: list[str] = []
    for node in outside:
        lines.extend(child for child in node.children if isinstance(child, str))
    proximity = find_proximity(" ".join(line.split()) for line in lines)

    job_id = key.group(1)
    row: dict[str, Any] = {
        "title": trim(title, 120),
        "company": trim(company, 100),
        "location": trim(place, 100),
        "job_id": job_id,
        "url": f"https://www.linkedin.com/jobs/view/{job_id}",
        "easy_apply": easy_apply,
    }
    workplace = _workplace(place)
    if workplace:
        row["workplace"] = workplace
    if when:
        row["when"] = when
        if reposted:
            row["reposted"] = True
    if proximity.get("state"):
        # OMITTED WHEN NOT DRAWN, exactly as ``shape._job_card_out`` omits it.
        row["proximity"] = proximity
    hiring = _card_hiring(card, stack)
    if hiring:
        # OMITTED WHEN NOT DRAWN, as ``proximity`` is: absent means no chip
        # this package knows was drawn, never "not hiring".
        row["hiring"] = hiring
    return row


def _total(root: _Node) -> Optional[dict[str, Any]]:
    found = []
    for text in _texts(root):
        match = _TOTAL.match(text)
        if match:
            found.append((int(match.group(1)), bool(match.group(2))))
    if len(set(found)) != 1:
        return None
    shown, capped = found[0]
    return {"shown": shown, "capped": capped}


def _pager(root: _Node) -> dict[str, Any]:
    ids = [n.attrs.get("data-testid") or "" for n in _walk(root) if "data-testid" in n.attrs]
    nxt = None
    if "pagination-controls-next-button-visible" in ids:
        nxt = "visible"
    elif "pagination-controls-next-button-hidden" in ids:
        nxt = "hidden"
    return {
        "indicators": sum(1 for value in ids if _PAGER_INDICATOR.match(value)),
        "next_control": nxt,
    }


def _easy_apply_toggle(root: _Node) -> dict[str, Any]:
    toggles = [
        n for n in _walk(root)
        if n.tag == "input" and (n.attrs.get("aria-label") or "") == EASY_APPLY_TOGGLE_LABEL
    ]
    return {
        "drawn": bool(toggles),
        "checked": any("checked" in n.attrs for n in toggles) if toggles else None,
    }


def read_ai_search(html: str) -> dict[str, Any]:
    """Read the AI job search off its serialised HTML.

    Returns ``rows`` (one per card that offered an id and a title),
    ``unparsed`` (cards that did not), and the page's telemetry: ``total``
    (``{"shown", "capped"}`` or ``None``), ``pager``, ``easy_apply_toggle`` and
    the render evidence's ``sdui_screen``. Pure: no browser, no network.
    """
    root = _parse(html)
    cards = _outer_cards(root)
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    unparsed = 0
    for card in cards:
        row = _read_ai_card(card)
        if row is None:
            unparsed += 1
            continue
        if row["job_id"] in seen:
            continue
        seen.add(row["job_id"])
        rows.append(row)
    return {
        "html_read": bool(isinstance(html, str) and html.strip()),
        "rows": rows,
        "cards": len(cards),
        "unparsed": unparsed,
        "total": _total(root),
        "pager": _pager(root),
        "easy_apply_toggle": _easy_apply_toggle(root),
        "sdui_screen": _screen_of(root),
    }


# ---------------------------------------------------------------------------
# 6. The refusals. Literals, integers and declared names only.
# ---------------------------------------------------------------------------


def describe_evidence(evidence: dict[str, Any]) -> str:
    """One line from :func:`render_evidence`'s fields. Nothing else enters it."""
    if not evidence.get("html_read"):
        return "the page's markup could not be read"
    return (
        "the page drew {cards} AI result card(s), {anchors} classic job link(s), "
        "classic list {lst}, deprecation banner {banner}, SDUI screen {screen}, "
        "and no empty state this package recognises"
    ).format(
        cards=int(evidence.get("ai_cards") or 0),
        anchors=int(evidence.get("job_view_anchors") or 0),
        lst="drawn" if evidence.get("classic_list") else "not drawn",
        banner="drawn" if evidence.get("deprecation_banner") else "not drawn",
        screen=evidence.get("sdui_screen") if evidence.get("sdui_screen") in (
            "none", "semantic_job_details", "other_screen") else "unread",
    )


def zero_refusal(route: str, evidence: dict[str, Any], *, records: int = 0, dropped: int = 0) -> str:
    """The render veto's message: no card, and no empty state to believe."""
    where = "classic job search" if route == CLASSIC else "AI job search"
    return (
        f"the {where} page held no job card this reader could read "
        f"({int(records)} card record(s) harvested, {int(dropped)} unparsed), and "
        f"{describe_evidence(evidence)}. LinkedIn's own no-results wording has "
        "never been captured for this page, so an empty result cannot be told "
        "apart from a broken read, and it is reported as a failure instead of "
        "as an empty shortlist. If the offset is past the end of the results, "
        "that is the expected cause."
    )


def landing_refusal(shape: str) -> str:
    """The landing veto's message. ``shape`` is ``landing.withheld`` of the landing."""
    return (
        "the job search did not land on LinkedIn's classic job search or its AI "
        "job search, so neither reader is aimed at the page it got. The landing, "
        f"described without its address: {shape}."
    )


def fallback_refusal(refused: list[str], toggle: dict[str, Any], *, html_read: bool = True) -> str:
    """The fallback's message: the AI route served, and these arguments are unmeasured there."""
    refusing = [argument for argument in refused if argument in AI_ROUTE_UNMEASURED]
    grounds = "; ".join(
        f"{argument}: {why}"
        for argument, why in AI_ROUTE_UNMEASURED.items()
        if argument in refusing
    )
    if not html_read:
        drawn = "unread (the page's markup could not be read)"
    else:
        drawn = "drawn" if toggle.get("drawn") else "not drawn"
    return (
        "LinkedIn served its AI job search in place of the classic one, and the "
        "AI route is the fallback: it honours "
        + ", ".join(AI_ROUTE_HONOURED)
        + " only, and refuses every filter not yet measured on it rather than "
        "return a shortlist that was never filtered. Refused: "
        + ", ".join(refusing)
        + f" ({grounds}). The page's Easy Apply toggle is {drawn}. "
        "Call again without the refused arguments for a keyword search; "
        "easy_apply is applied there locally, to each card's own mark."
    )


def retired_route_refusal(refused: list[str]) -> str:
    """The pre-load refusal (REFUSE-BEFORE-LOAD-ON-A-RETIRED-ROUTE): names only.

    Every name is a key of :data:`AI_ROUTE_UNMEASURED` -- the tool's own
    parameter names -- with its ground; no value the caller passed is repeated.
    """
    refusing = [argument for argument in refused if argument in AI_ROUTE_UNMEASURED]
    grounds = "; ".join(
        f"{argument}: {why}"
        for argument, why in AI_ROUTE_UNMEASURED.items()
        if argument in refusing
    )
    return (
        "LinkedIn's classic job search is retired (a capture on 2026-11-26 found "
        "its address redirected to the AI job search), and the AI job search "
        "honours " + ", ".join(AI_ROUTE_HONOURED) + " only, so this call is "
        "refused before any page loads rather than spend a load and a search to "
        "refuse after one. Refused: " + ", ".join(refusing) + f" ({grounds}). "
        "Call again without the refused arguments for a keyword search; "
        "easy_apply is applied there locally, to each card's own mark. Nothing "
        "was loaded."
    )


def classic_at_ai_refusal() -> str:
    """The message when an AI-routed ``easy_apply`` call is answered with the classic page.

    Lane jobs7: such a call asks for the AI address with no filter on it,
    because ``easy_apply`` is applied there to each card's own mark. A classic
    page served in its place was asked for no filter, so its rows are not Easy
    Apply postings -- the accepted-and-ignored filter this module exists to
    refuse.
    """
    return (
        "LinkedIn served its classic job search at the AI search's own address, "
        "and this call's easy_apply was to be applied to the AI page's own card "
        "marks: the classic page was asked for no filter, so its rows are not "
        "Easy Apply postings and are not returned. Call again without "
        "easy_apply for the classic page's rows."
    )


def query_refusal() -> str:
    """The fallback's message when the AI page served is not the search asked for."""
    return (
        "LinkedIn served its AI job search in place of the classic one, but the "
        "address it landed on does not carry the keywords this call searched "
        "for, so its cards are not this search's results and are not returned."
    )
