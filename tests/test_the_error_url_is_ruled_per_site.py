"""``ExtractionFailedError.url`` HAD A CONTRACT AND NO RULING. TWENTY SITES FED IT.

``server._error`` builds the failure envelope every tool in this package
returns::

    out = {"error": exc.kind, "message": scrub(str(exc))}
    url = getattr(exc, "url", "")
    if url:
        out["url"] = url                 # <-- NO SCRUBBER. Not at all.
    hint = getattr(exc, "hint", "")
    if hint:
        out["hint"] = scrub(hint)

Scrubbing it would achieve nothing anyway -- ``scrub`` substitutes this
server's own filesystem paths and a name has no shape to scrub -- so "not
scrubbed" was never the defect. **The defect is that twenty sites fed that
field and nobody had decided, per site, whether the value may be published.**

The measurement is ``_audit/2026-09-21-the-landed-url.md`` section 6.1: all
twelve ``dom.py`` sites were driven to their own raise and all twelve published
a planted ``/in/<slug>/`` verbatim at ``$.url``. The ruling is
``_audit/2026-09-21-the-field-beside-the-message.md``. This file is the
ruling's executable half.

## THE SPLIT, AND WHY IT IS NOT A COMPROMISE

One question, asked at each of the twenty: **at the moment of this raise, does
an address THIS SERVER COMPOSED exist in scope?**

``server.py``   YES, at all seven. Each raise sits inside a tool that built its
                own url out of ``BASE_URL`` plus nothing, a closed stage token,
                or digits already proven numeric. Publishing THAT honours the
                field's declared contract exactly -- *"the operator can open
                the same page by hand"* -- and opening the requested address
                travels the same redirect the server travelled. Ruled
                :data:`ASKED_FOR`.

``dom.py``      NO, at any of the twelve. They are library readers holding a
                ``page`` and nothing else. Ruled :data:`WITHHELD`: no ``url``
                is passed at all, and the landing is DESCRIBED in the hint
                through ``dom._landing_note`` -> ``landing.withheld``, whose
                output is literals, integers and booleans.

``require_rows`` is the RELAY and is pinned as one, the way
``tests/test_the_source_url_split_was_never_ruled.py`` pins ``shape.envelope``:
it writes its own ``url`` parameter into the exception verbatim, so the verdict
belongs entirely to its callers and NEVER to the call.

## WHY WITHHOLDING ALL TWENTY WOULD HAVE BEEN THE WRONG ANSWER

``tests/test_the_source_url_split_was_never_ruled.py`` rules on the SUCCESS-PATH
TWIN of this value -- ``source_url``, in several of the same functions -- and it
forbids exactly that::

    Wrapping a deliberate publication is as much a defect as leaking an
    accidental one: it silently breaks a tool's contract, and the next reader
    cannot tell which shapers were reasoned and which were reflexive.

So this file fails in BOTH directions, as that one does. A ``WITHHELD`` site
that starts passing a url again is red. An ``ASKED_FOR`` site whose url becomes
navigation-derived is red. An ``ASKED_FOR`` site wrapped in a describer is ALSO
red -- a descriptor in a field documented as an openable address is a type lie,
and a reflexive wrap is what this file exists to refuse.

## WHAT IS DELIBERATELY NOT COVERED, SAID HERE RATHER THAN DISCOVERED

* **This is a SOURCE-TEXT rule over expression names and shapes.** It reads
  names, not values. A landing bound to a name this walk does not recognise as
  navigation-derived is invisible to it; :func:`_navigation_derived_names` says
  exactly which four forms it does recognise.
* **It does not rule on ``$.message``.** Every ``dom.py`` reader interpolates
  ``{exc}`` -- the BROWSER's own exception text -- into its message, and a
  needle planted there was measured arriving at ``$.message`` in all twelve
  drives. That is a third party composing the string and it is a different
  decision with a different remedy. Section 4 of the audit.
* **It does not rule on ``$.hint`` as a CHANNEL.** It requires the twelve
  ``WITHHELD`` sites to put a DESCRIBER there, and it says nothing about the
  two hints in ``server.py`` that carry page text on purpose.
* **:data:`FEEDERS` and :data:`DESCRIBERS` are BY-NAME sets**, the same shape of
  trust ``SHAPERS`` extends in the sibling file. A second relay written under a
  different name would not be enumerated. Both sets are asserted to name
  functions that exist, which catches a typo and a dead entry and does not
  pretend to check a contract.
"""
from __future__ import annotations

import ast
import functools
import pathlib

import pytest

from linkedin_server import dom, server
from linkedin_server.errors import ExtractionFailedError

REPO = pathlib.Path(__file__).resolve().parent.parent
SCANNED = REPO / "linkedin_server"

#: The keyword this file rules on, on the calls that feed it.
FIELD = "url"

#: Calls that put a value into ``ExtractionFailedError.url``. The class itself,
#: plus every declared RELAY that forwards a ``url`` into it. ``require_rows``
#: is the only relay today and :data:`DECLARED` rules it ``PASSTHROUGH``.
FEEDERS = frozenset({"ExtractionFailedError", "require_rows"})

#: Functions that turn a landing into literals. ``landing.withheld`` is the
#: package's one importable home for that and ``dom._landing_note`` is its
#: single dom-side caller; ``describe_landing`` and ``render`` are the two
#: halves ``withheld`` is composed of, admitted so a caller that wants the
#: dict rather than the line is not forced to lie about what it did.
DESCRIBERS = frozenset(
    {"withheld", "describe_landing", "render", "_landing_note"}
)

ASKED_FOR = "ASKED_FOR"
WITHHELD = "WITHHELD"
PASSTHROUGH = "PASSTHROUGH"
#: A feeder that could not publish an address if it wanted to: a pure string
#: builder taking neither a page nor a url. **DECLARED RATHER THAN IGNORED**,
#: because the guard's subject is every site that COULD feed the field and not
#: only the ones that do -- a `url=` keyword added to one of these tomorrow
#: arrives undeclared and goes red. They are NOT part of the twenty; the audit
#: says so where it counts them.
NO_ADDRESS_IN_SCOPE = "NO_ADDRESS_IN_SCOPE"

#: **THE DECLARATION.** ``(file, enclosing function) -> (verdict, how many)``.
#:
#: The COUNT is part of it, for the reason the sibling file states: a NEW
#: feeder added to a function that already has one must fail here rather than
#: inherit its neighbour's ruling.
DECLARED: dict[tuple[str, str], tuple[str, int]] = {
    # --- the relay, pinned ------------------------------------------------
    # Writes its own ``url`` parameter into the exception verbatim. Treating
    # it as anything else would rule its two callers on the strength of the
    # function they call rather than the value they hand it.
    ("dom.py", "require_rows"): (PASSTHROUGH, 1),
    # --- WITHHELD: the twelve page readers --------------------------------
    # Every one of these is `try: await page.evaluate(<script>) except
    # Exception: raise ...`. The url they used to publish was `page.url` read
    # INSIDE that except block, and the production raising class is
    # Playwright's "execution context destroyed by a navigation mid-evaluate"
    # -- on which path `page.url` is the address of the page that REPLACED the
    # one being read. So the old value was a string LinkedIn chose AND the
    # wrong page. There is no address in scope that this server composed,
    # because a dom reader is handed a page and never a url.
    ("dom.py", "harvest_linked_cards"): (WITHHELD, 1),
    ("dom.py", "harvest_block_cards"): (WITHHELD, 1),
    ("dom.py", "read_profile_fields"): (WITHHELD, 1),
    ("dom.py", "read_surface_census"): (WITHHELD, 1),
    ("dom.py", "read_self_owned_editor_fields"): (WITHHELD, 1),
    ("dom.py", "read_self_owned_editor_values"): (WITHHELD, 1),
    ("dom.py", "read_own_activity_items"): (WITHHELD, 1),
    ("dom.py", "read_compose_modes"): (WITHHELD, 1),
    ("dom.py", "read_selected_recipients"): (WITHHELD, 1),
    ("dom.py", "read_job_insight_panels"): (WITHHELD, 1),
    ("dom.py", "read_profile_views_insights"): (WITHHELD, 1),
    ("dom.py", "read_search_appearances"): (WITHHELD, 1),
    # --- ASKED_FOR: the seven tool-side raises ----------------------------
    # `url` is this helper's own parameter, composed by its caller
    # (`linkedin_search_jobs._search_url`) out of BASE_URL and urlencode.
    # `test_navigation_is_never_derived` is the standing proof that no
    # navigation target in this package is page-derived.
    ("server.py", "_read_cards"): (ASKED_FOR, 1),
    # f"{BASE_URL}/jobs-tracker/?stage={stage}" -- this package's template.
    ("server.py", "_read_tracker"): (ASKED_FOR, 1),
    # The last of two module constants. THE ONE SURFACE WHOSE OWN DOCSTRING
    # RECORDS THE REDIRECT: "/me/profile-views/ now redirects to that same
    # page", so requested and landed are documented to differ here.
    ("server.py", "linkedin_who_viewed_me"): (ASKED_FOR, 1),
    # f"{BASE_URL}/jobs/view/{digits}", digits already proven numeric. The
    # landing baseline rules this same provenance SERVER_CONSTRUCTED for this
    # function's MESSAGE, one field over.
    ("server.py", "linkedin_job_detail"): (ASKED_FOR, 1),
    # f"{BASE_URL}/mynetwork/network-manager/company/" -- a pure constant.
    ("server.py", "linkedin_followed_companies"): (ASKED_FOR, 1),
    # f"{BASE_URL}/notifications/" -- a pure constant.
    ("server.py", "linkedin_notifications"): (ASKED_FOR, 1),
    # f"{BASE_URL}/in/me/". **THE SHARPEST OF THE SEVEN.** What it LANDS on is
    # /in/<vanity>/, and a vanity slug is a name; the shipped
    # `test_a_profile_page_with_no_readable_name_is_a_failure` drove exactly
    # that redirect and asserted the resolved slug reached `$.url`. It passed
    # for as long as the leak existed. It is inverted now.
    ("server.py", "linkedin_my_profile"): (ASKED_FOR, 1),
    # --- NO_ADDRESS_IN_SCOPE: selector builders ---------------------------
    # Pure string builders. None takes a page or a url, so none of them could
    # publish an address if it tried. Declared so the guard's coverage is the
    # whole feeder population rather than the leaking subset.
    ("dom.py", "named_role_selector"): (NO_ADDRESS_IN_SCOPE, 2),
    ("dom.py", "settings_radio_label_selector"): (NO_ADDRESS_IN_SCOPE, 1),
    ("dom.py", "save_control_selector"): (NO_ADDRESS_IN_SCOPE, 1),
    ("dom.py", "follow_control_selector"): (NO_ADDRESS_IN_SCOPE, 1),
    ("dom.py", "unfollow_control_selector"): (NO_ADDRESS_IN_SCOPE, 1),
    ("dom.py", "post_submit_selector"): (NO_ADDRESS_IN_SCOPE, 1),
    ("dom.py", "compose_recipient_selector"): (NO_ADDRESS_IN_SCOPE, 1),
    ("dom.py", "compose_send_selector"): (NO_ADDRESS_IN_SCOPE, 1),
    ("dom.py", "comment_submit_selector"): (NO_ADDRESS_IN_SCOPE, 1),
    ("dom.py", "escaped_needle"): (NO_ADDRESS_IN_SCOPE, 1),
    ("dom.py", "_typeahead_selector_named"): (NO_ADDRESS_IN_SCOPE, 1),
}


# ---------------------------------------------------------------------------
# The walk
# ---------------------------------------------------------------------------


def _callee(node: ast.Call) -> str:
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return ""


def _reads_a_landing(expr: ast.AST, derived: set[str]) -> bool:
    """FOUR FORMS, and they are the whole of what this walk recognises.

    ``x.goto(...)``    the navigator; its return value IS ``page.url``
    ``_url_of(...)``   ``dom``'s own reader of the same thing
    ``<name>.url``     the live attribute
    a name already known derived, so one hop of propagation is followed

    Everything else is NOT navigation-derived as far as this file is
    concerned, and that limit is stated in the module docstring rather than
    left for somebody to find.
    """
    for node in ast.walk(expr):
        if isinstance(node, ast.Call) and _callee(node) in ("goto", "_url_of"):
            return True
        if isinstance(node, ast.Attribute) and node.attr == "url":
            return True
        if isinstance(node, ast.Name) and node.id in derived:
            return True
    return False


def _navigation_derived_names(func: ast.AST) -> set[str]:
    """Names inside one function bound to a landing, to a fixed point.

    **THE LOOP TARGET IS A BINDING TOO.** ``for u in <something landing-ish>``
    binds ``u`` exactly as an assignment does, and this repository has already
    paid once for a binding engine that did not know that -- the note in
    ``scripts/_bindings`` records *"ITERATION IS A BINDING, AND THIS ENGINE DID
    NOT KNOW THAT UNTIL 2026-09-20"*. So ``ast.For`` targets are walked here on
    the first attempt rather than after an incident.
    """
    derived: set[str] = set()
    changed = True
    while changed:
        changed = False
        for node in ast.walk(func):
            if isinstance(node, ast.Assign):
                targets, value = node.targets, node.value
            elif isinstance(node, ast.AnnAssign) and node.value is not None:
                targets, value = [node.target], node.value
            elif isinstance(node, (ast.For, ast.AsyncFor)):
                targets, value = [node.target], node.iter
            else:
                continue
            names: list[str] = []
            for target in targets:
                names.extend(
                    child.id
                    for child in ast.walk(target)
                    if isinstance(child, ast.Name)
                )
            if not names or not _reads_a_landing(value, derived):
                continue
            for name in names:
                if name not in derived:
                    derived.add(name)
                    changed = True
    return derived


def _parameters(func: ast.AST) -> set[str]:
    args = getattr(func, "args", None)
    if args is None:
        return set()
    every = list(args.posonlyargs) + list(args.args) + list(args.kwonlyargs)
    if args.vararg:
        every.append(args.vararg)
    if args.kwarg:
        every.append(args.kwarg)
    return {arg.arg for arg in every}


def feeder_sites(source: str, filename: str) -> list[dict]:
    """Every call in ``source`` that can put a value into the field.

    Returns one dict per site. Takes SOURCE rather than a path so a control can
    hand it a planted module -- the property that lets the sibling file's
    controls exist, copied deliberately.
    """
    tree = ast.parse(source, filename=filename)

    owner: dict[int, ast.AST] = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for inner in ast.walk(node):
                # INNERMOST WINS: several of these sit in nested helpers and
                # the outer name would misattribute them. ast.walk is
                # breadth-first from the top, so a later (deeper) function
                # legitimately overwrites an earlier one.
                owner[id(inner)] = node

    out: list[dict] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or _callee(node) not in FEEDERS:
            continue
        holder = owner.get(id(node))
        derived = _navigation_derived_names(holder) if holder is not None else set()
        params = _parameters(holder) if holder is not None else set()
        kwargs = {kw.arg: kw.value for kw in node.keywords if kw.arg}
        url = kwargs.get(FIELD)
        hint = kwargs.get("hint")
        out.append(
            {
                "file": filename,
                "function": getattr(holder, "name", "<module>"),
                "line": node.lineno,
                "has_url": url is not None,
                "url_expr": ast.unparse(url) if url is not None else None,
                "url_is_derived": bool(url is not None and _reads_a_landing(url, derived)),
                "url_is_parameter": bool(
                    isinstance(url, ast.Name) and url.id in params
                ),
                "url_describes": bool(
                    url is not None
                    and any(
                        isinstance(child, ast.Call) and _callee(child) in DESCRIBERS
                        for child in ast.walk(url)
                    )
                ),
                "hint_describes": bool(
                    hint is not None
                    and any(
                        isinstance(child, ast.Call) and _callee(child) in DESCRIBERS
                        for child in ast.walk(hint)
                    )
                ),
                "takes_a_page": "page" in params,
                "derives_a_landing": bool(derived),
            }
        )
    return out


@functools.lru_cache(maxsize=1)
def _all_sites() -> tuple[dict, ...]:
    """Every feeder site in the scanned package. ONCE PER PROCESS.

    The cache is a latency fix and changes nothing about what is checked, which
    is the only reason a guard may have one -- the sibling file's words, and
    its receipt: it paid its corpus walk fourteen times before noticing.
    SAFE BECAUSE THE CORPUS DOES NOT MOVE DURING A RUN: nothing in this suite
    writes to ``linkedin_server/``.
    """
    out: list[dict] = []
    for path in sorted(SCANNED.glob("*.py")):
        out.extend(feeder_sites(path.read_text(encoding="utf-8"), path.name))
    return tuple(out)


# ---------------------------------------------------------------------------
# The declaration
# ---------------------------------------------------------------------------


def test_every_feeder_site_is_declared():
    """A NEW ONE ARRIVES UNDECLARED AND FAILS. That is the whole mechanism."""
    seen: dict[tuple[str, str], int] = {}
    for site in _all_sites():
        key = (site["file"], site["function"])
        seen[key] = seen.get(key, 0) + 1

    undeclared = sorted(set(seen) - set(DECLARED))
    assert not undeclared, (
        "these can feed ExtractionFailedError.%s and are not declared: %s. "
        "Decide which it is -- ASKED_FOR (the address this server REQUESTED, "
        "composed by this package), WITHHELD (no url is published and the "
        "landing is described in the hint), PASSTHROUGH (a relay; the verdict "
        "belongs to its callers) or NO_ADDRESS_IN_SCOPE (nothing to publish) "
        "-- and say why. Do NOT wrap it reflexively: a descriptor in a field "
        "documented as an openable address is a type lie, and wrapping a "
        "deliberate publication breaks a contract silently."
        % (FIELD, undeclared)
    )

    gone = sorted(set(DECLARED) - set(seen))
    assert not gone, (
        "these are declared and no longer feed the field: %s. A declaration "
        "for a site that is gone is a comment pretending to be a check -- "
        "delete it." % gone
    )

    wrong_count = {
        key: (seen[key], DECLARED[key][1])
        for key in seen
        if key in DECLARED and seen[key] != DECLARED[key][1]
    }
    assert not wrong_count, (
        "the number of feeder sites changed in these functions (found, "
        "declared): %s. A new site in a function that already has one does "
        "not inherit its neighbour's ruling." % wrong_count
    )


def verdict_violations(key: tuple[str, str], sites: list[dict]) -> list[str]:
    """Every way ``sites`` break the verdict declared for ``key``.

    **A FUNCTION RATHER THAN A BODY OF ASSERTIONS, SO THE CONTROL THAT SHOWS
    THIS GUARD FAILING RUNS THE SAME CODE.**
    ``scripts/_check_the_error_url_ruling_can_fail.py`` plants the spelling
    that actually shipped and requires every row to be convicted; if it
    re-implemented these rules they would drift, and the drift would be
    invisible in exactly the direction that matters.
    """
    verdict, _count = DECLARED[key]
    where = "%s::%s" % key
    out: list[str] = []

    if not sites:
        return ["%s: no feeder site found" % where]

    if verdict == WITHHELD:
        leaking = [s["url_expr"] for s in sites if s["has_url"]]
        if leaking:
            out.append(
                "%s is declared WITHHELD and now passes %s=%r into the error. "
                "server._error publishes that field with NO scrubber. If the "
                "value is an address this server COMPOSED, move the row to "
                "ASKED_FOR and say so; if it is a landing, it may not be "
                "published." % (where, FIELD, leaking)
            )
        if any(not s["hint_describes"] for s in sites):
            out.append(
                "%s is declared WITHHELD and no longer describes the landing "
                "in its hint. Withholding is not deleting: the operator still "
                "needs to know WHICH KIND of page this failed on, and "
                "dom._landing_note -> landing.withheld says that in literals. "
                "An absence assertion on its own passes on a refusal that "
                "says nothing." % where
            )
    elif verdict == ASKED_FOR:
        if any(not s["has_url"] for s in sites):
            out.append(
                "%s is declared ASKED_FOR and now publishes no url at all. "
                "That field is this tool's reproduction instruction -- 'the "
                "operator can open the same page by hand'. If it was withheld "
                "on purpose, move the row and say why." % where
            )
        derived = [s["url_expr"] for s in sites if s["url_is_derived"]]
        if derived:
            out.append(
                "%s is declared ASKED_FOR and its url is navigation-derived "
                "again: %r. BROWSER.goto returns page.url, so that value is a "
                "string LinkedIn chose, and server._error publishes it "
                "unscrubbed. Publish the address this tool REQUESTED instead."
                % (where, derived)
            )
        wrapped = [s["url_expr"] for s in sites if s["url_describes"]]
        if wrapped:
            out.append(
                "%s is declared ASKED_FOR and its url now goes through a "
                "describer: %r. THIS IS THE REFLEXIVE WRAP AND IT IS A DEFECT: "
                "the field is documented as an address the operator can OPEN, "
                "a descriptor sentence there is a type lie, and the value is "
                "one this package composed and may publish." % (where, wrapped)
            )
    elif verdict == PASSTHROUGH:
        for site in sites:
            if not site["has_url"]:
                out.append("%s is a relay with no url" % where)
            elif not site["url_is_parameter"]:
                out.append(
                    "%s is declared PASSTHROUGH and its url is no longer its "
                    "own parameter (%r). A relay that shapes, or that reads a "
                    "landing of its own, rules every caller on the strength "
                    "of the function they call rather than the value they "
                    "hand it." % (where, site["url_expr"])
                )
            if site["url_is_derived"]:
                out.append("%s is declared PASSTHROUGH and derives a landing" % where)
    else:
        assert verdict == NO_ADDRESS_IN_SCOPE, verdict
        for site in sites:
            if site["has_url"]:
                out.append(
                    "%s is declared NO_ADDRESS_IN_SCOPE and now passes a url: "
                    "%r" % (where, site["url_expr"])
                )
            if site["takes_a_page"] or site["derives_a_landing"]:
                out.append(
                    "%s is declared NO_ADDRESS_IN_SCOPE and now has one in "
                    "scope. That is not automatically a leak, but it is no "
                    "longer the reason this row was filed here." % where
                )
    return out


@pytest.mark.parametrize("key", sorted(DECLARED), ids=lambda k: "%s::%s" % k)
def test_the_code_matches_what_was_declared(key):
    """VERDICT DRIFT FAILS IN BOTH DIRECTIONS.

    A WITHHELD site that starts publishing a url is the leak this guards.
    An ASKED_FOR site wrapped in a describer is the OTHER defect and is
    guarded just as hard.
    """
    sites = [s for s in _all_sites() if (s["file"], s["function"]) == key]
    assert verdict_violations(key, sites) == []


def test_the_twenty_are_still_twenty():
    """THE HEADLINE NUMBER, PINNED, so a silent drift is loud.

    Twenty sites fed this field: 12 WITHHELD + 7 ASKED_FOR + 1 PASSTHROUGH.
    The NO_ADDRESS_IN_SCOPE rows are the guard's completeness surface and were
    never part of that count; they are asserted separately so a reader cannot
    confuse the two.
    """
    tally: dict[str, int] = {}
    for verdict, count in DECLARED.values():
        tally[verdict] = tally.get(verdict, 0) + count
    assert tally[WITHHELD] == 12, tally
    assert tally[ASKED_FOR] == 7, tally
    assert tally[PASSTHROUGH] == 1, tally
    assert tally[WITHHELD] + tally[ASKED_FOR] + tally[PASSTHROUGH] == 20, tally
    assert tally[NO_ADDRESS_IN_SCOPE] == 12, tally


# ---------------------------------------------------------------------------
# Controls -- synthetic sources, never written into linkedin_server/
# ---------------------------------------------------------------------------

_WITHHELD_SHAPE = (
    "async def r(page):\n"
    "    try:\n"
    "        return await page.evaluate(S)\n"
    "    except Exception as exc:\n"
    "        raise ExtractionFailedError('x', hint=_landing_note(page)) from exc\n"
)
_WITHHELD_REVERTED = (
    "async def r(page):\n"
    "    try:\n"
    "        return await page.evaluate(S)\n"
    "    except Exception as exc:\n"
    "        raise ExtractionFailedError('x', url=_url_of(page)) from exc\n"
)
_ASKED_FOR_SHAPE = (
    "async def t():\n"
    "    requested = f'{BASE_URL}/notifications/'\n"
    "    final_url = await BROWSER.goto(page, requested)\n"
    "    raise ExtractionFailedError('x', url=requested)\n"
)
_ASKED_FOR_REVERTED = (
    "async def t():\n"
    "    requested = f'{BASE_URL}/notifications/'\n"
    "    final_url = await BROWSER.goto(page, requested)\n"
    "    raise ExtractionFailedError('x', url=final_url)\n"
)


def test_the_check_would_notice_a_withheld_site_publishing_again():
    """CONTROL. The leak direction, on the exact shape that shipped."""
    good = feeder_sites(_WITHHELD_SHAPE, "s.py")
    assert len(good) == 1 and good[0]["has_url"] is False
    assert good[0]["hint_describes"] is True

    bad = feeder_sites(_WITHHELD_REVERTED, "s.py")
    assert len(bad) == 1 and bad[0]["has_url"] is True
    assert bad[0]["url_is_derived"] is True, bad


def test_the_check_would_notice_an_asked_for_site_going_back_to_the_landing():
    """CONTROL. The other direction, and the negative half in the same test.

    The two sources differ in ONE token. If the walk answered the same for
    both, the first assertion would pass on a checker that convicts nothing
    and the second on a checker that convicts everything.
    """
    good = feeder_sites(_ASKED_FOR_SHAPE, "s.py")
    assert len(good) == 1 and good[0]["url_is_derived"] is False, good

    bad = feeder_sites(_ASKED_FOR_REVERTED, "s.py")
    assert len(bad) == 1 and bad[0]["url_is_derived"] is True, bad

    assert _ASKED_FOR_SHAPE != _ASKED_FOR_REVERTED


def test_the_check_would_notice_a_bare_page_url():
    """CONTROL. The spelling that skips the helper entirely."""
    source = "def t(page):\n    raise ExtractionFailedError('x', url=page.url)\n"
    site = feeder_sites(source, "s.py")[0]
    assert site["url_is_derived"] is True, site


def test_a_landing_bound_by_a_loop_is_still_a_landing():
    """CONTROL. ITERATION IS A BINDING, and the engine that forgot cost a day."""
    source = (
        "async def t():\n"
        "    for u in urls:\n"
        "        landed = await BROWSER.goto(page, u)\n"
        "    raise ExtractionFailedError('x', url=landed)\n"
    )
    site = feeder_sites(source, "s.py")[0]
    assert site["url_is_derived"] is True, site

    loop = (
        "async def t():\n"
        "    for landed in await gather_landings(page):\n"
        "        pass\n"
        "    raise ExtractionFailedError('x', url=landed)\n"
    )
    assert feeder_sites(loop, "s.py")[0]["url_is_derived"] is False, (
        "a name bound from a call this walk does not recognise is NOT "
        "reported derived, and that limit is declared in the docstring"
    )


def test_the_relay_check_would_notice_a_relay_that_stopped_relaying():
    """CONTROL. A relay reading a landing of its own rules all its callers."""
    honest = "def require_rows(rows, *, url):\n    raise ExtractionFailedError('x', url=url)\n"
    site = feeder_sites(honest, "s.py")[0]
    assert site["url_is_parameter"] is True and site["url_is_derived"] is False

    dishonest = (
        "def require_rows(rows, *, url, page=None):\n"
        "    landed = _url_of(page)\n"
        "    raise ExtractionFailedError('x', url=landed)\n"
    )
    bad = feeder_sites(dishonest, "s.py")[0]
    assert bad["url_is_parameter"] is False and bad["url_is_derived"] is True


def test_an_undeclared_site_is_reported_as_undeclared():
    """CONTROL for the enumeration half, on a name that cannot be declared."""
    source = "def a_function_that_was_never_written():\n    raise ExtractionFailedError('x', url=z)\n"
    sites = feeder_sites(source, "s.py")
    keys = {(s["file"], s["function"]) for s in sites}
    assert keys - set(DECLARED) == {
        ("s.py", "a_function_that_was_never_written")
    }


def test_every_feeder_and_describer_name_exists():
    """A DEAD OR TYPO'D NAME SILENTLY ENUMERATES NOTHING.

    It cannot mark a site safe by mistake -- a name nobody calls never matches
    -- so the failure is quiet in the dangerous direction: the sets look
    broader than they are. This checks EXISTENCE, not a contract, and says so.
    """
    defined: set[str] = {"ExtractionFailedError"}
    for path in sorted(SCANNED.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.name)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                defined.add(node.name)
    missing = sorted((FEEDERS | DESCRIBERS) - defined)
    assert not missing, (
        "these are trusted to enumerate or to describe and no function of "
        "that name exists: %s" % missing
    )


def test_there_are_sites_to_rule_on():
    """A RULE ASSERTED OVER ZERO SITES IS A GREEN TEST THAT CHECKS NOTHING."""
    sites = _all_sites()
    assert len(sites) >= 30, len(sites)
    assert any(s["has_url"] for s in sites), "no site publishes a url"
    assert any(not s["has_url"] for s in sites), "no site withholds one"
    assert any(s["hint_describes"] for s in sites), "no site describes a landing"


# ---------------------------------------------------------------------------
# Driven controls -- the source-text rule is not the whole claim
# ---------------------------------------------------------------------------

#: A synthetic landing carrying a vanity slug. NOT a real person: the shape
#: guard in tests/test_no_committed_identity.py is on the SHAPE, because a
#: reviewer cannot tell an invented slug from a real one, so this reuses the
#: suite's own placeholder spelling rather than inventing a new name.
PLANTED_SLUG = "example-person-placeholder"
PLANTED_LANDING = (
    "https://www.linkedin.com/authwall?sessionRedirect="
    "https%3A%2F%2Fwww.linkedin.com%2Fin%2F" + PLANTED_SLUG + "%2F"
)


class _PageThatLanded:
    """A page with a url and nothing else.

    NOT ``tests.plantedpage.PlantedPage``, deliberately: that instrument
    answers every PAGE-CONTROLLED accessor in strings so a reader's coercions
    can be measured, and ``_landing_note`` coerces nothing and reads exactly
    one attribute. Borrowing it here would dress a one-attribute double in
    machinery that measures something else.
    """

    def __init__(self, url: str):
        self.url = url


def test_the_landing_note_publishes_no_character_the_site_chose():
    """DRIVEN, not read. The helper the twelve now call."""
    note = dom._landing_note(_PageThatLanded(PLANTED_LANDING))
    assert PLANTED_SLUG not in note, note
    assert "linkedin.com" not in note.replace("www.linkedin.com", ""), note
    # AND IT MUST STILL SAY SOMETHING. An absence assertion on its own passes
    # on a helper that returns "".
    assert "route" in note and "bounced from" in note, note
    assert "authwall" in note, note


def test_that_hunt_can_find_the_needle_it_is_looking_for():
    """THE POSITIVE CONTROL for the test above.

    Without it, "the slug is not in the note" could mean the search is blind.
    """
    assert PLANTED_SLUG in PLANTED_LANDING
    assert PLANTED_SLUG in ("a string containing " + PLANTED_SLUG)


def test_the_envelope_a_dom_reader_produces_carries_no_url_and_no_slug():
    """THE ROUND TRIP, through the real ``server._error``.

    Built exactly as the twelve build it, because a claim about the envelope
    is worth what the envelope says and not what the raise site looks like.
    """
    page = _PageThatLanded(PLANTED_LANDING)
    exc = ExtractionFailedError(
        "could not read the page: RuntimeError: boom",
        hint=dom._landing_note(page),
    )
    out = server._error(exc)

    assert "url" not in out, out
    assert PLANTED_SLUG not in repr(out), out
    assert "hint" in out and "route" in out["hint"], out


def test_that_round_trip_would_have_convicted_the_code_that_shipped():
    """THE SAME ASSERTION, HANDED THE PRE-REPAIR SHAPE, MUST CONVICT.

    ``url=_url_of(page)`` is what all twelve passed at 479761e. If this
    assertion cannot fail on that, the test above is decoration.
    """
    page = _PageThatLanded(PLANTED_LANDING)
    exc = ExtractionFailedError(
        "could not read the page: RuntimeError: boom",
        url=page.url,
    )
    out = server._error(exc)

    assert "url" in out, "the pre-repair shape must still publish its url here"
    assert PLANTED_SLUG in repr(out), (
        "the pre-repair shape must still LEAK here, or the green above is "
        "measuring nothing"
    )
