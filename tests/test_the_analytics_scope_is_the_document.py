"""Two readers RULE that their scope is the document, and CODE the opposite.

THE DEFECT, MEASURED 2026-09-20. ``PROFILE_VIEWS_INSIGHTS_JS`` and
``SEARCH_APPEARANCES_JS`` each open with a long comment ruling that the scope is
the DOCUMENT, and each gives the measurement behind the ruling:

    "This scoped to main and returned nulls for three fields on the live page
     -- measured 2026-09-03: trend null, filters [], viewer_rows 0, while the
     controls were on screen and nine viewer rows had just been harvested."

Then both write ``const scope = main || document.body;`` -- which USES ``main``
whenever it exists. The live page has a ``main``; that is *why* it returned
nulls. **The fix was reasoned out, written up and never applied.**

WHY NO TEST CAUGHT IT, and this is the part worth keeping. Every committed
fixture of these pages has **zero** ``<main>`` elements, so every test takes the
``document.body`` branch while production takes the other one. A branch that no
fixture can reach is not covered by a passing suite -- it is invisible to it.
That is the same family as a control that cannot fire on a platform and a guard
that cannot run on its own floor.

WHY THIS IS A SOURCE ASSERTION. These are strings executed inside a page. A
fixture carrying a ``main`` would prove the behaviour, but it would also be a
fixture nobody has captured from the live page, so it would assert MY model of
LinkedIn's markup rather than LinkedIn's. Reading the source asserts exactly
what was ruled, and nothing about a page shape I made up.

THE PRIVACY ARGUMENT IS UNCHANGED BY THE WIDENING, and both scripts state it:
their property is not WHERE they look but WHAT they look at -- bare numbers,
``<label>`` captions, the chart's own sentence, booleans and counts. None of
those reaches a person at document scope any more than at main scope.
"""
from __future__ import annotations

import re

from linkedin_server import dom

SCOPED_READERS = ("PROFILE_VIEWS_INSIGHTS_JS", "SEARCH_APPEARANCES_JS")

#: The shape that obeys ``main``. Matched loosely on purpose: any rewrite that
#: still falls back to the document only when ``main`` is ABSENT has the same
#: defect under a different spelling.
OBEYS_MAIN = re.compile(r"const\s+scope\s*=\s*main\s*\|\|")


def test_neither_reader_scopes_to_main():
    """The ruling is the document. The code must say so."""
    offenders = [
        name for name in SCOPED_READERS
        if OBEYS_MAIN.search(getattr(dom, name))
    ]
    assert not offenders, (
        "these readers rule that the scope is the DOCUMENT and then scope to "
        "main when main exists: %s. The live page HAS a main -- that is why the "
        "2026-09-03 reading returned trend null, filters [], viewer_rows 0. No "
        "fixture can catch this because every committed capture of these pages "
        "has zero <main> elements, so the tests take one branch and production "
        "takes the other." % offenders
    )


def test_both_readers_still_report_main_rather_than_obeying_it():
    """Widening must not delete the two-zeros distinction.

    The comment is explicit that ``main_present`` survives the widening,
    "because the difference between 'no main' and 'an empty main' is exactly
    the kind of two-zeros distinction this package keeps". A fix that widened
    the scope by deleting the ``main`` lookup would pass the test above and
    destroy that, so this pins the reporting half.
    """
    missing = [n for n in SCOPED_READERS if "main_present" not in getattr(dom, n)]
    assert not missing, (
        "widening the scope must not remove main_present: %s" % missing
    )


def test_control_the_guard_convicts_the_shape_it_hunts():
    """A guard that cannot fail certifies nothing -- so fail it on purpose."""
    assert OBEYS_MAIN.search("  const scope = main || document.body;")
    assert not OBEYS_MAIN.search("  const scope = document.body;")
