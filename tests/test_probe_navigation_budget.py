"""CAN A PROBE NAVIGATE WHERE THE ALLOWLIST REFUSES? It can, and this bounds it.

The mutation half of this question was answered on 2026-09-19: the package is
scanned and ``scripts/`` never was. **This is the navigation half, and the
answer is the same sentence.**

## WHAT ``BROWSER.goto`` DOES, AND WHAT A RAW ``page.goto`` SKIPS

``browser.py`` does three things in order, and only the first is a boundary:

    assert_read_url(url)             <- the BOUNDARY half
    await self.wait_for_rate_slot()  <- the ACCOUNT half
    await page.goto(...)
    self._last_navigation_at = ...   <- the ACCOUNT half again

A raw ``page.goto`` does none of them.

## THE CENSUS, PARSED RATHER THAN GREPPED

A file mentioning a guard symbol says nothing about whether a PARTICULAR call
was checked, so this walks the AST and asks which receiver each ``.goto`` was
called on, then walks the enclosing function for a guard call at a LOWER line
number than the navigation.

    scripts/          113 navigation calls
                      103 via BROWSER.goto -- guarded by construction
                       10 raw page.goto, of which 2 guard by hand and
                                              8 DO NOT

    linkedin_server/   both raw sites are legitimate and neither is a hole:
                       browser.py is the enforcement point itself, and
                       writes.py calls assert_read_url on the line BEFORE,
                       deliberately and by its own docstring.

**So eight sites can point this signed-in browser at any address with no
allowlist check.** The read allowlist is a guarantee about the PACKAGE, not
about the REPOSITORY.

## WHY THE RULE IS NOT "NO RAW NAVIGATION"

**A probe legitimately navigates where the package must not.** Measuring what an
unlisted address SERVES is a real question and the only way to answer it is to
go there; a rule forbidding that outright would be wrong and would be bypassed
within a day, which is the same reductio that kept ``tests/`` out of the
mutation scan.

**THE LINE IS BETWEEN A MEASUREMENT AND A ROUTE.** A measurement goes to an
address to find out what it is and reports a relation. A route goes to an
address to GET something the allowlist would not have handed over. Those are
not distinguishable by AST -- but **whether somebody declared which one they
were doing is**, and that is what this file requires.

So: a raw ``page.goto`` must either be preceded by ``assert_read_url`` in its
own function -- a faithful reimplementation of the guarded door -- or be
DECLARED here with its reason.

## AND THE FINDING THAT EXPLAINS THE EROSION

The two halves of ``BROWSER.goto`` were reimplemented at wildly different rates
by the same authors in the same files:

    wait_for_rate_slot + the timestamp stamp     9 of 10
    assert_read_url                              2 of 10

**THE GUARD PEOPLE KEEP IS THE ONE WHOSE ABSENCE HURTS THEM.** Dropping the
rate slot gets a probe throttled and a run ruined. Dropping the allowlist costs
nothing anyone can feel -- the page simply loads. That is not carelessness; it
is what happens when one half of a helper is self-enforcing and the other half
is only polite, and it is why this file exists rather than a note asking people
to remember.
"""
from __future__ import annotations

import ast
import pathlib

SCRIPTS = pathlib.Path(__file__).resolve().parents[1] / "scripts"

#: Receivers whose ``.goto`` is the guarded door.
GUARDED_RECEIVERS = frozenset({"BROWSER", "browser"})

#: Calls that establish the address before a raw navigation.
GUARD_CALLS = frozenset({"assert_read_url", "is_read_url"})

#: RAW SITES THAT EXIST TODAY WITH NO GUARD, recorded with the commit that owns
#: each. **THIS IS NOT AN EXEMPTION TABLE.** An exemption says "this is fine";
#: this says "this is unguarded, here is who owns it, and the guard will notice
#: when it changes".
#:
#: I am NOT vouching for these eight. Declaring a probe's navigation as a
#: legitimate measurement means arguing what it measures and why the allowlist
#: should not bound it, and that argument belongs to the author -- pinning a
#: file adopts its disclosure as well as its design.
#: **SEVEN OF THE ORIGINAL EIGHT LEFT BY BEING FIXED, NOT BY BEING DECLARED**,
#: on 2026-09-19. Four were ROUTED through ``BROWSER.goto`` -- which changed
#: nothing they measure, because ``NAV_TIMEOUT_MS`` IS the 45_000 they
#: hardcoded and the door's settle is the same networkidle-then-flat-wait
#: against the same ``SETTLE_MS``. Three were HAND-GUARDED instead, because
#: routing them would have deleted a measurement rather than merely changed a
#: wait:
#:
#:   _probe_apply_flow          captures the document BEFORE the settle and
#:                              after; a door that settles cannot yield the
#:                              pre-settle document at all
#:   _probe_manage_pages_both   the file name is the reason -- BOTH states
#:   _probe_apply_route_screen  waits for a CONTROL, not a clock (settling is
#:                              the behaviour it was rewritten to stop), and
#:                              turns a failed navigation into a return value
#:                              rather than an exception
#:
#: Hand-guarding is a FIX and not a declaration: ``assert_read_url`` is lifted
#: out of the door and called in the same position in the sequence, so the
#: boundary holds and the measurement is untouched.
KNOWN_UNGUARDED: dict[str, str] = {
    # THE ONE GENUINE DECLARATION, and it is the case the rule was written for.
    #
    # This probe exists to discover WHICH ``?stage=`` value the jobs tracker
    # actually renders, by trying five candidates in order and keeping the
    # first that returns rows: draft, in-progress, inprogress, in_review,
    # applied. Measured against the boundary today, the allowlist admits
    # ``?stage=draft`` and ``?stage=applied`` and REFUSES ``in-progress``,
    # ``inprogress``, ``in_review`` and the bare ``/jobs-tracker/``.
    #
    # **SO NEITHER ROUTING NOR HAND-GUARDING IS AVAILABLE HERE**: both call the
    # same check, and both would raise on three of the five candidates, ending
    # the sweep partway through the question it exists to answer. A probe that
    # can only try the values already known to be admitted cannot discover
    # which value is real.
    #
    # That is what "a probe legitimately navigates where the package must not"
    # means concretely, and it is why the remedy is a declaration rather than a
    # fix. Corroborated independently by ``_probe_apply_flow``'s own docstring,
    # which records the same experiment: only ``draft`` renders the rows, and
    # the other spellings redirect to a bare tracker with no counts.
    "_probe_in_progress.py": "c0b8bb4",
}


def _enclosing(tree: ast.AST, lineno: int):
    best = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.lineno <= lineno and (best is None or node.lineno > best.lineno):
                end = getattr(node, "end_lineno", None)
                if end is None or lineno <= end:
                    best = node
    return best


def _call_name(node: ast.Call):
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return None


def navigation_sites() -> list[dict]:
    """Every ``.goto`` in ``scripts/``, classified. The instrument."""
    out: list[dict] = []
    for path in sorted(SCRIPTS.glob("*.py")):
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except (OSError, SyntaxError, UnicodeDecodeError):
            continue
        for node in ast.walk(tree):
            if not (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "goto"
            ):
                continue
            receiver = node.func.value
            guarded_door = (
                isinstance(receiver, ast.Name) and receiver.id in GUARDED_RECEIVERS
            )
            hand_guarded = False
            if not guarded_door:
                function = _enclosing(tree, node.lineno)
                if function is not None:
                    for inner in ast.walk(function):
                        if (
                            isinstance(inner, ast.Call)
                            and _call_name(inner) in GUARD_CALLS
                            and inner.lineno < node.lineno
                        ):
                            hand_guarded = True
                            break
            out.append({
                "file": path.name,
                "line": node.lineno,
                "guarded_door": guarded_door,
                "hand_guarded": hand_guarded,
            })
    return out


def _unguarded() -> list[dict]:
    return [
        site for site in navigation_sites()
        if not site["guarded_door"] and not site["hand_guarded"]
    ]


def test_no_new_probe_navigates_without_a_guard_or_a_declaration():
    """THE GUARD. A new raw navigation shows up in a diff, not in an incident."""
    undeclared = [
        site for site in _unguarded() if site["file"] not in KNOWN_UNGUARDED
    ]
    assert not undeclared, (
        "these probes navigate with a raw page.goto and no allowlist check:\n"
        + "\n".join(
            "    %(file)s:%(line)d" % site for site in undeclared
        )
        + "\n\nEither route it through BROWSER.goto -- which also takes the "
        "rate slot, so you want it anyway -- or call assert_read_url before "
        "the navigation, or add the file to KNOWN_UNGUARDED with the commit "
        "that owns it. A probe may legitimately navigate where the package "
        "must not; what it may not do is navigate there without anybody "
        "having said so."
    )


#: Calls that take CONTENT out of whatever page is loaded.
CONTENT_READS = frozenset({
    "content", "inner_text", "text_content", "inner_html",
    "all_text_contents", "all_inner_texts", "evaluate",
})


def _content_reads(path: pathlib.Path) -> dict[str, int]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return {}
    found: dict[str, int] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in CONTENT_READS:
                found[node.func.attr] = found.get(node.func.attr, 0) + 1
    return found


def test_the_measurement_exemplar_proves_the_distinction_discriminates():
    """A MEASUREMENT AND A ROUTE ARE DIFFERENT, AND THE REPO HAS ONE OF EACH.

    Without this test the measurement/route distinction would be a phrase.
    ``_probe_landed_address_sweep.py`` is the exemplar -- it exists precisely to
    measure what an address LANDS ON -- and it is shaped exactly as the
    distinction predicts:

        navigations   1, ALL through the guarded door
        content reads ZERO

    **It goes somewhere to find out where it ends up, and takes nothing.**
    Meanwhile all eight recorded unguarded sites call ``page.content()`` or
    ``evaluate`` after navigating, so what they do is not "measure an address"
    -- it is take a full document from wherever they landed.

    **THAT IS THE RISK STATED PRECISELY.** Not that any of them went somewhere
    bad, which is unknown and not statically knowable since every one passes a
    variable -- but that the allowlist is the only thing that would have
    bounded WHERE A FULL DOCUMENT COULD BE TAKEN FROM, and it was not consulted.

    If this exemplar ever starts reading content, the distinction has lost its
    only clean example and this test should fail rather than the phrase
    quietly becoming untrue.
    """
    exemplar = SCRIPTS / "_probe_landed_address_sweep.py"
    assert exemplar.exists(), "the measurement exemplar is gone"

    reads = _content_reads(exemplar)
    assert not reads, (
        f"the landed-address sweep now reads page content: {reads}. It was "
        "the clean example of a MEASUREMENT -- go somewhere, report where you "
        "ended up, take nothing."
    )

    sites = [
        site for site in navigation_sites()
        if site["file"] == exemplar.name
    ]
    assert sites, "the exemplar no longer navigates at all"
    assert all(site["guarded_door"] for site in sites), (
        "the exemplar now navigates raw. It measured addresses THROUGH the "
        "guarded door, which is what made it an argument that the guarded "
        "door does not prevent the measurement."
    )


def test_every_recorded_site_takes_content_and_that_is_the_actual_risk():
    """The other side of the same distinction, asserted so it stays true.

    All eight recorded sites harvest the document. If one is ever rewritten to
    report only a relation -- the landed address, a count -- it has become a
    measurement and should be re-argued rather than left in a table of routes.
    """
    takers = {
        name for name in KNOWN_UNGUARDED
        if _content_reads(SCRIPTS / name)
    }
    missing = sorted(set(KNOWN_UNGUARDED) - takers)
    assert not missing, (
        f"these recorded sites no longer read content: {missing}. That is a "
        "change in KIND, not a tidy-up: a probe that navigates unguarded but "
        "takes nothing is a measurement, and belongs in a different argument "
        "from one that takes a full document."
    )


def test_the_recorded_sites_are_still_unguarded():
    """The INVERSE of an exemption: fixing one turns this red.

    Same idiom as the outage guard's KNOWN_UNFIXED. The record of a defect may
    not outlive the defect, so a probe that gains a guard drops out of the
    measured set and whoever guarded it removes the entry.
    """
    live = {site["file"] for site in _unguarded()}
    repaired = sorted(name for name in KNOWN_UNGUARDED if name not in live)
    assert not repaired, (
        f"these are no longer unguarded: {repaired}. If one was fixed, delete "
        "its KNOWN_UNGUARDED entry -- a stale record reads as coverage and "
        "hides the next real one behind a familiar name."
    )


def test_the_package_navigation_guarantee_still_holds():
    """THE CONTRAST, and it is the half worth protecting.

    Every navigation in ``linkedin_server`` goes through the guarded door
    except two, and both are legitimate: ``browser.goto`` IS the enforcement
    point, and ``writes`` calls ``assert_read_url`` immediately before.

    Asserted here rather than assumed, because the mutation half of this
    question was clean too -- right up until two modules landed unwaived.
    """
    package = SCRIPTS.parent / "linkedin_server"
    raw: list[tuple[str, int]] = []
    for path in sorted(package.glob("*.py")):
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except (OSError, SyntaxError, UnicodeDecodeError):
            continue
        for node in ast.walk(tree):
            if not (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "goto"
            ):
                continue
            receiver = node.func.value
            if isinstance(receiver, ast.Name) and receiver.id in GUARDED_RECEIVERS:
                continue
            function = _enclosing(tree, node.lineno)
            guarded = False
            if function is not None:
                for inner in ast.walk(function):
                    if (
                        isinstance(inner, ast.Call)
                        and _call_name(inner) in GUARD_CALLS
                        and inner.lineno < node.lineno
                    ):
                        guarded = True
                        break
            if not guarded and path.name != "browser.py":
                raw.append((path.name, node.lineno))
    assert not raw, (
        f"unguarded navigation inside the package: {raw}. The package's "
        "navigation guarantee is that every address goes through "
        "assert_read_url. browser.py is the one exception because it IS the "
        "enforcement point."
    )


def test_the_scan_finds_the_guarded_door_too():
    """A census that only ever reports violations is not a census.

    If ``BROWSER.goto`` stopped being recognised, every site would read as raw
    and the numbers above would be nonsense in the alarming direction.
    """
    sites = navigation_sites()
    assert len(sites) >= 100, f"only {len(sites)} navigation sites found"
    guarded = [site for site in sites if site["guarded_door"]]
    assert len(guarded) >= 90, (
        f"only {len(guarded)} sites went through BROWSER.goto; the receiver "
        "check may have stopped matching."
    )


def test_hand_guarding_is_recognised_and_ordered():
    """A guard AFTER the navigation is not a guard, and the check knows it.

    Two probes reimplement the guarded door faithfully -- assert first, then
    navigate. The line-number comparison is what makes that a real check
    rather than a mention count, so it is asserted on a fixture where the two
    orderings are the only difference.
    """
    before = (
        "async def f(page, url):\n"
        "    assert_read_url(url)\n"
        "    await page.goto(url)\n"
    )
    after = (
        "async def f(page, url):\n"
        "    await page.goto(url)\n"
        "    assert_read_url(url)\n"
    )

    def hand_guarded(source: str) -> bool:
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "goto"
            ):
                function = _enclosing(tree, node.lineno)
                for inner in ast.walk(function):
                    if (
                        isinstance(inner, ast.Call)
                        and _call_name(inner) in GUARD_CALLS
                        and inner.lineno < node.lineno
                    ):
                        return True
        return False

    assert hand_guarded(before) is True
    assert hand_guarded(after) is False, (
        "a guard called AFTER the navigation was counted as protection. The "
        "page has already loaded by then."
    )


def test_two_probes_really_do_hand_guard():
    """The positive control on real files, so the ordering check is not
    vacuously passing over a corpus where nobody guards at all."""
    hand = {
        site["file"] for site in navigation_sites()
        if site["hand_guarded"] and not site["guarded_door"]
    }
    assert "_capture_toggle_states.py" in hand
    assert "_probe_follow_on_posting.py" in hand
