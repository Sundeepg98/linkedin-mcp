"""THE DIRECTION THE SCANNER'S DIGEST CANNOT REPORT.

``tests/test_readonly_boundary_invariant.py`` pins ``_MUTATION_CALL_PATTERNS``
by a sha. That sha says the scanner is not what it was. **It says nothing about
which way**, and the two directions are not remotely equivalent:

* ADDING a detector refuses more, and costs nothing but a re-freeze;
* REMOVING one makes a whole class of mutating call invisible, in a package
  whose central guarantee is a COUNT of the mutating calls it contains.

**Re-baselining the digest is the identical edit in both cases.** That file says
so itself, about the forbidden list, and names the remedy it adopted:

    "THAT EROSION IS WHY THE ROSTER TEST BELOW EXISTS. A dict of digests that
    gets rewritten whenever the boundary legitimately changes cannot, by
    itself, distinguish a legitimate change from a weakening ... So the two
    structures whose direction matters are now ALSO pinned by their contents."

This file is that remedy applied to the third structure whose direction
matters, and it exists because the scanner's digest moved on 2026-09-19 for a
reason that was an ADDITION -- eleven new classes -- and nothing in the suite
could have told a reviewer that. The check that proved the direction was a
count I typed into a terminal, which is not a check at all.

**WHY THIS IS A SEPARATE FILE.** ``tests/test_readonly.py`` holds the
``FORBIDDEN_SUBSTRINGS_EVER`` precedent this file copies, and that is the
natural home. It is also a file several waves are editing, and the standing
rule here is that an append-only shared file has no git-level protection: a
neighbour's lines land inside a path you legitimately own. A new module has no
such race and costs one import.
"""
from __future__ import annotations

import re

from linkedin_server import readonly

#: EVERY DETECTOR CLASS THIS SCANNER HAS EVER CARRIED.
#:
#: The first eighteen are the set as it stood before 2026-09-19, read off the
#: tuple at that commit rather than remembered. The eleven after them are that
#: day's addition. Growth needs no edit here -- a new class simply is not
#: checked for. A DELETION cannot pass without an edit, and making that edit
#: means writing down why a class of mutating call should stop being detected,
#: which is a boundary decision somebody reviews rather than a digest somebody
#: re-bakes.
DETECTOR_CLASSES_EVER: tuple[str, ...] = (
    # -- the original eighteen ---------------------------------------------
    "click",
    "dblclick",
    "fill",
    "type_text",
    "press",
    "check",
    "select_option",
    "set_input_files",
    "drag",
    "tap",
    "dispatch_event",
    "form_submit",
    "http_post",
    "keyboard",
    "mouse",
    "evaluate",
    "add_init_script",
    "route",
    # -- added 2026-09-19, measured against playwright's own surface --------
    "hover",
    "focus_or_blur",
    "select_text",
    "scroll_into_view",
    "press_sequentially",
    "set_checked",
    "drag_and_drop",
    "script_tag",
    "expose",
    "route_family",
    "http_headers",
)

#: Classes deliberately retired, with the ruling that retired them.
#:
#: **DELIBERATELY EMPTY, AND THAT IS THE POINT.** No detector has ever been
#: removed from this scanner. An entry here is how a removal becomes reviewable
#: instead of invisible, and the empty tuple is the current honest state rather
#: than a placeholder nobody filled in.
DETECTOR_CLASSES_DELIBERATELY_REMOVED: tuple[str, ...] = ()


def _live() -> tuple[str, ...]:
    return tuple(kind for kind, _pattern in readonly._MUTATION_CALL_PATTERNS)


def test_no_detector_has_left_the_scanner():
    """THE DIRECTION, asserted as a SUBSET. The whole point of the file."""
    live = set(_live())
    lost = [
        kind
        for kind in DETECTOR_CLASSES_EVER
        if kind not in live and kind not in DETECTOR_CLASSES_DELIBERATELY_REMOVED
    ]
    assert not lost, (
        f"these detector classes left the scanner: {lost}. Each one was a "
        "class of mutating call somebody decided this package must not "
        "contain unnoticed. Removing one does not weaken a refusal -- it "
        "makes the refusal unable to see its subject, which is worse, "
        "because the package's guarantee is a COUNT and the count would "
        "still look right. If it was intended, record it in "
        "DETECTOR_CLASSES_DELIBERATELY_REMOVED with the ruling."
    )


def test_the_retirement_list_cannot_rot_into_a_blanket():
    """An entry for a LIVE class would grant nothing and hide the next removal.

    Copied from the forbidden-roster precedent, including the reason: a stale
    exemption is worse than none, because it reads as coverage.
    """
    live = set(_live())
    still_present = [
        kind for kind in DETECTOR_CLASSES_DELIBERATELY_REMOVED if kind in live
    ]
    assert not still_present, (
        f"these classes are named as removed and are still live: "
        f"{still_present}. An exemption for something that never left grants "
        "nothing and hides the next real removal behind a stale name."
    )
    unknown = [
        kind
        for kind in DETECTOR_CLASSES_DELIBERATELY_REMOVED
        if kind not in DETECTOR_CLASSES_EVER
    ]
    assert not unknown, (
        f"these classes are named as removed and the roster never knew them: "
        f"{unknown}."
    )


def test_the_roster_knows_every_class_the_scanner_currently_has():
    """The other direction: a class added without being recorded here.

    Without this, the roster silently stops describing the scanner and the
    subset check above keeps passing over an ever-smaller fraction of it --
    which is the slow version of the erosion this file exists to stop.
    """
    unrecorded = [kind for kind in _live() if kind not in DETECTOR_CLASSES_EVER]
    assert not unrecorded, (
        f"the scanner has detector classes the roster does not know: "
        f"{unrecorded}. Add them to DETECTOR_CLASSES_EVER so a later deletion "
        "is visible. This is bookkeeping, not a judgement."
    )


def test_every_class_name_is_unique():
    """A duplicated name would make the subset check unfalsifiable for one of
    them: the roster would find the survivor and report nothing lost."""
    live = _live()
    assert len(live) == len(set(live)), (
        f"duplicate detector class names: {live}"
    )


def test_every_detector_actually_fires_on_something():
    """A PATTERN THAT CANNOT MATCH IS A DETECTOR IN NAME ONLY.

    The roster above pins names. This pins that each name still has a working
    pattern behind it, because a detector could be neutralised WITHOUT being
    removed -- edit its regex to something unmatchable and every check in this
    file still passes. That is the removal wearing a rename's clothes.

    Each probe below is a FIXTURE STRING written here. Nothing is executed,
    no browser is opened, and no page is touched -- which matters for the two
    classes that would otherwise tempt somebody to prove them live.
    """
    probes = {
        "click": "await loc.click()",
        "dblclick": "await loc.dblclick()",
        "fill": "await loc.fill('x')",
        "type_text": "await loc.type('x')",
        "press": "await loc.press('Enter')",
        "check": "await loc.check()",
        "select_option": "await loc.select_option('a')",
        "set_input_files": "await loc.set_input_files('f')",
        "drag": "await loc.drag_to(other)",
        "tap": "await loc.tap()",
        "dispatch_event": "await loc.dispatch_event('click')",
        "form_submit": "await form.submit()",
        "http_post": "await api.post(url)",
        "keyboard": "await page.keyboard.insert_text('x')",
        "mouse": "await page.mouse.move(1, 2)",
        "evaluate": "await page.evaluate('1')",
        "add_init_script": "await page.add_init_script('x')",
        "route": "await page.route('**', handler)",
        "hover": "await loc.hover()",
        "focus_or_blur": "await loc.focus()",
        "select_text": "await loc.select_text()",
        "scroll_into_view": "await loc.scroll_into_view_if_needed()",
        "press_sequentially": "await loc.press_sequentially('x')",
        "set_checked": "await loc.set_checked(True)",
        "drag_and_drop": "await page.drag_and_drop('a', 'b')",
        "script_tag": "await page.add_script_tag(url='u')",
        "expose": "await page.expose_function('f', fn)",
        "route_family": "await page.unroute('**')",
        "http_headers": "await page.set_extra_http_headers({})",
    }
    live = _live()
    missing_probe = [kind for kind in live if kind not in probes]
    assert not missing_probe, (
        f"no fixture probe for these classes: {missing_probe}. A class "
        "admitted without one is admitted without being shown to fire."
    )
    dead = []
    for kind in live:
        hits = readonly.scan_source_for_mutations(probes[kind])
        if not any(found == kind for _line, found, _text in hits):
            dead.append(kind)
    assert not dead, (
        f"these detectors did not fire on the call they exist to catch: "
        f"{dead}. A pattern that cannot match certifies nothing, and a "
        "scanner made of such patterns manufactures confidence at scale."
    )


def test_a_read_is_not_mistaken_for_a_mutation():
    """THE FALSE-POSITIVE CONTROL, without which the file above is half a test.

    A scanner tuned until it flags everything is as useless as one that flags
    nothing, and the failure is quieter: it produces noise, the noise gets
    suppressed, and the suppression is where a real hit goes to die. These are
    the reads this package makes constantly.
    """
    reads = (
        "value = await loc.input_value()",
        "state = await loc.is_checked()",
        "total = await loc.count()",
        "shot = await page.screenshot()",
        "text = await loc.inner_text()",
        "attr = await loc.get_attribute('href')",
    )
    for source in reads:
        hits = readonly.scan_source_for_mutations(source)
        assert not hits, (
            f"a read was classed as a mutation: {source!r} -> {hits}. "
            "Every false positive here is pressure to suppress output, and "
            "suppressed output is where a real hit goes unseen."
        )


def test_the_clear_collision_is_still_absent():
    """``clear`` WAS CONSIDERED AND REJECTED, and this pins the reason.

    ``Locator.clear()`` is a real Playwright mutation, so the obvious move is
    to add ``\\.clear\\s*\\(``. Measured on 2026-09-19, that pattern matches
    ``_CACHE.clear()``, ``_GRANTS.clear()`` and ``_OBSERVED.clear()`` -- three
    dict and set calls in this package with no browser in sight.

    **PLAYWRIGHT'S METHOD NAMES COLLIDE WITH PYTHON'S CONTAINER API**, so a
    text scanner cannot take a bare verb without asking what else in the
    language owns that name. This test fails if somebody adds it anyway, and
    the failure message is the argument.
    """
    ordinary_python = "_CACHE.clear()"
    hits = readonly.scan_source_for_mutations(ordinary_python)
    assert not hits, (
        f"{ordinary_python!r} is now flagged as a mutating call: {hits}. A "
        "bare `.clear(` pattern cannot tell Locator.clear() from dict.clear() "
        "-- and this package calls the second one. If Locator.clear() must be "
        "detected, it needs a pattern that is not satisfied by every container "
        "in the language, not a waiver on each false positive."
    )


def test_navigation_is_deliberately_not_a_detector_class():
    """``goto`` IS NOT HERE ON PURPOSE, and the absence is pinned so it is a
    decision rather than an oversight.

    Measured 2026-09-19: ``\\.goto\\s*\\(`` matches 31 times across
    ``auth.py``, ``browser.py``, ``server.py`` and ``writes.py``. This package
    navigates as its whole job. Adding the class would demand 31 sanction
    entries and would change what the guarantee MEANS -- from "it does not act
    on LinkedIn" to "it does not move" -- which is the operator's call.

    If somebody later rules that navigation belongs in the scanner, this test
    is the thing that has to be deleted, deliberately, with the ruling.
    """
    assert "navigate" not in set(_live())
    assert not readonly.scan_source_for_mutations("await page.goto(url)"), (
        "navigation is now classed as a mutating call. That is a defensible "
        "ruling and it is not this file's to make silently: it turns 31 "
        "existing call sites into unsanctioned mutations."
    )


def test_the_pattern_source_is_still_regex_and_not_a_substring_test():
    """Every detector is a compiled pattern, not a plain string.

    A pattern swapped for a bare substring check would still 'fire' in the
    test above while losing the anchoring that stops ``.route(`` matching
    ``.unroute(`` -- the precise near-miss family this scanner gained classes
    for on 2026-09-19.
    """
    for kind, pattern in readonly._MUTATION_CALL_PATTERNS:
        assert isinstance(pattern, re.Pattern), (
            f"{kind} is not a compiled pattern: {pattern!r}"
        )
        assert pattern.pattern.startswith("\\."), (
            f"{kind}'s pattern does not anchor on a leading dot: "
            f"{pattern.pattern!r}. Without it, a method name is matched "
            "anywhere it appears as a substring of a longer name."
        )
