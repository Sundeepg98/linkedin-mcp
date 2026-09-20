"""A module nobody imports must be RULED, not merely unnoticed.

An AST import-graph pass on 2026-09-19 found roughly 90 KB of reader code in
``linkedin_server/`` that nothing in the package imported. Two of those modules
had been sitting there since 2026-09-05. **None of them was wrong; none of them
was reachable either**, and nobody had written down which of those two facts
was intended.

``linkedin_server/jobfilter.py`` says the same thing about a census row in its
own first paragraph -- *"both halves of that blocker are now built and the row
is still GAP, because nothing joined them"* -- and that sentence sat unread for
two weeks. **This file is that sentence turned into an assertion**, one level
up: a module with no importer either becomes reachable or gets a reason, and a
NEW one fails here until somebody chooses.

## WHY THIS IS NOT A STYLE RULE

Wiring something that should not be a tool is WORSE than leaving it orphaned,
because it widens the tool surface permanently and every future reader inherits
it. ``menus.py`` is the worked example: it classifies labels on a surface where
a label is routinely a person's name, it exists so a PROBE could answer one
measurement question, and there is no operator-facing question it answers. It
should stay uncallable, and keeping it so is what makes the boundary obvious.

**So this file does not push anything toward being wired.** It requires only
that the choice is written down where the next import-graph audit finds it.

## THE SCOPE BUG THIS FILE WAS BORN WITH, recorded because it is the point

My first graph walked ``linkedin_server/*.py`` ONLY and reported ``transport``
as an orphan. It is not: the top-level ``linkedin.py`` entry point imports
``serve_http`` from it. **A scan whose scope excludes the caller reports the
callee as dead** -- the same shape as the lead's grep that matched a local
variable and called two orphans wired. The walk below therefore includes the
repository-root entry points, and :func:`_entry_points` is asserted non-empty
so that a rename cannot silently shrink the corpus back.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

_ROOT = pathlib.Path(__file__).resolve().parent.parent
_PKG = _ROOT / "linkedin_server"

#: Modules that are deliberately not imported by the package, each with the
#: reason. **AN ENTRY HERE IS A CLAIM AND IT IS CHECKED**: the module must
#: exist and must still have no importer, so a stale entry fails as loudly as a
#: missing one. That discipline is copied from
#: ``test_a_correction_is_findable_from_the_claim.NOT_A_CORRECTION``.
DELIBERATELY_UNWIRED: dict[str, str] = {
    "job_collections": (
        "A SHAPER FOR A PAGE NOBODY HAS EVER OPENED -- ruled by the "
        "premium-four wave lead, 2026-09-20. It landed in the same commit as "
        "the two allowlist entries it is the shaper for, on this "
        "repository's standing rule that an address and its name-free reader "
        "land TOGETHER OR NEITHER LANDS. What it cannot have is a wired tool: "
        "there is no capture of /jobs/collections/top-applicant or "
        "/jobs/collections/top-choice and there never has been, so every "
        "selector in it is measured off the two captured SIBLING job lists "
        "and the module is a HYPOTHESIS about its target. Wiring a tool now "
        "would hand a caller a posting count it could not distinguish from a "
        "measured one -- which is the failure the module's own "
        "list_container_seen field exists to prevent, one level up. "
        "NOT PERMANENT, and the unblocking step is one page load: see "
        "_audit/2026-09-20-the-premium-four.md section 9, which names the "
        "exact call and states what each outcome banks. Delete this line in "
        "the commit that fires the reader live and wires the tool. See also "
        "KNOWN_UNWIRED['job_collections.read_job_collection'] in "
        "tests/test_readers_outside_dom_are_a_pinned_inventory.py, which "
        "rules the same module at READER level for the same reason."
    ),
    "menus": (
        "AN INSTRUMENT, NOT A CAPABILITY -- ruled by its author 2026-09-19. It "
        "classifies menu labels INSIDE the page on a surface where a label is "
        "routinely a person's name, and it exists so a probe could settle one "
        "measurement question. There is no operator-facing question it "
        "answers: 'classify the labels on this menu into UI verbs' is "
        "something a measuring wave asks on the way to a reading, never "
        "something he calls. It is also load-bearing for the disclosing-press "
        "mechanism, which requires a control be matched by ATTRIBUTE and never "
        "by label text -- so keeping it uncallable keeps that boundary "
        "obvious. Reached by scripts/_probe_messaging_menu_enumeration.py and "
        "tests/test_menus.py, which is the intended shape."
    ),
    "feed": (
        "A CAPABILITY WITH A MISSING COMPANION, and the gap is mechanical "
        "rather than a ruling. It answers an operator-facing question -- who "
        "is posting, is one author dominating the feed -- but its functions "
        "take HREFS, not a page, so nothing in the package can reach it "
        "without a page reader in front. That is EXACTLY the state groups.py "
        "was in: groups_page.py's own docstring says groups.py 'shipped "
        "2026-09-05 with no page reader, so nothing in this package could "
        "call it and no tool could reach the one question /groups/ was "
        "admitted to answer'. The same fix applies and has not been written. "
        "NOT PERMANENT: delete this entry when a feed page reader lands."
    ),
    "recommendations": (
        "I FILED THIS AS THE IDENTICAL GAP TO feed AND THE MEASUREMENT SAYS "
        "OTHERWISE. It takes hrefs rather than a page, so it does need a page "
        "reader -- but writing one needs the recommendations section's "
        "structure, and FOUR INSTRUMENTS FAILED THEIR CONTROLS trying to find "
        "it (scripts/_probe_profile_sections_live.py, 2026-09-19): an id "
        "substring, the vocabulary-into-the-page matcher, Playwright "
        "`:has-text`, and a re-read after a settle. Each asked for "
        "`Experience` and `Education` alongside, and each read zero for them "
        "on a profile that has both. The detail address "
        "`/in/me/details/recommendations/` is REFUSED by the boundary and "
        "SCROLL is not sanctioned, so neither is a route. **So this is not a "
        "mechanical gap a page reader closes; the surface is UNMEASURED and "
        "the next attempt needs a different instrument, not more effort.** "
        "NOT PERMANENT, and the remaining hypothesis is written in that "
        "probe's docstring."
    ),
    "intro_fields": (
        "LANDED 2026-09-19 (2ac9aea) FROM ANOTHER WAVE, and the ruling is its "
        "author's rather than mine. It is a PROJECTION over an existing "
        "reader -- its own docstring says it 'does not re-read' the container "
        "and takes dom.read_self_owned_editor_fields' output -- so it is in "
        "the same shape as feed and recommendations: correct, and with no "
        "caller. It was written to answer a precondition (does the control "
        "exist to be written?) for three profile rows, which reads as "
        "capability-support rather than as a tool in itself. **THIS ENTRY IS A "
        "HOLDING ONE.** It records that the orphan is known and owed, not that "
        "it was ruled unwireable, and the author should replace this reason "
        "with theirs. NOT PERMANENT."
    ),
    "press": (
        "IN PROGRESS, owned by another wave as of 2026-09-19. The "
        "disclosing-press mechanism is being built in its own module with a "
        "clean entry point and its author will supply the wiring line rather "
        "than editing server.py under another wave's hands. Its sanctioned "
        "mutations are already in readonly.SANCTIONED_MUTATIONS. NOT "
        "PERMANENT: delete this entry when it is wired."
    ),
    "search_results": (
        "A CAPABILITY HELD ON A CONDITION, and the condition is written down "
        "rather than implied. The module and its 963-line test file landed "
        "2026-09-19; the navigation admission for /search/results/ did not, "
        "and deliberately so. A SEARCH RESULTS PAGE IS A LIST OF OTHER "
        "PEOPLE -- every row carries a name and a /in/<slug> href, and a slug "
        "IS a name -- so the admission is held on the rule that it and a "
        "name-free shaper land TOGETHER OR NEITHER LANDS. The groups "
        "admission was granted the same day precisely because it does NOT "
        "have this problem: a group id is numeric, so that address names "
        "nobody and needs no shaper. "
        "THE WAVE THAT WROTE THIS ENDED BEFORE WIRING IT, so this entry "
        "records a held condition rather than a completed ruling -- the "
        "shaper exists in linkedin_server/search_results.py and is tested, "
        "but nothing calls it and no address admits it. "
        "NOT PERMANENT: delete this entry when the admission and a tool land "
        "together. Until then the module is reachable only from "
        "tests/test_search_results.py, which is the honest state."
    ),
}


def _entry_points() -> list[pathlib.Path]:
    """Repository-root modules that import the package.

    THE SCOPE FIX. Walking only ``linkedin_server/*.py`` reports ``transport``
    as an orphan, and it is not -- ``linkedin.py`` imports ``serve_http`` from
    it. A scan whose scope excludes the caller reports the callee as dead.
    """
    return [p for p in _ROOT.glob("*.py") if p.name != "conftest.py"]


def _imported_submodules(path: pathlib.Path) -> set[str]:
    """Every ``linkedin_server`` submodule this file imports, off the AST.

    PARSED, NEVER GREPPED. A module name is exactly the kind of token that
    also appears as a local variable, and a grep for it reported two orphans
    as wired on 2026-09-19.
    """
    out: set[str] = set()
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                parts = alias.name.split(".")
                if parts[0] == "linkedin_server" and len(parts) > 1:
                    out.add(parts[1])
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module == "linkedin_server":
                out.update(alias.name for alias in node.names)
            elif module.startswith("linkedin_server."):
                out.add(module.split(".")[1])
            elif node.level:
                if module:
                    out.add(module.split(".")[0])
                else:
                    out.update(alias.name for alias in node.names)
    return out


def _orphans() -> set[str]:
    modules = [p for p in _PKG.glob("*.py")
               if p.name not in {"__init__.py", "__main__.py"}]
    names = {p.stem for p in modules}
    imported: set[str] = set()
    for path in modules + _entry_points():
        imported |= {n for n in _imported_submodules(path) if n != path.stem}
    return {name for name in names if name not in imported}


def test_the_graph_is_readable_at_all() -> None:
    """The control. A walk that imports nothing reports every module orphaned.

    Without this, a rename of the package or a change to the import forms
    would make :func:`_orphans` return EVERYTHING and the parametrised test
    below would report a catastrophe that is really a broken reader.
    """
    modules = {p.stem for p in _PKG.glob("*.py")}
    assert len(modules) >= 25, f"only {len(modules)} package modules found"
    assert "server" in modules and "dom" in modules
    assert _entry_points(), (
        "no repository-root entry point found. transport is imported ONLY "
        "from there, so an empty list here would report it orphaned."
    )
    orphans = _orphans()
    assert len(orphans) < len(modules) / 2, (
        f"{len(orphans)} of {len(modules)} modules look orphaned, which is a "
        "reading about this walk rather than about the package"
    )


def test_transport_is_not_an_orphan_because_the_entry_point_imports_it() -> None:
    """The specific case that convicted the first version of this walk."""
    assert "transport" not in _orphans(), (
        "transport is being reported as an orphan again, which means the "
        "entry-point scope has been lost. linkedin.py imports serve_http."
    )


def test_every_orphan_is_ruled() -> None:
    """A module with no importer must carry a written reason."""
    unruled = sorted(_orphans() - set(DELIBERATELY_UNWIRED))
    assert not unruled, (
        f"{unruled} are imported by nothing and nobody has ruled on them. "
        "Either wire the module, or add it to DELIBERATELY_UNWIRED with the "
        "reason. An orphan nobody has ruled on is how a backlog grows: the "
        "code is not wrong and it is not reachable, and nothing records which "
        "of those was intended."
    )


@pytest.mark.parametrize("name", sorted(DELIBERATELY_UNWIRED))
def test_every_ruling_is_still_about_a_real_orphan(name: str) -> None:
    """A STALE ENTRY FAILS AS LOUDLY AS A MISSING ONE.

    An allowlist nobody re-checks is a silencer. If a module named here has
    since been wired, the ruling is spent and must be deleted -- otherwise the
    next reader believes a deliberate decision is still in force when the
    thing it decided has moved.
    """
    assert (_PKG / f"{name}.py").exists(), (
        f"{name} is ruled deliberately unwired and the module is gone. "
        "Delete the entry."
    )
    assert name in _orphans(), (
        f"{name} is listed as deliberately unwired and something now imports "
        "it. The ruling is spent: delete the entry, and if the wiring was "
        "deliberate say so where the tool is."
    )


@pytest.mark.parametrize("name", sorted(DELIBERATELY_UNWIRED))
def test_every_ruling_gives_an_actual_reason(name: str) -> None:
    """A one-word reason is how this table becomes a rubber stamp."""
    reason = DELIBERATELY_UNWIRED[name]
    assert len(reason) >= 120, (
        f"the ruling for {name} is {len(reason)} characters. It has to say "
        "WHY -- instrument versus capability, or what is missing -- because a "
        "table of bare names is an allowlist wearing a decision's clothes."
    )
