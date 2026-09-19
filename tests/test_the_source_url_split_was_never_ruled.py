"""``source_url`` IS SHAPED IN SIX PLACES AND RAW IN SEVEN. NOTHING DECIDED THAT.

One field, one kind of value -- the address a read landed on -- and FOURTEEN
emission points that disagree about whether it may be published. Measured
2026-09-04 while a cold verifier was checking something else:

    SHAPED       linkedin_connections (x4), linkedin_my_profile,
                 linkedin_surface_census                            6 in server.py
    RAW          _read_cards, _read_tracker, linkedin_who_viewed_me,
                 linkedin_new_messages, linkedin_job_detail,
                 linkedin_followed_companies, linkedin_notifications
                                                                    7 in server.py
    PASSTHROUGH  shape.envelope, which relays whatever it is given   1 in shape.py

THE DENOMINATOR IS SITES, NOT OCCURRENCES, and the two differ. Grepping the
string in ``server.py`` returns 19 lines; six of those are comments and notes
ABOUT the field, leaving the 13 places it is actually written. This file
counts the places it is written, in both modules, which is 14.

**THE FINDING IS THE SPLIT, NOT THE COUNT, AND THE FIX IS NOT TO WRAP THE
SEVEN.** Wrapping a deliberate publication is as much a defect as leaking an
accidental one: it silently breaks a tool's contract, and the next reader
cannot tell which shapers were reasoned and which were reflexive. This
repository has the worked example in its own source --
``linkedin_my_profile`` shapes ``source_url`` and says in a comment that doing
so "DOES NOT MAKE THIS PAYLOAD SLUG-FREE AND MUST NOT BE READ THAT WAY",
because ``name``, ``public_identifier`` and ``profile_url`` three lines up
carry the operator's identity DELIBERATELY and redacting them would empty the
tool.

So this file encodes THE ANSWER rather than the current state: per site, is the
identifying url part of the tool's contract, incidental and shaped, or simply
UNMEASURED? And it fails if a site changes category without its declaration
changing -- in BOTH directions. A shaper removed from a SHAPED site fails. A
shaper ADDED to a PUBLISHES or UNMEASURED site fails too, which is the half
that stops the reflexive wrap.

## Why most of them are UNMEASURED rather than "fine"

The tempting argument is that these tools land on RESOURCE paths -- a feed, a
notifications page, a job posting -- so their urls carry no identity. **That is
the exact argument that produced the third slug leak of 2026-09-03.** "Paths
are safe" was never the rule; "these paths are safe" was, and carrying the
short form one file over published a member slug out of a probe whose docstring
promised it never printed a url. ``KNOWN_TAINTED_OUTPUT`` in
``tests/test_navigation_is_never_derived.py`` reached the same conclusion about
its eight probe sites and declared them instead of fixing them on an assumption.

UNMEASURED states the truth: a rule now sees the site, nobody has measured what
that surface's landed url actually carries, and the declaration makes that
visible instead of latent. **Closing one means MEASURING it** -- landing on the
surface and reading what the url came back as -- and then moving it to
PUBLISHES or SHAPED with the measurement cited. Do not close a row by
reasoning about what the path ought to be.

## What each raw site actually loads, measured off the source

Two land on module constants and five on a variable the caller supplies::

    linkedin_new_messages          BROWSER.goto(page, FEED_URL)
    linkedin_notifications         BROWSER.goto(page, f"{BASE_URL}/notifications/")
    _read_cards                    BROWSER.goto(page, url)      caller's
    _read_tracker                  BROWSER.goto(page, url)      caller's
    linkedin_who_viewed_me         BROWSER.goto(page, url)      caller's
    linkedin_job_detail            BROWSER.goto(page, url)      caller's
    linkedin_followed_companies    BROWSER.goto(page, url)      caller's

A constant start is not a measured finish: what is emitted is where the browser
LANDED, and ``/in/me/`` landing on ``/in/<vanity>/`` is precisely how this
class of defect was found in the first place.

## The structural fact that makes the split possible

``shape.envelope`` is NEUTRAL. Its body writes ``"source_url": source_url``
into the returned dict verbatim, whatever the caller handed it, so a call to
``envelope`` neither shapes nor leaks -- the verdict belongs entirely to the
argument. Four of the thirteen sites below are ``envelope`` kwargs and are
judged on what they pass, never on the call.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
SCANNED = REPO / "linkedin_server"

#: The field this file rules on. ONE field deliberately: the split was measured
#: here, and a rule asserted over fields nobody has looked at would be a claim
#: rather than a finding.
FIELD = "source_url"

#: Calls whose result cannot reconstruct the url that went in.
#:
#: ``envelope`` IS DELIBERATELY ABSENT and that is the whole reason this file
#: can be written: it passes ``source_url`` through verbatim, so treating it as
#: a shaper would mark all four of its call sites safe on the strength of the
#: function they call rather than the value they hand it.
SHAPERS = frozenset(
    {
        "census_substitute",
        "census_shape",
        "census_redact_rare",
        "redact_thread_id",
        "_path_without_member",
        "_landed_path",
        "_shape_of",
        "_redact",
        # ADDED 2026-09-04, AND THIS TEST IS WHY IT WAS NOTICED. An hour after
        # this file was written, another agent replaced `census_substitute` at
        # all four `linkedin_connections` sites with this named helper, and the
        # SHAPED declaration went red because the set did not know the name.
        # THE TEST WAS RIGHT TO FIRE: it refused a category change that had not
        # been declared. The helper is a STRONGER shaper, not a weaker one --
        # it publishes a module CONSTANT in the ordinary case, drops the query
        # on a mismatch, and closes a bare-member-token-in-a-query gap that
        # `census_substitute` measurably leaves open, which matters here
        # because every Message control on that surface carries
        # `?recipient=<token>`. So the declaration stands and the set widens.
        "_connections_source_url",
    }
)

#: **THE RESIDUAL, NAMED RATHER THAN IMPLIED: THIS SET IS ALSO BY-NAME.**
#: Adding a name here marks every site that calls it as shaped, which is the
#: same shape of trust `_SANITISERS` extends and that
#: `tests/test_a_sanitiser_earns_its_entry.py` exists to bound. Two things keep
#: it smaller than that one: this set only CLASSIFIES sites inside the table
#: below, where every entry already carries a written reason, and it silences
#: no other check in the package. If it ever grows past a handful, enrol these
#: the way that file enrols sanitisers -- against an adversarial table, shown
#: failing. What is asserted today is only that each name EXISTS, which catches
#: a typo and a dead entry and does not pretend to check a contract.

PUBLISHES = "PUBLISHES"
SHAPED = "SHAPED"
UNMEASURED = "UNMEASURED"
#: The NEUTRAL RELAY. ``shape.envelope`` writes its ``source_url`` argument
#: into the returned dict verbatim. Declaring it pins that neutrality as a
#: CHECKED FACT rather than a sentence in a docstring: a shaper added inside
#: ``envelope`` would silently change what four ``linkedin_connections``
#: sites emit -- double-shaping them -- and every other caller too, from one
#: edit nobody would think of as touching those tools.
PASSTHROUGH = "PASSTHROUGH"

#: **THE DECLARATION.** ``(file, enclosing function) -> (category, how many)``.
#:
#: The COUNT is part of the declaration so that a NEW emission point added to a
#: function that already has one fails here rather than inheriting its
#: neighbour's ruling.
DECLARED: dict[tuple[str, str], tuple[str, int]] = {
    # --- PASSTHROUGH: the neutral relay, pinned -----------------------------
    ("shape.py", "envelope"): (PASSTHROUGH, 1),
    # --- SHAPED: incidental, and shaped on a stated ground -------------------
    # Four refusal/success paths on a surface that carries THIRD PARTIES -- his
    # connections -- and the four are ONE ruling applied four times rather than
    # four independent decisions. They now go through `_connections_source_url`
    # rather than `census_substitute` directly; see the note on SHAPERS for why
    # that swap made this entry go red and why the category did not change.
    ("server.py", "linkedin_connections"): (SHAPED, 4),
    # The census's own defect, already fixed and already argued in place: the
    # raw source_url was the ONLY unshaped url in a payload that substituted
    # /in/<member>/ everywhere else, on a surface that also carried third
    # parties.
    ("server.py", "linkedin_surface_census"): (SHAPED, 1),
    # SHAPED FOR CONSISTENCY, NOT BECAUSE IT HIDES ANYTHING -- the source
    # comment says so at length. This tool publishes `name`,
    # `public_identifier` and `profile_url` DELIBERATELY; shaping source_url
    # makes every url this server reports go through one shaper, and does not
    # make the payload slug-free. The deliberate publication lives in those
    # other three fields, which this file does not rule on.
    ("server.py", "linkedin_my_profile"): (SHAPED, 1),
    # SHAPED BECAUSE NOBODY HAS EVER SEEN WHERE THIS ONE LANDS, 2026-09-05, and
    # that is a different ground from the three above rather than a fourth
    # instance of them.
    #
    # The address is a constant carrying no identifier at all --
    # /analytics/search-appearances/ -- so in the ordinary case the shaper
    # changes nothing and the entry looks like pure ceremony. THE ORDINARY CASE
    # IS THE ONE NOBODY HAS OBSERVED. `assert_read_url` gates the REQUESTED url
    # and the landed url is never re-checked, this page had never been opened by
    # anybody in this repository when the tool shipped, and its own docstring
    # says so. So "it lands where it was sent" is a prediction, not a reading.
    #
    # THE HONEST ALTERNATIVE WAS UNMEASURED, AND IT IS THE WRONG CATEGORY HERE
    # rather than the humbler one. UNMEASURED means "raw, and nobody has
    # measured what the surface emits" -- it leaves the value RAW while saying
    # so. That is right for the helpers below, whose callers supply the url and
    # cannot be ruled on separately. Here there is one caller, one constant, and
    # a shaper that costs nothing, so leaving it raw to be honest about the
    # ignorance would spend a real hole to buy an accurate label.
    #
    # WHAT IS NOT CLAIMED: that the substitution would catch whatever a redirect
    # might carry. It rewrites identifier-shaped PATH segments and nothing else.
    # `redirected` is returned beside it precisely so the first live reading can
    # SEE that a redirect happened rather than inferring it from a shaped
    # string, and whoever takes that reading should re-open this entry.
    #
    # **THIS ENTRY RULES ON THE URL. IT DOES NOT RULE ON THE PAYLOAD**, and the
    # distinction matters more here than at any other row in this table because
    # of what this particular page is made of. The other entries name surfaces
    # whose url is the only interesting string; this one names a page RENDERED
    # OUT OF OTHER PEOPLE'S SEARCHES -- their employers, their titles, the words
    # they typed, and possibly their names.
    #
    # What the reader does with those is a SEPARATE question with a separate
    # answer, and it lives in `dom.read_search_appearances` and
    # `dom._search_appearance_labels`: past the first two paragraph pairs the
    # label is withheld INSIDE the page, the two that cross are shaped, tallied
    # and run through `census_redact_rare`, and the only positive publication is
    # an integer count of member links. None of that is asserted by this row.
    # A reader who takes "SHAPED" here as a statement about the payload has
    # read a claim this table does not make.
    ("server.py", "linkedin_search_appearances"): (SHAPED, 1),
    # --- UNMEASURED: raw, and nobody has measured what the surface emits -----
    # Internal helpers, so the landed url is whatever their THREE callers
    # supplied. A helper cannot be ruled on without ruling on its callers, and
    # that is a measurement nobody has taken.
    ("server.py", "_read_cards"): (UNMEASURED, 1),
    ("server.py", "_read_tracker"): (UNMEASURED, 1),
    # Lands on a caller-supplied analytics url.
    ("server.py", "linkedin_who_viewed_me"): (UNMEASURED, 1),
    # Lands on FEED_URL, a module constant -- but what is emitted is where the
    # browser FINISHED, and a constant start is not a measured finish.
    ("server.py", "linkedin_new_messages"): (UNMEASURED, 1),
    # A job posting url. It carries a JOB id rather than a member id, which is
    # an argument worth making and has not been made with a measurement.
    ("server.py", "linkedin_job_detail"): (UNMEASURED, 1),
    ("server.py", "linkedin_followed_companies"): (UNMEASURED, 1),
    ("server.py", "linkedin_notifications"): (UNMEASURED, 1),
}


def _has_shaper(node: ast.AST) -> bool:
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            func = child.func
            name = (
                func.id if isinstance(func, ast.Name)
                else func.attr if isinstance(func, ast.Attribute)
                else ""
            )
            if name in SHAPERS:
                return True
    return False


def _enclosing(tree: ast.AST, lineno: int) -> str:
    """The INNERMOST function containing a line. Innermost, because several of
    these sit in nested helpers and the outer name would misattribute them."""
    best = ("<module>", -1)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.lineno <= lineno <= (node.end_lineno or node.lineno):
                if node.lineno > best[1]:
                    best = (node.name, node.lineno)
    return best[0]


def emission_points(source: str, filename: str) -> list[tuple[str, str, bool]]:
    """``(file, function, shaped?)`` for every place :data:`FIELD` is WRITTEN.

    THREE SPELLINGS, because this repository writes it three ways and a check
    that knew one would report a confident partial count:

        ``envelope(..., source_url=X)``     a keyword argument
        ``{"source_url": X}``               a dict literal entry
        ``out["source_url"] = X``           a subscript assignment
    """
    tree = ast.parse(source, filename=filename)
    found: list[tuple[str, str, bool]] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            for kw in node.keywords:
                if kw.arg == FIELD:
                    found.append(
                        (filename, _enclosing(tree, kw.value.lineno),
                         _has_shaper(kw.value))
                    )
        elif isinstance(node, ast.Dict):
            for key, value in zip(node.keys, node.values):
                if isinstance(key, ast.Constant) and key.value == FIELD:
                    found.append(
                        (filename, _enclosing(tree, value.lineno),
                         _has_shaper(value))
                    )
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if (
                    isinstance(target, ast.Subscript)
                    and isinstance(target.slice, ast.Constant)
                    and target.slice.value == FIELD
                ):
                    found.append(
                        (filename, _enclosing(tree, node.value.lineno),
                         _has_shaper(node.value))
                    )
    return found


def _all_points() -> list[tuple[str, str, bool]]:
    out: list[tuple[str, str, bool]] = []
    for path in sorted(SCANNED.glob("*.py")):
        out.extend(emission_points(path.read_text(encoding="utf-8"), path.name))
    return out


def test_every_emission_point_is_declared():
    """A NEW ONE ARRIVES UNDECLARED AND FAILS.

    That is the whole mechanism: the split existed because a site could be
    added on either side without anybody deciding which side was right.
    """
    seen: dict[tuple[str, str], int] = {}
    for filename, function, _shaped in _all_points():
        seen[(filename, function)] = seen.get((filename, function), 0) + 1

    undeclared = sorted(set(seen) - set(DECLARED))
    assert not undeclared, (
        "these write %s and are not declared: %s. Decide which it is -- "
        "PUBLISHES (the tool's contract deliberately returns an identifying "
        "url), SHAPED (incidental, and it goes through a shaper), or "
        "UNMEASURED (raw, and nobody has measured what that surface emits) -- "
        "and say why. Do NOT wrap it reflexively: wrapping a deliberate "
        "publication breaks a tool's contract silently."
        % (FIELD, undeclared)
    )

    gone = sorted(set(DECLARED) - set(seen))
    assert not gone, (
        "these are declared and no longer write %s: %s. A declaration for a "
        "site that is gone is a comment pretending to be a check -- delete it."
        % (FIELD, gone)
    )

    wrong_count = {
        key: (seen[key], DECLARED[key][1])
        for key in seen
        if key in DECLARED and seen[key] != DECLARED[key][1]
    }
    assert not wrong_count, (
        "the number of %s sites changed in these functions (found, declared): "
        "%s. A new site in a function that already has one does not inherit "
        "its neighbour's ruling." % (FIELD, wrong_count)
    )


@pytest.mark.parametrize(
    "key", sorted(DECLARED), ids=lambda k: "%s::%s" % k
)
def test_the_code_matches_what_was_declared(key):
    """CATEGORY DRIFT FAILS IN BOTH DIRECTIONS.

    Removing a shaper from a SHAPED site is the leak this guards. ADDING one to
    a PUBLISHES or UNMEASURED site is the other defect and is guarded just as
    hard: a reflexive wrap breaks a contract, and once it is in place nobody
    can tell it from a reasoned one.
    """
    category, _count = DECLARED[key]
    states = [
        shaped for filename, function, shaped in _all_points()
        if (filename, function) == key
    ]
    assert states, "no site found for %s" % (key,)

    if category == SHAPED:
        assert all(states), (
            "%s::%s is declared SHAPED and %d of its %d sites no longer pass "
            "through a shaper. Either restore it, or change the declaration "
            "and argue for the change."
            % (key[0], key[1], states.count(False), len(states))
        )
    else:
        assert not any(states), (
            "%s::%s is declared %s and now passes through a shaper. If that "
            "was a considered decision, move it to SHAPED and say why. If it "
            "was reflex, take it out -- wrapping a url that is published on "
            "purpose breaks the tool's contract, and wrapping an UNMEASURED "
            "one hides the fact that nobody has measured it."
            % (key[0], key[1], category)
        )


def test_the_check_would_notice_a_shaper_being_removed():
    """CONTROL. Synthetic source, the SHAPED direction."""
    green = 'def f():\n    return envelope(source_url=shape.census_substitute(x))\n'
    red = 'def f():\n    return envelope(source_url=x)\n'
    assert emission_points(green, "s.py") == [("s.py", "f", True)]
    assert emission_points(red, "s.py") == [("s.py", "f", False)]


def test_the_check_would_notice_a_shaper_being_added():
    """CONTROL. The other direction, which is the one nobody guards.

    Also pins all three spellings, so a site written a way this checker does
    not read cannot pass as an absence.
    """
    kwarg = 'def f():\n    return envelope(source_url=shape.census_shape(x))\n'
    literal = 'def f():\n    return {"source_url": shape.census_shape(x)}\n'
    subscript = 'def f():\n    out["source_url"] = shape.census_shape(x)\n'
    for source, spelling in (
        (kwarg, "keyword argument"),
        (literal, "dict literal"),
        (subscript, "subscript assignment"),
    ):
        assert emission_points(source, "s.py") == [("s.py", "f", True)], spelling


def test_envelope_is_not_treated_as_a_shaper():
    """THE STRUCTURAL FACT THIS FILE RESTS ON, PINNED.

    ``shape.envelope`` writes ``source_url`` into its result verbatim. If a
    future reader added it to :data:`SHAPERS` -- an easy mistake, since it is
    the function four of these sites call -- every one of those four would go
    green on the strength of the call rather than the value.
    """
    assert "envelope" not in SHAPERS
    passthrough = 'def f():\n    return shape.envelope(rows, source_url=landed)\n'
    assert emission_points(passthrough, "s.py") == [("s.py", "f", False)]


def test_every_name_in_shapers_exists():
    """A DEAD OR TYPO'D SHAPER NAME SILENTLY MARKS NOTHING.

    It cannot mark a site UNSHAPED by mistake -- a name nobody calls simply
    never matches -- so the failure is quiet in the dangerous direction: the
    set looks bigger than it is, and a reader trusts a coverage it does not
    have. This does not check a CONTRACT, only existence, and says so.
    """
    defined: set[str] = set()
    for folder in ("linkedin_server", "scripts"):
        for path in sorted((REPO / folder).glob("*.py")):
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.name)
            except SyntaxError:
                continue  # a file mid-edit is not evidence about this set
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    defined.add(node.name)
    missing = sorted(SHAPERS - defined)
    assert not missing, (
        "these are trusted as shapers and no function of that name exists: "
        "%s. A name nobody calls never matches, so it marks nothing while "
        "making this set look broader than it is." % missing
    )


def test_the_existence_check_would_notice_a_dead_name():
    """THE CONTROL for the check above, on a name that cannot exist."""
    defined = {"census_substitute"}
    invented = "_a_shaper_that_was_never_written"
    assert sorted({invented, "census_substitute"} - defined) == [invented]


def test_there_are_sites_to_rule_on():
    """A RULE ASSERTED OVER ZERO SITES IS A GREEN TEST THAT CHECKS NOTHING,
    and this repository has already shipped one of those."""
    points = _all_points()
    assert len(points) >= 10, points
    assert any(shaped for _f, _n, shaped in points), "no site is shaped"
    assert any(not shaped for _f, _n, shaped in points), "no site is raw"
