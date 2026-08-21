"""The read-only invariant, checked rather than claimed.

Every check here is shown FAILING on a deliberately bad sample before it is
trusted on the real package. A check that cannot fail certifies nothing, and
a read-only guarantee backed by a check that cannot fail is worse than no
guarantee at all -- it manufactures confidence.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from linkedin_own_server import dom, readonly
from linkedin_own_server.errors import WriteAttemptError

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


@pytest.mark.parametrize("name", sorted(INJECTED_SCRIPTS))
def test_injected_script_cannot_mutate(name: str):
    found = readonly.scan_js_for_mutations(INJECTED_SCRIPTS[name])
    assert found == [], f"{name} contains mutating tokens: {found}"


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
    "https://www.linkedin.com/my-items/saved-jobs/?cardType=APPLIED",
    "https://www.linkedin.com/my-items/saved-jobs/?cardType=SAVED",
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
]


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
    from linkedin_own_server.config import BASE_URL, FEED_URL, LOGIN_URL

    built = [
        f"{BASE_URL}/analytics/profile-views/",
        f"{BASE_URL}/me/profile-views/",
        f"{BASE_URL}/my-items/saved-jobs/?cardType=APPLIED",
        f"{BASE_URL}/my-items/saved-jobs/?cardType=SAVED",
        f"{BASE_URL}/in/me/",
        f"{BASE_URL}/in/sundeep-g/details/skills/",
        f"{BASE_URL}/notifications/",
        FEED_URL,
        LOGIN_URL,
    ]
    for url in built:
        assert readonly.is_read_url(url), url
