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
def test_no_module_contains_a_mutating_call(module: Path):
    source = module.read_text(encoding="utf-8")
    hits = readonly.scan_source_for_mutations(source)
    assert hits == [], (
        f"{module.name} contains calls that could change state: {hits}. "
        "This package has no write path; if the call is genuinely a read, "
        "waive that single line with a trailing '# readonly-ok' so the waiver "
        "shows up in the diff."
    )


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
    assert waived_in.get("dom.py", 0) <= 3, waived_in


# ---------------------------------------------------------------------------
# 2. The injected JavaScript only reads
# ---------------------------------------------------------------------------

INJECTED_SCRIPTS = {
    "HARVEST_LINKED_CARDS_JS": dom.HARVEST_LINKED_CARDS_JS,
    "HARVEST_BLOCK_CARDS_JS": dom.HARVEST_BLOCK_CARDS_JS,
    "READ_PROFILE_JS": dom.READ_PROFILE_JS,
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
    assert len(EXECUTED_SCRIPTS) == 3, sorted(EXECUTED_SCRIPTS)


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
    "https://www.linkedin.com/jobs/search/?keywords=node&f_WT=2",
    "https://www.linkedin.com/in/me/",
    "https://www.linkedin.com/in/sundeep-g/details/skills/",
    "https://www.linkedin.com/notifications/",
    "https://www.linkedin.com/feed/",
    "https://www.linkedin.com/login",
]

BLOCKED = [
    # Actions on LinkedIn.
    "https://www.linkedin.com/jobs/application/12345",
    "https://www.linkedin.com/messaging/thread/2-abc/",
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
    # The job tracker, which the allowlist admits at exactly two addresses.
    # A wildcard query would have let every one of these through.
    "https://www.linkedin.com/jobs-tracker/",
    "https://www.linkedin.com/jobs-tracker/?stage=withdraw",
    "https://www.linkedin.com/jobs-tracker/?stage=archived",
    "https://www.linkedin.com/jobs-tracker/?apply=1",
    "https://www.linkedin.com/jobs-tracker/?stage=saved&save=1",
    "https://www.linkedin.com/jobs-tracker/?a%63tion=delete",
    "https://www.linkedin.com/jobs-tracker/?stage=saved#/../messaging/",
    "https://www.linkedin.com.evil.example/jobs-tracker/?stage=saved",
    # The address the tracker replaced. Nothing builds it any more, so it is
    # off the list -- a pattern kept for a url the server never opens is a
    # door with nobody watching it.
    "https://www.linkedin.com/my-items/saved-jobs/?cardType=SAVED",
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
        f"{BASE_URL}/in/me/",
        f"{BASE_URL}/in/sundeep-g/details/skills/",
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
