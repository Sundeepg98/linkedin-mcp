"""No tracked file may carry a real identity, or the key to one.

WHY THIS FILE EXISTS
--------------------
``tests/test_no_committed_credential.py`` closed the credential half of this
question: it hunts the SHAPE of a session cookie across every file git tracks,
because a guard made of NAMES cannot see a VALUE. This file closes the
identity half, and it exists because the fixtures were sanitised correctly and
the KEY was published beside them.

``scripts/_build_follow_fixtures.py`` shipped the complete before->after
mapping -- twenty real company Pages paired with their real numeric ids,
thirteen real slugs, his real name and vanity, a real job title, requisition
id and job id -- committed and pushed, in the same file whose own check
reported the four fixtures clean. Both statements were true at once. A clean
fixture plus its key is not a sanitised fixture; it is a sanitised fixture and
the instructions for reversing it.

THE HARD PART, AND WHY THIS GUARD IS SHAPED THE WAY IT IS. The obvious guard
is a list of the real strings, swept over every tracked file. That guard
CANNOT BE WRITTEN HERE, because writing it down is the leak: the reviewer's
own sweep script had to embed the mapping to hunt for it, which is why that
script lives outside this repo. A tracked guard may not contain the thing it
is looking for.

So this file hunts two things that need no real values at all:

1. **THE SHAPE OF A KEY.** The leak was not a value, it was a PAIRING. A
   table that puts a string appearing in a committed fixture beside a string
   that does NOT appear in any fixture is, by construction, a pre-image: the
   fixture side is public, so the other side is what the fixture was hiding.
   :func:`key_shaped_tables` finds that shape in any tracked Python file
   without knowing a single real name -- and it is exactly what would have
   caught this one on the day it was written.

2. **OPAQUE LINKEDIN IDS, REPO-WIDE.** ``test_sdui_surfaces_fixture.py``
   already hunts member ids and ``urn:li`` in the FIXTURES. The leak was in
   ``scripts/``, which that sweep never looked at. The same patterns are
   re-run here over everything git tracks, for the same reason the credential
   sweep enumerates ``git ls-files`` rather than a list somebody maintains.

WHAT THIS DELIBERATELY DOES NOT COVER, stated so the gap is not mistaken for
coverage. An invented company id and a real one are the same shape, so no
value-free guard can tell them apart in isolation; only the PAIRING gives it
away, which is what (1) reads. And a real employer's campus name in a comment
is just an English phrase -- nothing structural marks it. That case needs the
exact-value sweep in ``scripts/sweep_tracked_for_identity.py``, which reads
its wordlist from a gitignored file because the wordlist IS the key.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from tests.leakwalk import url_spellings
from tests.test_no_committed_credential import tracked_files
from tests.test_sdui_surfaces_fixture import (
    _ALLOWED_OPAQUE_IDS,
    _OPAQUE_ID_PATTERNS,
)

REPO = Path(__file__).resolve().parent.parent
FIXTURE_DIR = REPO / "tests" / "fixtures"

#: Files allowed to contain an identity-shaped string, by EXACT repo-relative
#: path. Both DEFINE the shapes rather than carrying an instance of one.
#: Adding a third entry should feel like the deliberate act it is.
_SHAPE_HOMES = {
    "tests/test_sdui_surfaces_fixture.py",
    "tests/test_no_committed_identity.py",
}

#: A string shorter than this is not evidence of anything -- "Save", "id" and
#: "the" appear in every fixture ever captured.
MIN_MEANINGFUL = 5

#: How many paired rows make a table a KEY rather than a coincidence. Two
#: strings can line up by accident; three rows of the same shape is a table.
MIN_KEY_ROWS = 3


def fixture_blob() -> str:
    """Every committed fixture, concatenated once.

    The fixtures are the PUBLIC half by definition -- anyone with the repo can
    read them. That is exactly what makes them the right thing to test a
    table against: a value in here is not a secret, and a value paired with
    one is the secret it replaced.
    """
    parts = []
    for path in sorted(FIXTURE_DIR.glob("*.html")):
        parts.append(path.read_text(encoding="ascii", errors="replace"))
    return "\n".join(parts)


def _string_rows(node: ast.AST) -> list[list[str]]:
    """Rows of a list/tuple literal whose elements are tuples of strings."""
    if not isinstance(node, (ast.List, ast.Tuple)):
        return []
    rows: list[list[str]] = []
    for element in node.elts:
        if not isinstance(element, (ast.Tuple, ast.List)):
            return []
        values = [
            item.value
            for item in element.elts
            if isinstance(item, ast.Constant) and isinstance(item.value, str)
        ]
        if len(values) < 2:
            return []
        rows.append(values)
    return rows


def key_shaped_tables(source: str, blob: str) -> list[tuple[str, int]]:
    """Tables that pair fixture content with something absent from every fixture.

    Returns ``(name, rows)`` for each offending table. The rule, stated as the
    leak itself would have tripped it:

        a row is a PRE-IMAGE when one of its strings appears in a committed
        fixture and another does not.

    Both-sides-present is fine and is what the scrubbed script now looks like:
    an invented name beside its invented id reveals nothing, because a reader
    can already see that pairing in the fixture. Neither-side-present is fine
    too -- that is an ordinary lookup table about LinkedIn, not about him.
    """
    offenders: list[tuple[str, int]] = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Assign):
            continue
        rows = _string_rows(node.value)
        if len(rows) < MIN_KEY_ROWS:
            continue
        paired = 0
        for values in rows:
            meaningful = [v for v in values if len(v) >= MIN_MEANINGFUL]
            if len(meaningful) < 2:
                continue
            present = [v for v in meaningful if v in blob]
            absent = [v for v in meaningful if v not in blob]
            if present and absent:
                paired += 1
        if paired >= MIN_KEY_ROWS:
            name = next(
                (t.id for t in node.targets if isinstance(t, ast.Name)), "<table>"
            )
            offenders.append((name, paired))
    return offenders


# ---------------------------------------------------------------------------
# 1. The shape of a key
# ---------------------------------------------------------------------------


def test_no_tracked_file_pairs_fixture_content_with_anything_else():
    """THE ONE THAT WOULD HAVE CAUGHT IT.

    Run against the state before the scrub, this fires on
    ``FOLLOWED_PAGES``: twenty rows each pairing an invented Page name that IS
    in ``manage_pages_following.html`` with a real name that is not.
    """
    blob = fixture_blob()
    assert len(blob) > 100_000, "the fixtures did not load; this would pass on nothing"

    found: dict[str, list[tuple[str, int]]] = {}
    for rel in tracked_files():
        if not rel.endswith(".py") or rel in _SHAPE_HOMES:
            continue
        source = (REPO / rel).read_text(encoding="utf-8", errors="replace")
        offenders = key_shaped_tables(source, blob)
        if offenders:
            found[rel] = offenders
    assert found == {}, found


def test_that_detector_fires_on_the_shape_it_was_written_for():
    """THE CONTROL, reconstructed from INVENTED values only.

    The pre-image side here is a made-up string that appears in no fixture,
    which is the whole property being detected -- so this control carries no
    real name while still being the exact shape of the table that leaked.
    """
    blob = fixture_blob()
    invented_in_fixtures = "Ashgrove Systems"
    assert invented_in_fixtures in blob, "fixture content changed; pick another"

    source = (
        "PAGES = [\n"
        f"    ('Real Company One Ltd', {invented_in_fixtures!r}),\n"
        f"    ('Real Company Two Ltd', {invented_in_fixtures!r}),\n"
        f"    ('Real Company Three Ltd', {invented_in_fixtures!r}),\n"
        "]\n"
    )
    offenders = key_shaped_tables(source, blob)
    assert offenders and offenders[0][0] == "PAGES", offenders


def test_the_detector_does_not_fire_on_a_table_that_reveals_nothing():
    """The second half of the rule, and the reason the scrubbed script passes.

    An invented name beside its invented id is not a key: both halves are
    already visible in the fixture, so the pairing tells a reader nothing the
    file they can open does not.
    """
    blob = fixture_blob()
    both_sides = "PAGES = [\n" + "".join(
        f"    ('Ashgrove Systems', 'Ashgrove Systems'),\n" for _ in range(4)
    ) + "]\n"
    assert key_shaped_tables(both_sides, blob) == []

    neither_side = (
        "MODES = [\n"
        "    ('past_24h', 'r86400'),\n"
        "    ('past_week', 'r604800'),\n"
        "    ('past_month', 'r2592000'),\n"
        "]\n"
    )
    assert key_shaped_tables(neither_side, blob) == []


# ---------------------------------------------------------------------------
# 2. Opaque LinkedIn ids, everywhere git looks -- not just in the fixtures
# ---------------------------------------------------------------------------


#: The one opaque shape swept REPO-WIDE, and why only this one.
#:
#: ``_OPAQUE_ID_PATTERNS`` holds two. The member id -- ``ACoAA`` followed by
#: twenty-plus characters -- is twenty-five characters of entropy that names a
#: PERSON, and outside a capture there is no innocent reason to write one
#: down. The other is the ``urn:li:`` PREFIX, which is a naming convention,
#: and prose legitimately mentions it: measured across this repo, every
#: non-fixture hit was synthetic (``urn:li:activity:123`` in an audit note, a
#: truncated ``ACoAAA`` beside an invented name in four test modules). Sweeping
#: the prefix repo-wide would therefore fire five times on nothing, and a
#: guard that cries wolf five times is a guard somebody exempts a directory
#: from. It stays where it discriminates: over the FIXTURES, in
#: ``test_sdui_surfaces_fixture.py``, where a urn prefix really does mean real
#: payload survived a capture.
_MEMBER_ID = dict(_OPAQUE_ID_PATTERNS)["member id"]


@pytest.mark.parametrize("rel", tracked_files(), ids=lambda r: r)
def test_no_tracked_file_carries_a_real_member_id(rel):
    """The fixture sweep, widened to the whole repo.

    The identity leak was in ``scripts/``. The existing opaque-id hunt is
    parametrised over ``tests/fixtures/`` and had no reason to look there,
    which is the same gap ``git ls-files`` closed for credentials.
    """
    if rel in _SHAPE_HOMES:
        pytest.skip("defines the shapes rather than carrying one")
    try:
        text = (REPO / rel).read_text(encoding="utf-8", errors="replace")
    except (OSError, ValueError):  # pragma: no cover - unreadable blob
        pytest.skip("not a text file")
    for match in _MEMBER_ID.finditer(text):
        # The same window the fixture guard uses. The pattern matches from the
        # id's PREFIX, so the allowlist is searched in the tail rather than in
        # the match -- checking the match alone fails every legitimate invented
        # id, which is how this check first behaved.
        tail = text[match.start() : match.start() + 120]
        assert _ALLOWED_OPAQUE_IDS.search(tail), (rel, tail[:90])


def test_the_repo_wide_member_id_sweep_can_actually_fail():
    """A sweep that has only ever passed certifies nothing."""
    planted = "urn:li:fsd_profile:ACoAA" + "Z9y8X7w6V5u4T3s2R1q0P9o8N7m6L5k4J3h2"
    assert _MEMBER_ID.search(planted), "the pattern no longer sees a member id"
    assert not _ALLOWED_OPAQUE_IDS.search(planted)
    # ...and it must not fire on the synthetic shapes this repo really uses,
    # or the exemption pressure starts and the guard loses a directory.
    for benign in ("urn:li:activity:123", "urn%3Ali%3Afsd_profile%3AACoAAA"):
        assert not _MEMBER_ID.search(benign), benign


# ---------------------------------------------------------------------------
# 3. The spelling expansion, which is why a literal list is not enough
# ---------------------------------------------------------------------------


def test_a_phrase_is_hunted_in_its_url_spellings_too():
    """The defect that let a real job title through a 69/69 PASS.

    The forbidden list held the spaced spelling; the ATS apply link in the
    same file spelled it with hyphens. The check was telling the truth about
    the wrong strings. Driven here on a synthetic phrase, so this test names
    no real title.
    """
    spellings = url_spellings("Some Real Job Title")
    assert "Some Real Job Title" in spellings
    assert "Some-Real-Job-Title" in spellings
    assert "Some%20Real%20Job%20Title" in spellings
    assert "Some+Real+Job+Title" in spellings
    assert "SomeRealJobTitle" in spellings
    # And it does not emit fragments too short to mean anything.
    assert all(len(s) >= 5 for s in url_spellings("a b"))


def test_the_exact_value_sweep_exists_and_keeps_its_wordlist_out_of_the_repo():
    """The half no shape can do, and the reason it is a script not a test.

    A campus name in a comment is an English phrase; nothing structural marks
    it. Catching that needs the real strings -- so the sweep reads them from a
    gitignored file, and the sweep itself is tracked while its wordlist never
    is. A test that needed the wordlist would either embed it or skip, and a
    skipping guard is a dead one.
    """
    sweep = REPO / "scripts" / "sweep_tracked_for_identity.py"
    assert sweep.exists(), sweep
    source = sweep.read_text(encoding="ascii")
    assert "url_spellings" in source, "the sweep must expand spellings"
    assert "_sanitisation_key.json" in source

    ignored = (REPO / ".gitignore").read_text(encoding="utf-8")
    assert "_audit/_sanitisation_key.json" in ignored
    assert "scripts/sweep_tracked_for_identity.py" in tracked_files()
