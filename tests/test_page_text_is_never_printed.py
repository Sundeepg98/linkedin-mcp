"""A value the page WROTE never reaches a print. The sibling of the url rule.

``tests/test_navigation_is_never_derived.py`` guards one thing: a url the
browser chose. Its taint sources are a ``goto`` return and a ``.url``
attribute, and that is the whole list. **MEASURED 2026-09-05: a person's name
read off an anchor with ``inner_text`` and handed straight to a ``print`` walks
past it GREEN.** Four mutations were planted in a probe -- print the landed
url, navigate to a page-chosen url, smuggle the url through an f-string, print
a raw accessible name. The first three went red. The fourth did not, and it is
the only one of the four that puts a PERSON in a transcript.

That is not a gap in the mutation. It is the guard's scope, and its own
docstring is careful about it: *"'This function is safe' was never true; 'this
function is safe for urls' is."* The file is honest about what it covers. What
nobody had written down is that the uncovered half is the half with the names
in it.

## WHY THIS IS A SEPARATE FILE AND NOT A WIDER ``_TAINTED_ATTRS``

**BECAUSE THE SANITISERS DO NOT TRANSFER, AND MERGING THE TWO WOULD SILENTLY
LAUNDER A NAME.** ``_relation`` reduces a url to a served/redirected verdict
and provably carries no substring of its input -- for a URL. Hand it a person's
name and it returns ``"SERVED, exact"`` or a path depth, which is not
sanitising the name so much as discarding the question. If page text were
added to the same taint set, every function on ``_SANITISERS`` would be
credited with cleaning it, on the strength of an argument that was only ever
made about addresses. A shared taint set with unshared sanitisers is worse than
two rules: it is one rule that is wrong half the time and says so nowhere.

**ONE ENGINE, TWO RULES.** The fixed point, the sink list, the counting-call
and comparison carve-outs are IMPORTED from that module rather than copied, so
they cannot drift. Only the taint SOURCES and the sanitiser list differ, which
is exactly the thing that should differ.

## THE OBJECTION THAT HAD TO BE MET, AND THE NUMBER THAT MEETS IT

That file declines to taint response bodies, and states why:

    "tainting it would flag ``len(payload)`` and every count taken off it, and
    a rule whose true positives arrive buried in false ones gets declared into
    uselessness."

That is a real argument and it applies to page text just as well, so it was
MEASURED rather than argued with. Over ``scripts/`` and ``linkedin_server/``::

    sanitisers as they stand                                    81 sites
    + census_shape                                              80
    + census_redact_rare                                        80
    + census_substitute                                         79
    + subscription_row, membership_row, invitation_badge        79

**CREDITING EVERY SHAPING FUNCTION IN THE PACKAGE REMOVES 2 OF 81 HITS.** So
these sites are not printing shaped text with a shaper the rule cannot see.
They are printing text that never met a shaper at all. The feared false-positive
flood is about 2.5 percent, and the reason is that the machinery which would
have caused it already exists: ``_COUNTING_CALLS`` keeps ``len(text)`` clean and
the ``Compare`` carve-out keeps ``"x" in text`` clean, and between them they
absorb the ordinary uses.

## WHAT IS AND IS NOT A SOURCE

``evaluate`` is included and it is the loudest entry by far, because its return
is whatever the page's own JavaScript produced. That is how most text is read
here. Excluding it to keep the number small would leave the rule guarding the
uncommon path.

**TAINT STOPS AT THE MODULE BOUNDARY, AND THAT IS A FEATURE.** The analysis is
per module, so ``dom.read_surface_census(page)`` is not a source: a probe
calling it holds already-shaped records and is not flagged. The rule therefore
lands where the RAW text lives -- in the module that did the extraction --
which is precisely where this package's privacy placement rule says shaping
must happen. It is a tight rule about a small number of places, not a dragnet.

## WHAT IT DOES NOT COVER, SAID PLAINLY

* A name that leaves through a RETURN VALUE rather than a print. Nothing here
  looks at what a function returns.
* A name written to a FILE. ``write_text`` is not a sink in either rule.
* The inventory below is pinned PER FILE and EXACTLY. A wave that removes one
  raw-text print and adds another in the SAME file keeps the count and passes.
  That hole is why the pin is per file rather than one grand total -- compare
  the sets, never the totals -- and it is stated because a limit nobody wrote
  down is a limit nobody checks.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

from test_navigation_is_never_derived import (  # the ONE engine
    _COUNTING_CALLS,
    _is_sanitiser_call,
    _sink_calls,
)

REPO = pathlib.Path(__file__).resolve().parent.parent
SCANNED = ("scripts", "linkedin_server")

#: CALLS WHOSE RETURN IS SOMETHING THE PAGE WROTE.
#:
#: Playwright's text and attribute readers, plus the two general escape hatches.
#: An entry here is a claim that the value coming back was authored by LinkedIn
#: rather than by this repository -- the same claim ``goto`` carries in the
#: sibling rule, about a different kind of value.
#:
#: ``get_attribute`` covers ``aria-label``, and a nav control's aria-label is
#: HIS OWN NAME on the Me control. That is measured, not hypothesised: it is why
#: ``_probe_connections_badge_cost.py`` prints a family taken off the href and
#: never the label it read.
#:
#: ``content`` returns the whole document. ``json`` and ``text`` are the
#: response readers -- included here even though the sibling rule declines
#: them, because the argument for declining was about NOISE and the noise has
#: now been measured at two sites in eighty-one.
TEXT_CALLS = frozenset({
    "inner_text",
    "text_content",
    "all_text_contents",
    "all_inner_texts",
    "input_value",
    "inner_html",
    "get_attribute",
    "get_property",
    "evaluate",
    "eval_on_selector",
    "eval_on_selector_all",
    "content",
    "text",
    "json",
    "accessible_name",
    "aria_snapshot",
})

#: FUNCTIONS THAT PROVABLY REDUCE PAGE TEXT TO SOMETHING NAMING NOBODY.
#:
#: **DELIBERATELY EMPTY, AND THAT IS THE FINDING RATHER THAN A GAP.** Every
#: candidate was measured and every one of them fails the bar that
#: ``_SANITISERS`` sets -- a function must provably return a value that cannot
#: reconstruct its input:
#:
#:     census_substitute   MEASURED to return a plain human name UNCHANGED. It
#:                         looks for urns, member paths, possessives and digit
#:                         runs, and a name carries none of them.
#:     census_shape        a LENGTH AND CHARSET gate. Returns a short plain
#:                         name verbatim, by design and by its own docstring.
#:     census_redact_rare  a CAPITALISED-RUN rule, not a name detector. A title
#:                         spelling its author in lower case survives it, which
#:                         is asserted in tests/test_subscription_row.py.
#:
#: So this package has no instrument that can decide whether a string is a
#: person's name -- already on the record, and this list is where that finding
#: becomes structural instead of documentary. An entry here would be a promise
#: made on a function's behalf, and ``_redact`` was once admitted to the sibling
#: list on the strength of its NAME and turned out to have no rule at all.
#:
#: The legitimate uses are already covered without any entry: ``len(text)`` by
#: ``_COUNTING_CALLS`` and ``"x" in text`` by the comparison carve-out. That is
#: what the 81-to-79 measurement above is showing.
TEXT_SANITISERS: frozenset[str] = frozenset()


def _reads_page_text(node: ast.AST, tainted: set[str]) -> bool:
    """Does this expression read anything LinkedIn wrote?

    The same walk as the sibling rule's, with the same three stopping
    conditions -- a sanitiser call, a comparison, a counting call -- so that a
    count of a name and a name are not confused. Those carve-outs are IMPORTED,
    not restated.
    """
    stack: list[ast.AST] = [node]
    while stack:
        child = stack.pop()
        if _is_sanitiser_call(child) or _is_text_sanitiser_call(child):
            continue
        if isinstance(child, ast.Compare):
            # A COMPARISON YIELDS A BOOLEAN whatever it compared.
            continue
        if isinstance(child, ast.Call):
            func = child.func
            if isinstance(func, ast.Name) and func.id in _COUNTING_CALLS:
                # COUNTING A THING IS THE DISCIPLINE THIS PACKAGE USES INSTEAD
                # OF PRINTING IT, and the rule has to recognise its own remedy.
                continue
            if isinstance(func, ast.Attribute) and func.attr in TEXT_CALLS:
                return True
        if isinstance(child, ast.Name) and child.id in tainted:
            return True
        stack.extend(ast.iter_child_nodes(child))
    return False


def _is_text_sanitiser_call(node: ast.AST) -> bool:
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    if isinstance(func, ast.Name):
        return func.id in TEXT_SANITISERS
    if isinstance(func, ast.Attribute):
        return func.attr in TEXT_SANITISERS
    return False


def _tainted_names(tree: ast.AST) -> set[str]:
    """Names bound, however indirectly, to something the page wrote.

    To a FIXED POINT and PER MODULE, for the sibling rule's reasons: an
    assignment can taint a name an earlier line already copied, and a closure
    reads from its enclosing scope.
    """
    tainted: set[str] = set()
    for _ in range(6):
        before = set(tainted)
        for node in ast.walk(tree):
            for value, targets in _bindings(node):
                if value is None or not _reads_page_text(value, tainted):
                    continue
                for target in targets:
                    for name in ast.walk(target):
                        if isinstance(name, ast.Name):
                            tainted.add(name.id)
        if tainted == before:
            break
    return tainted


def _bindings(node: ast.AST):
    """Every ``(value, targets)`` pair in a node that BINDS a name.

    **ITERATION IS A BINDING, AND THE SIBLING RULE DOES NOT KNOW THAT.**
    Measured while red-proofing this file: its ``_tainted_names`` walks
    ``Assign`` and ``AnnAssign`` only, so

        rows = await page.evaluate(JS)
        for row in rows:
            print(row["title"])

    taints ``rows`` and never ``row``, and the print goes unseen. That is the
    single most natural way to handle page data in this codebase -- read a list
    of rows, loop, report each -- and the same hole exists in the url rule for
    a list of landed addresses.

    It was found by a planted RED case failing, not by reading the engine. The
    case was written because it is the shape a reader takes, and the engine
    disagreed. Comprehensions and ``with ... as`` bind the same way and are
    included for the same reason.
    """
    if isinstance(node, ast.Assign):
        yield node.value, node.targets
    elif isinstance(node, ast.AnnAssign):
        yield node.value, [node.target]
    elif isinstance(node, (ast.For, ast.AsyncFor)):
        yield node.iter, [node.target]
    elif isinstance(node, (ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp)):
        for generator in node.generators:
            yield generator.iter, [generator.target]
    elif isinstance(node, ast.withitem):
        yield node.context_expr, [node.optional_vars] if node.optional_vars else []
    elif isinstance(node, ast.NamedExpr):
        yield node.value, [node.target]


def text_violations(source: str, label: str = "<source>") -> list[tuple[int, str]]:
    """Every ``print`` or logging call handed something the page wrote."""
    tree = ast.parse(source, filename=label)
    tainted = _tainted_names(tree)
    found: list[tuple[int, str]] = []
    for call, sink in _sink_calls(tree):
        for argument in list(call.args) + [k.value for k in call.keywords]:
            if _reads_page_text(argument, tainted):
                found.append((call.lineno, sink))
                break
    return sorted(found)


# ---------------------------------------------------------------------------
# Shown failing in BOTH directions, on synthetic source
# ---------------------------------------------------------------------------

_RED_CASES = [
    (
        "name = await item.inner_text()\nprint(name)\n",
        "THE MEASURED MISS. This exact shape is green under the url rule.",
    ),
    (
        "title = await anchor.get_attribute('aria-label')\nprint('x %s' % title)\n",
        "an aria-label is a person's name on the Me control",
    ),
    (
        "rows = await page.evaluate(JS)\nfor row in rows:\n    print(row['title'])\n",
        "evaluate returns whatever the page's own script produced",
    ),
    (
        "text = await node.text_content()\nlabel = text\nprint(f'saw {label}')",
        "taint follows the binding, so renaming defeats nothing",
    ),
    (
        "body = await response.json()\nlogger.info('%s', body)\n",
        "a response body reaching a logging verb",
    ),
]

_GREEN_CASES = [
    (
        "name = await item.inner_text()\nprint(len(name))\n",
        "COUNTING a thing is the remedy this package uses instead of printing "
        "it, and a rule that flagged its own remedy would be unusable",
    ),
    (
        "text = await node.text_content()\nprint('needle' in text)\n",
        "a comparison yields a boolean whatever it compared",
    ),
    (
        "print('a fixed message this repository authored')\n",
        "a literal is not the page's",
    ),
    (
        "name = await item.inner_text()\nprint('chars=%d' % len(name))\n",
        "the exact shape the newsletter probe uses to report a title",
    ),
    (
        "rows = await page.evaluate(JS)\nprint('rows=%d' % len(rows))\n",
        "a count off an evaluate is the normal, correct thing to print",
    ),
]


@pytest.mark.parametrize("body,why", _RED_CASES, ids=range(len(_RED_CASES)))
def test_it_goes_red_on_page_text_reaching_a_print(body, why):
    assert text_violations(body), why


@pytest.mark.parametrize("body,why", _GREEN_CASES, ids=range(len(_GREEN_CASES)))
def test_it_stays_green_on_a_value_that_carries_no_page_text(body, why):
    assert text_violations(body) == [], why


def test_the_url_rule_is_green_on_the_case_this_one_was_built_for():
    """THE WHOLE JUSTIFICATION, ASSERTED RATHER THAN RECOUNTED.

    If the sibling rule ever grows to cover this, this assertion fails and this
    file should be reconsidered -- which is the right way round. A guard whose
    reason for existing is only written in its docstring outlives its reason.
    """
    import test_navigation_is_never_derived as urls

    body = "name = await item.inner_text()\nprint(name)\n"
    assert urls.output_violations(body) == [], (
        "the url rule now catches raw page text, so this file's premise has "
        "changed -- re-measure before deleting anything"
    )
    assert text_violations(body), "and this rule must still catch it"


# ---------------------------------------------------------------------------
# The repository, as a pinned inventory
# ---------------------------------------------------------------------------


def _python_files() -> list[pathlib.Path]:
    out: list[pathlib.Path] = []
    for folder in SCANNED:
        out.extend(sorted((REPO / folder).glob("*.py")))
    return out


#: EVERY FILE THAT PRINTS SOMETHING THE PAGE WROTE, AND HOW MANY TIMES.
#:
#: **THIS IS AN INVENTORY, NOT AN ABSOLUTION.** Not one of these sites has been
#: audited. What is claimed is only that they existed when the rule was written,
#: and the point of writing them down is that a NEW one now shows up in a diff
#: instead of in an incident -- which is the same argument
#: ``test_the_remaining_raw_source_url_sites_are_a_pinned_inventory`` is built
#: on, one surface over.
#:
#: IT IS ASSERTED AS AN EXACT MAPPING, so it cannot rot in either direction: a
#: file that gains a site fails, and a file that is FIXED also fails until its
#: entry is corrected. The documentation of a defect may not outlive the defect.
#: That is ``KNOWN_DERIVED_NAVIGATIONS``'s mechanism, and it has been exercised
#: in both directions there.
#:
#: NONE OF THESE ARE THE NEWSLETTER WAVE'S. ``newsletters.py`` and
#: ``_probe_newsletter_subscriptions_live.py`` are absent, which is the whole
#: reason that probe reduces a gated row to a relation before printing it. That
#: discipline was held by hand; this file is what makes it checkable.
#: MEASURED 2026-09-05 17:25 IST against the WORKING TREE, not against a SHA.
#: Several of these files had uncommitted edits from other waves at the time,
#: which is stated because a suite reading is dated by the tree and this one is
#: no exception. 111 sites, 25 files.
KNOWN_TEXT_SINKS: dict[str, int] = {
    "linkedin_server/dom.py": 9,
    "scripts/_capture_toggle_states.py": 1,
    "scripts/_probe_analytics_controls_live.py": 8,
    "scripts/_probe_apply_flow.py": 7,
    "scripts/_probe_apply_route_screen.py": 1,
    "scripts/_probe_comment_overflow_menu.py": 9,
    "scripts/_probe_connections_badge_cost.py": 2,
    "scripts/_probe_events_row_menu.py": 2,
    "scripts/_probe_follow_on_posting.py": 1,
    "scripts/_probe_following.py": 3,
    "scripts/_probe_group_row_affordances.py": 2,
    "scripts/_probe_groups_menu.py": 8,
    "scripts/_probe_in_progress.py": 1,
    "scripts/_probe_interests.py": 3,
    "scripts/_probe_job_search_filter_params.py": 1,
    "scripts/_probe_manage_pages_both.py": 2,
    "scripts/_probe_membership_tally_live.py": 7,
    "scripts/_probe_messaging.py": 4,
    "scripts/_probe_open_to_work_payload.py": 10,
    "scripts/_probe_radio_click_target.py": 10,
    "scripts/_probe_sdui_action_resolver.py": 5,
    "scripts/_probe_thread_reply_surface.py": 4,
    "scripts/_probe_unmeasured_surfaces_live.py": 4,
    "scripts/_probe_where_the_editor_lives.py": 2,
    "scripts/_probe_which_item_is_reacted.py": 5,
}


def test_no_file_prints_page_text_beyond_its_pinned_inventory():
    """The rule, on this repository.

    THE FAILURE IS A ROUTING SLIP, NOT A WALL OF DICT. A red here names the
    file and the direction, because the two directions need opposite responses
    and a bare inequality tells the reader neither.
    """
    measured: dict[str, int] = {}
    for path in _python_files():
        hits = text_violations(
            path.read_text(encoding="utf-8", errors="replace"), path.name
        )
        if hits:
            measured["%s/%s" % (path.parent.name, path.name)] = len(hits)

    gained = sorted(
        "%s  %d -> %d" % (rel, KNOWN_TEXT_SINKS.get(rel, 0), count)
        for rel, count in measured.items()
        if count > KNOWN_TEXT_SINKS.get(rel, 0)
    )
    lost = sorted(
        "%s  %d -> %d" % (rel, count, measured.get(rel, 0))
        for rel, count in KNOWN_TEXT_SINKS.items()
        if measured.get(rel, 0) < count
    )
    assert not gained and not lost, (
        "the page-text inventory moved.\n"
        "  GAINED (a new site hands something LinkedIn wrote to a print --\n"
        "  do NOT add it here to clear the red; emit a count, a relation or a\n"
        "  marker, and if you believe the site is legitimate say so in a\n"
        "  commit message rather than in this dict):\n    %s\n"
        "  LOST (fixed -- correct the entry, because the record of a defect\n"
        "  may not outlive the defect):\n    %s"
        % ("\n    ".join(gained) or "(none)", "\n    ".join(lost) or "(none)")
    )


def test_the_inventory_is_not_a_list_of_files_that_no_longer_exist():
    """An entry naming a deleted file would silently shrink the rule."""
    live = {"%s/%s" % (p.parent.name, p.name) for p in _python_files()}
    missing = sorted(set(KNOWN_TEXT_SINKS) - live)
    assert not missing, missing


def test_there_is_something_to_scan_and_text_calls_among_it():
    """A RULE THAT SCANNED NOTHING WOULD PASS EVERY ASSERTION ABOVE."""
    files = _python_files()
    assert len(files) > 40, len(files)
    seen = 0
    for path in files:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr in TEXT_CALLS
            ):
                seen += 1
    assert seen > 100, (
        "the scan found almost no text-extraction calls, so a green run above "
        "says nothing: %d" % seen
    )
