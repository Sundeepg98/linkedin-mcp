"""THE PROBE RULE. It is NOT the package rule, and that is the whole design.

``tests/test_readonly.py`` asserts that ``linkedin_server/*.py`` contains
exactly the mutating calls named in ``readonly.SANCTIONED_MUTATIONS`` -- five,
by ``(path, function, kind)``. **That scan has never covered ``scripts/``.**
Measured 2026-09-19: ``MODULES = sorted(PACKAGE_DIR.glob("*.py"))``, 31 files.
The 99 probe scripts, the 140 test modules and the repo-root entrypoint are all
outside it.

So the sentence everyone quotes -- *"this package contains exactly two calls
that can change anything on LinkedIn"* -- is **a guarantee about the package,
not about what this repository's own probes do to a live signed-in account.**

## AND THE PROBES ARE NOT ABSTAINING. MEASURED, NOT ASSUMED.

    scripts/   99 files, 21 with mutating calls, 45 hits
               evaluate 24, click 12, press 7, http_post 1, fill 1

Ten of those clicks are real ``.click()`` calls on a live page, seven are
``page.keyboard.press("Escape")``, and one is a ``page.fill()`` that types a
name into a message composer. **The refusal to press that one wave recorded as
a principle is not a fleet-wide practice**: at least seven probes open a menu by
clicking it and close it with Escape, which is the established way this
repository enumerates a menu.

That is worth stating plainly because a wave declined a menu enumeration on the
grounds that pressing was unsanctioned, and it was unsanctioned **in the
package** while being routine **in the probes**. Nobody had ruled; everybody
assumed.

## WHY THE PACKAGE RULE WOULD BE THE WRONG RULE HERE

A probe legitimately does things the package must never do. Enumerating a menu
REQUIRES opening it, and opening is a read by this repository's own doctrine --
``SANCTIONED_MUTATIONS`` already carries a read-path click for exactly that
reason (``dom.activate_messaging_filter``: *"counted by EFFECT rather than by
verb ... a view filter is a read"*).

Pretending otherwise produces a guard everybody learns to bypass. An
allowlist of ``(path, function, kind)`` over 99 churning probe files would be
stale the day it landed, and its first stale week would teach every wave to
route around it.

## SO THIS GUARD SPLITS THE VERBS INSTEAD OF THE FILES

**OPEN CLASSES** -- a probe may use these freely, because each is either a read
in effect or the means of reaching one: ``click``, ``evaluate``, ``hover``,
``focus_or_blur``, ``select_text``, ``scroll_into_view``, ``keyboard``,
``mouse``.

**GATED CLASSES** -- each one either persists something, sends something, or
hands LinkedIn input a human did not approve. A probe may still use one, but it
must be DECLARED here with its reason, so it arrives in a diff rather than in
an incident. That phrasing is deliberate: it is the standard
``test_the_remaining_raw_source_url_sites_are_a_pinned_inventory`` already sets
in this repository, and it is the only form that survives a fleet nobody is
supervising.

**AND ``press`` IS SPLIT BY ITS ARGUMENT, not by its name.** ``press("Escape")``
closes a menu and changes nothing. ``press("Enter")`` submits. They are the same
call and opposite acts, so the key is what this guard reads.
"""
from __future__ import annotations

import pathlib
import re

from linkedin_server import readonly

SCRIPTS = pathlib.Path(__file__).resolve().parents[1] / "scripts"

#: Verbs a probe may use without declaring anything. See the module docstring.
OPEN_CLASSES: frozenset[str] = frozenset({
    "click",
    "evaluate",
    "hover",
    "focus_or_blur",
    "select_text",
    "scroll_into_view",
    "keyboard",
    "mouse",
})

#: Verbs that need a declaration. Everything the scanner knows that is not
#: open, derived rather than listed, so a detector class added to
#: ``readonly._MUTATION_CALL_PATTERNS`` tomorrow is GATED BY DEFAULT rather
#: than silently open. That default is the conservative direction and it is the
#: one this repository keeps choosing.
def gated_classes() -> frozenset[str]:
    return frozenset(
        kind for kind, _pattern in readonly._MUTATION_CALL_PATTERNS
    ) - OPEN_CLASSES


#: Keys that only ever DISMISS. A press of one of these is treated as open.
#: Escape closes a menu; Enter submits one. Same call, opposite acts.
DISMISS_KEYS = ("Escape",)

#: THE DECLARED EXCEPTIONS, as ``filename -> {class: reason}``.
#:
#: Each entry is somebody's argued decision, not a tolerance. A probe that
#: gains a gated call and is not here turns this file red, and the fix is to
#: write the reason down.
DECLARED: dict[str, dict[str, str]] = {
    "_probe_typeahead_commit.py": {
        "fill": (
            "Types a NEEDLE into a message composer to measure whether "
            "clicking a typeahead suggestion commits a recipient -- the "
            "question writes._recipient_gate turns on and which no read can "
            "answer, because a chip does not exist until a recipient is "
            "committed. Its own docstring bounds it: it never types a message "
            "BODY and never presses a send control, and it refuses to start "
            "on a composer it did not find empty. Declared rather than "
            "forbidden because the measurement is real and the blast radius "
            "is argued in the file."
        ),
    },
    "_probe_badge_and_language_affordances.py": {
        "http_post": (
            "A FALSE POSITIVE, declared as one rather than suppressed. The "
            "line is JavaScript inside a Python string -- langValues.delete('') "
            "-- and the scanner's http_post pattern is "
            "\\.(post|put|patch|delete|fetch)\\s*\\( which cannot tell a JS "
            "Set.delete from an HTTP DELETE. No request is issued. Recorded "
            "here so the next reader does not re-investigate it, and so that "
            "the scanner's real precision limit is written down somewhere "
            "rather than rediscovered."
        ),
    },
}


def _gated_hits() -> list[tuple[str, int, str, str]]:
    """Every gated call in ``scripts/``, as ``(file, line, kind, text)``."""
    gated = gated_classes()
    out: list[tuple[str, int, str, str]] = []
    for path in sorted(SCRIPTS.glob("*.py")):
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for lineno, kind, text in readonly.scan_source_for_mutations(source):
            if kind not in gated:
                continue
            if kind == "press" and any(key in text for key in DISMISS_KEYS):
                continue
            out.append((path.name, lineno, kind, text))
    return out


def test_every_gated_probe_interaction_is_declared():
    """THE GUARD. A probe that gains a gated call shows up in a diff."""
    undeclared = [
        (name, lineno, kind, text)
        for name, lineno, kind, text in _gated_hits()
        if kind not in DECLARED.get(name, {})
    ]
    assert not undeclared, (
        "these probe scripts make a gated interaction nobody declared:\n"
        + "\n".join(
            "    %s:%d  %s  %s" % (n, l, k, t[:80])
            for n, l, k, t in undeclared
        )
        + "\n\nA probe may click, hover and evaluate freely -- those are reads "
        "in effect. These verbs persist something, send something, or hand "
        "LinkedIn input a human did not approve. If the call is right, add it "
        "to DECLARED with the reason and the bound. If it is a false positive, "
        "declare it as one. Do NOT widen OPEN_CLASSES to clear this: that "
        "silences the verb everywhere at once."
    )


def test_the_declaration_table_cannot_rot():
    """A declaration for a call that no longer exists reads as coverage.

    The same law the forbidden-substring roster states: a stale exemption
    grants nothing and hides the next real one behind a familiar name.
    """
    live = {(name, kind) for name, _l, kind, _t in _gated_hits()}
    stale = [
        (name, kind)
        for name, kinds in DECLARED.items()
        for kind in kinds
        if (name, kind) not in live
    ]
    assert not stale, (
        f"these declarations no longer match any call: {stale}. Remove them -- "
        "a declaration for something that is gone is an exemption waiting to "
        "cover a future call nobody argued."
    )


def test_the_open_classes_are_all_real_detector_names():
    """An open class naming a detector that does not exist opens nothing and
    would hide a real verb if the name ever became live."""
    known = {kind for kind, _p in readonly._MUTATION_CALL_PATTERNS}
    unknown = sorted(OPEN_CLASSES - known)
    assert not unknown, (
        f"OPEN_CLASSES names detectors the scanner does not have: {unknown}."
    )


def test_a_new_detector_class_is_gated_by_default():
    """THE CONSERVATIVE DEFAULT, asserted rather than trusted.

    ``gated_classes()`` is derived by SUBTRACTION from the live scanner, so a
    class added to ``readonly._MUTATION_CALL_PATTERNS`` tomorrow is gated
    without an edit here. If it were an explicit list instead, a new detector
    would land OPEN and this guard would quietly stop covering it.
    """
    known = {kind for kind, _p in readonly._MUTATION_CALL_PATTERNS}
    assert gated_classes() == known - OPEN_CLASSES
    assert "set_input_files" in gated_classes()
    assert "fill" in gated_classes()
    assert "click" not in gated_classes()


def test_press_is_split_by_its_key_and_not_by_its_name():
    """``Escape`` dismisses, ``Enter`` submits, and they are the same call.

    Shown both ways on fixture strings, because this is the one place the guard
    reads an ARGUMENT rather than a verb, and a rule that reads arguments is a
    rule that can be wrong in a new direction.
    """
    dismiss = 'await page.keyboard.press("Escape")'
    submit = 'await page.keyboard.press("Enter")'
    assert readonly.scan_source_for_mutations(dismiss), "scanner saw nothing"
    assert readonly.scan_source_for_mutations(submit), "scanner saw nothing"
    assert any(key in dismiss for key in DISMISS_KEYS)
    assert not any(key in submit for key in DISMISS_KEYS), (
        "an Enter press would be treated as a dismissal, which is the one "
        "mistake this split can make."
    )


def test_the_scan_is_actually_reaching_the_probe_directory():
    """A guard that scans nothing passes forever.

    ``scripts/`` churns -- waves add probes daily -- so this asserts the corpus
    is non-trivial rather than pinning a count that would be stale by lunch.
    """
    files = sorted(SCRIPTS.glob("*.py"))
    assert len(files) >= 50, f"only {len(files)} probe scripts found"
    total = sum(
        len(readonly.scan_source_for_mutations(p.read_text(encoding="utf-8")))
        for p in files
    )
    assert total > 0, (
        "the scanner found NO mutating call anywhere in scripts/. That is not "
        "plausible for this corpus and means the scan is dead."
    )


def test_the_guard_fires_on_a_planted_gated_call():
    """SHOWN FAILING, without writing to the tree.

    The planted source is a string. Nothing is created, so this cannot leave a
    probe behind if the test dies midway.
    """
    planted = 'await page.set_input_files("#f", "/tmp/x.pdf")'
    hits = readonly.scan_source_for_mutations(planted)
    kinds = {kind for _l, kind, _t in hits}
    assert "set_input_files" in kinds
    assert kinds & gated_classes(), (
        "a file upload in a probe would not be gated by this guard, which "
        "would make the guard decorative."
    )


def test_an_open_class_is_not_gated():
    """The false-positive control: the guard must NOT fire on a plain click."""
    planted = "await locator.click(timeout=5000)"
    hits = readonly.scan_source_for_mutations(planted)
    kinds = {kind for _l, kind, _t in hits}
    assert kinds == {"click"}
    assert not (kinds & gated_classes()), (
        "a plain click is now gated. Every menu enumeration in this repository "
        "opens a menu by clicking it, so gating click would either stop that "
        "work or produce a declaration list nobody reads."
    )
