"""No tracked file may carry a real identity, or the key to one.

WHAT THIS COVERS, AND THE GAP THAT MATTERS MOST
-----------------------------------------------
**NONE OF THESE CHECKS DETECTS A PERSONAL NAME. NAMES HAVE NO SHAPE.**

Every real name found in this family's privacy sweep -- seven recruiters in
``uplers``, four in ``instahyre``, one platform staffer -- was found by a human
reading field names and values. Not one was found by a shape check, and none
could have been: ``Priya Raman`` and an invented ``Alex Rivera`` are the same
shape, the same length, the same character classes.

So a green run here means **no third-party IDENTIFIERS of the shapes below**.
It does NOT mean "no third-party PII". Anyone who reads it as the second has
been misled by the instrument, which would be the worst possible place in this
repo for that particular defect to live. Names still need a person.

WHY THIS FILE EXISTS
--------------------
``tests/test_no_committed_credential.py`` closed the credential half: it hunts
the SHAPE of a session cookie across every file git tracks, because a guard
made of NAMES cannot see a VALUE. This file closes the identity half, and it
exists because the fixtures were sanitised correctly and the KEY was published
beside them -- ``scripts/_build_follow_fixtures.py`` shipped the complete
before->after mapping in the same commit whose own check reported those
fixtures clean. Both statements were true at once. A clean fixture plus its key
is not a sanitised fixture; it is a sanitised fixture and the instructions for
reversing it.

THE DESIGN RULE, WHICH EVERY CHECK BELOW OBEYS
----------------------------------------------
**Hunt by SHAPE. Allowlist the SYNTHETIC. Never blocklist the real.**

A committed list of real strings IS a de-anonymisation key -- that is the
defect that started all of this, so the guard may not contain one. Every
allowlist here holds only invented values, which are safe to commit because
they are already the literal content of the committed fixtures. When a check
fires on something already synthetic, WIDEN THE ALLOWLIST -- never narrow the
shape, never delete the check.

Corollary, and it is not decoration: **failure messages render redacted**. A CI
log is a publication channel, and a guard that prints the identifier it found
has republished it somewhere new.

WHAT IS HUNTED
--------------
1. **The SHAPE OF A KEY** -- a table pairing a string that appears in a
   committed fixture with one that appears in no fixture is a pre-image by
   construction. This is the check that found a SECOND sanitisation script
   nobody had flagged; see :func:`key_shaped_tables`.
2. **Five identifier shapes** -- email, phone, ``/in/`` slug, LinkedIn opaque
   ids (company, member token, numeric urn) and credential/session tokens.

A GUARD IS NOT EXEMPT FROM WHAT IT GUARDS. The first draft of the shared
spelling expander in ``tests/leakwalk.py`` quoted the real job title, in both
spellings, inside the docstring explaining why real job titles end up in
tracked files. It was caught by pointing the sweep at the change that
introduced it -- not by reading it back, which had already happened twice. So
this module is swept like every other file; its own deliberate plants are
PINNED BY COUNT rather than skipped, for the reason in the next paragraph.

WHY NOTHING IS SKIPPED ANY MORE, AND WHAT THAT COST
---------------------------------------------------
This file used to EXCLUDE ``tests/test_sdui_surfaces_fixture.py`` from the
member-id sweep, because that module defines the allowlist and would otherwise
flag itself. A real member URN and a real ``ugcPost`` id were sitting inside
that excluded file, pasted there as inputs to a can-it-fail control -- the real
values, kept next to the fixtures they had been scrubbed out of.

Three independent blindnesses had to line up, and all three are fixed here:

* **the ``\\b`` in the old member-id pattern.** ``\\bACoAA[A-Za-z0-9_-]{20,}``
  cannot match ``...%3AACoAA...`` because the trailing ``A`` of ``%3A`` is a
  word character, so the boundary never fires -- and percent-encoded is the
  form LinkedIn actually serves. Measured, not guessed: the bare id matches,
  the raw-colon urn matches, the percent-encoded urn does not. The boundary is
  gone;
* **the urn prefix was dropped from the repo-wide sweep as too noisy**, which
  was true of the bare prefix and is not true once a length floor is required
  of the id behind it;
* **the file was excluded**, so even a working pattern would not have looked.

An exclusion is not a small thing. It is a promise that nothing in the file
needs checking, and it was wrong.

WIRING A SIBLING REPO
---------------------
Everything repo-specific is in the WIRING block below and nothing else is;
``uplers``, ``instahyre`` and ``naukri`` should be able to take this file and
replace that block alone.

* **naukri** -- add its four synthetic fixture email domains to
  :data:`SYNTHETIC_EMAIL_DOMAINS`, and allow the site's own asterisk-masked
  addresses (``s*****8@gmail.com``), which are masked at source and not ours to
  fix. Its ``API_HEADERS`` dict in ``naukri_server/config.py`` is NOT a key
  table and :func:`key_shaped_tables` already leaves it alone, because it
  cross-references against fixture content rather than asking whether a left
  column merely looks real.
* **uplers / instahyre** -- their opportunity ids are ten digits starting 6-9,
  i.e. the shape of an Indian mobile; extend :data:`ID_CONTEXTS` rather than
  listing values.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from tests.leakwalk import url_spellings
from tests.test_no_committed_credential import tracked_files

REPO = Path(__file__).resolve().parent.parent
FIXTURE_DIR = REPO / "tests" / "fixtures"

# ===========================================================================
# WIRING -- the only repo-specific part. A sibling repo replaces this block.
# ===========================================================================

#: Reserved and stub domains. Subdomains of a reserved name are reserved too,
#: which is why suites can use ``attacker@evil.example.com``.
SYNTHETIC_EMAIL_DOMAINS = frozenset(
    {"example.com", "example.org", "example.net", "localhost", "x.com", "b.co"}
)
SYNTHETIC_EMAIL_SUFFIXES = (".invalid", ".example.com", ".example.org", ".example.net")

#: LinkedIn's own notification senders. Corporate senders, not people -- the
#: address identifies a mail system, and there is no person behind it to
#: protect.
CORPORATE_EMAIL_DOMAINS = frozenset({"linkedin.com", "em.linkedin.com"})

#: Placeholder numbers. Anything all-zeroes is also allowed.
SYNTHETIC_PHONES = frozenset({"9876543210", "1000000000", "0000000000"})

#: A ten-digit run starting 6-9 is a job id as often as it is a mobile, so the
#: allowance is a syntactic CONTEXT rather than a value. A phone under an
#: honest key name (``phone``, ``mobile``, ``contact``) still fires; a phone
#: hidden under a key named ``*_id`` passes, and that cost is carried
#: deliberately.
ID_CONTEXTS = (
    re.compile(r"[?&][A-Za-z_]*(?:jid|job|id)[A-Za-z_]*=$", re.I),
    re.compile(r"/(?:v\d+/)?[A-Za-z_\-]+/$"),
    re.compile(r"[\"'][A-Za-z_]*_id[\"']\s*[:=]\s*[\"']?$", re.I),
)

#: Tokens that make a ``/in/`` slug self-evidently invented. ``fake`` is
#: deliberately NOT here: it asserts synthetic-ness rather than evidencing it,
#: and a real slug containing it would pass.
SYNTHETIC_SLUG_TOKENS = (
    "test", "someone", "somebody", "example", "anonymous", "a-real-person",
    "another-person", "candidate", "placeholder", "redacted", "hidden",
)

#: The invented slug family these fixtures actually use. Listing them is safe
#: -- they ARE the committed fixture content -- and a growing set shows up in
#: a diff, which a token convention would not.
SYNTHETIC_SLUGS = frozenset(
    {
        "alex-r", "alex-r-12ab34", "alex-rivera-8c21",
        "arun-b-4c19d833", "arun-balakrishnan-4c19d833",
        "dana%2Dwhitfield%2D4b12", "meera-iyer",
        "priya-raman-123", "priya-sharma-12ab34", "priya-sharma-8a41b207",
        "robin%2Dellery%2D77c3", "rohan-desai-71f2e004",
        "sam%2Dokonkwo%2D31a9", "some-person-a1b2c3", "some-real-slug-99",
    }
)

#: Invented LinkedIn numeric ids -- company ids across the fixtures, and the
#: synthetic content urns. Starts from measurement, grows only with invented
#: values.
SYNTHETIC_IDS = frozenset(
    {
        "20387164", "26105338", "27419063", "27553102", "28871450", "29604118",
        "3067452", "43902517", "4471905", "508933", "5300011", "53000011",
        "53000012", "5300013", "5300014", "53000015", "53000016", "5417062",
        "5820114", "610427", "61903442", "66208431", "79004613", "80215647",
        "84120775", "87332095", "88410926", "902611",
        "7400000000000000001", "7400000000000000002", "7400000000000000003",
        "7490000000000000001", "7490000000000000002",
    }
)

#: Invented member tokens, matched as a PREFIX because a percent-encoded urn
#: can carry trailing characters that belong to the surrounding markup.
SYNTHETIC_MEMBER_TOKENS = (
    "ACoAAB1c2D3e4F5g6H7i8J9k0L1m2N3o4P5q6R7",
    "ACoAAC8s7T6u5V4w3X2y1Z0a9B8c7D6e5F4g3H2",
    "ACoAAA1B2C3D4E5F6G7H8I9J0KLMNOPQRSTUVWX",
    "ACoAAB7hidden",
    "ACoAAAB",
)

#: A credential value that is obviously not one.
PLACEHOLDER_MARKERS = ("xxx", "dummy", "fake", "redacted", "placeholder", "<", "...")

#: Files that deliberately CONTAIN a violation, with how many the shape may
#: find there. Pinned by COUNT rather than skipped: a skip is a promise that
#: nothing in the file needs checking, and that promise is exactly what hid a
#: real member URN inside the fixture-guard module. A new real id in one of
#: these files changes the count and goes red.
DECLARED_PLANTS = {
    # This module's own controls: one planted violation per shape, plus the
    # allowlisted-form examples that are themselves shape-valid.
    ("tests/test_no_committed_identity.py", "company id"): 1,
    ("tests/test_no_committed_identity.py", "credential"): 1,
    ("tests/test_no_committed_identity.py", "email"): 2,
    ("tests/test_no_committed_identity.py", "linkedin slug"): 1,
    ("tests/test_no_committed_identity.py", "member token"): 3,
    ("tests/test_no_committed_identity.py", "phone"): 1,
    ("tests/test_no_committed_identity.py", "urn id"): 1,
    # The fixture guard's can-it-fail control, whose synthetic member token is
    # deliberately absent from the allowlist -- that IS the property it tests.
    ("tests/test_sdui_surfaces_fixture.py", "member token"): 1,
    # The messaging probe's redaction test needs a urn-SHAPED literal to feed
    # its redactor. THIS ENTRY WAS EARNED THE HARD WAY: that file first shipped
    # with the REAL member urn the probe had printed, and this guard caught it
    # between commit and push. The literal there now is invented (nine digits
    # that are nobody's), which is the rule -- a self-test needs a shape-VALID
    # literal, never a TRUE one. The count is pinned at 1 so a second urn
    # appearing in that file still fails, and declaring it here keeps this
    # guard live on every OTHER shape in the file rather than assembling the
    # urn at runtime to hide it, which would blind the guard to a real value
    # pasted in later.
    ("tests/test_probe_redaction.py", "urn id"): 1,
    # THE SECOND URN-SHAPED LITERAL, 2026-08-30, and it is here for the same
    # reason as the one above and by the same remedy: the file fired, the value
    # is already synthetic, so the ALLOWLIST WIDENS.
    #
    # tests/test_writes_nine.py certifies that ``writes._target_for`` declines
    # to validate the SHAPE of a feed-item urn -- this server has never read
    # one unshaped, because linkedin_surface_census substitutes ``<urn>`` out
    # before counting, so enforcing ``urn:li:activity:<digits>`` would be
    # asserting a shape nobody has seen. Demonstrating "no shape is enforced"
    # requires feeding it a urn-SHAPED string beside a string that is nothing
    # like one and showing the two treated identically. A shape-valid literal
    # is the test, so it cannot be paraphrased away.
    #
    # The literal there is nineteen ZEROES, which is nobody's -- the same
    # all-zeroes convention SYNTHETIC_PHONES already carries. Pinned at 1 so a
    # SECOND urn appearing in that file still fails, and declared here rather
    # than assembled at runtime for the reason spelled out directly above:
    # hiding a shape from the scanner blinds it to a real value pasted in
    # later, which is the failure this whole file exists to catch.
    ("tests/test_writes_nine.py", "urn id"): 1,
    # A planted session cookie, by exact path, in the module that defines it.
    ("tests/test_no_committed_credential.py", "credential"): 1,
}

# ===========================================================================
# The shapes
# ===========================================================================

#: Suffixes whose bytes are not text and cannot be read for identifiers.
BINARY_SUFFIXES = frozenset(
    {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".db", ".ico",
     ".woff", ".woff2", ".ttf", ".pyc", ".so", ".dll", ".exe", ".whl"}
)

#: Files whose content is hashes, which manufacture false emails and false
#: ten-digit runs.
HASHY = re.compile(r"(requirements.*\.txt|\.lock)$", re.I)

EMAIL_SHAPE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,24}")
PHONE_SHAPE = re.compile(r"(?<![\d.])(?:\+?91[-\s]?)?[6-9]\d{9}(?![\d.])")
PHONE_E164_SHAPE = re.compile(r"\+\d{1,3}[-\s]?\d{6,12}")
SLUG_SHAPE = re.compile(r"(?:linkedin\.com)?/in/([A-Za-z0-9\-_%]{3,})")
COMPANY_ID_SHAPE = re.compile(r"(?:/company/|currentCompany=|companyId=)(\d{3,})")

#: NO WORD BOUNDARY, and that is the whole fix. ``\bACoAA`` cannot match
#: ``%3AACoAA`` -- the trailing ``A`` of the percent-encoded colon is a word
#: character -- and percent-encoded is the form LinkedIn serves.
MEMBER_TOKEN_SHAPE = re.compile(r"ACoAA[A-Za-z0-9_\-]{10,}")

#: The urn prefix WITH a length floor on the id behind it. The bare prefix is
#: too noisy to sweep repo-wide -- prose says ``urn:li:activity:123`` -- but a
#: prefix followed by a six-digit-or-longer id is never prose.
URN_ID_SHAPE = re.compile(r"urn(?::|%3A)li(?::|%3A)[a-zA-Z_]+(?::|%3A)\(?(\d{6,})")

JWT_SHAPE = re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{5,}")
COOKIE_SHAPE = re.compile(
    r"(?:li_at|JSESSIONID|li_rm|bcookie|bscookie|nauk_at|sessionid|csrftoken)"
    r"\s*[=:]\s*\"?([^\s\"',]{20,})",
    re.I,
)

#: A ten-digit run inside a UUID's tail is a coincidence of hex digits that
#: happen to be decimal, not a telephone number. Measured on
#: ``tests/fixtures/job_detail.html``, whose only phone-shaped hit sits inside
#: ``id="ab7dc03f-6282-46a6-a3b9-XXXXXXXXXXe2"``. That resolves the one item a
#: sibling repo's sweep left explicitly UNRESOLVED.
UUID_SHAPE = re.compile(
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
)


def redact(value: str) -> str:
    """``<first2>..<last2>`` plus a length. Never the identifier itself."""
    if len(value) <= 6:
        return f"<{len(value)} chars>"
    return f"{value[:2]}..{value[-2:]} <{len(value)} chars>"


def _email_ok(match: re.Match[str], text: str) -> bool:
    domain = match.group(0).rsplit("@", 1)[1].lower().rstrip(".")
    if domain in SYNTHETIC_EMAIL_DOMAINS or domain in CORPORATE_EMAIL_DOMAINS:
        return True
    return any(domain.endswith(suffix) for suffix in SYNTHETIC_EMAIL_SUFFIXES)


def _phone_ok(match: re.Match[str], text: str) -> bool:
    digits = re.sub(r"\D", "", match.group(0))
    for cut in (0, 1, 2, 3):
        candidate = digits[cut:]
        if candidate and (set(candidate) == {"0"} or candidate in SYNTHETIC_PHONES):
            return True
    if any(
        found.start() <= match.start() and match.end() <= found.end()
        for found in UUID_SHAPE.finditer(text)
    ):
        return True
    before = text[max(0, match.start() - 40) : match.start()]
    return any(context.search(before) for context in ID_CONTEXTS)


def _slug_ok(match: re.Match[str], text: str) -> bool:
    slug = match.group(1)
    if slug in SYNTHETIC_SLUGS or slug.lower() in {"me", "in"}:
        return True
    lowered = slug.lower()
    return any(token in lowered for token in SYNTHETIC_SLUG_TOKENS)


def _id_ok(match: re.Match[str], text: str) -> bool:
    return match.group(1) in SYNTHETIC_IDS


def _member_ok(match: re.Match[str], text: str) -> bool:
    return match.group(0).startswith(SYNTHETIC_MEMBER_TOKENS)


def _credential_ok(match: re.Match[str], text: str) -> bool:
    value = match.group(1) if match.groups() else match.group(0)
    lowered = value.lower()
    if any(marker in lowered for marker in PLACEHOLDER_MARKERS):
        return True
    return len(set(value)) <= 2


#: name -> (pattern, allowed?). The name is what a failure reports and what
#: :data:`DECLARED_PLANTS` is keyed on.
SHAPES: tuple[tuple[str, re.Pattern[str], object], ...] = (
    ("email", EMAIL_SHAPE, _email_ok),
    ("phone", PHONE_SHAPE, _phone_ok),
    ("phone", PHONE_E164_SHAPE, _phone_ok),
    ("linkedin slug", SLUG_SHAPE, _slug_ok),
    ("company id", COMPANY_ID_SHAPE, _id_ok),
    ("member token", MEMBER_TOKEN_SHAPE, _member_ok),
    ("urn id", URN_ID_SHAPE, _id_ok),
    ("credential", JWT_SHAPE, _credential_ok),
    ("credential", COOKIE_SHAPE, _credential_ok),
)


def hits_in(text: str, *, only: str | None = None) -> list[tuple[str, str]]:
    """``(shape name, redacted value)`` for everything not allowed."""
    found: list[tuple[str, str]] = []
    for name, pattern, allowed in SHAPES:
        if only is not None and name != only:
            continue
        for match in pattern.finditer(text):
            if not allowed(match, text):
                found.append((name, redact(match.group(0))))
    return found


def sweepable() -> list[str]:
    return [
        rel
        for rel in tracked_files()
        if Path(rel).suffix.lower() not in BINARY_SUFFIXES
    ]


# ---------------------------------------------------------------------------
# 1. The five identifier shapes, over every tracked file
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("rel", sweepable(), ids=lambda r: r)
def test_no_tracked_file_carries_a_real_identifier(rel):
    """Nothing is skipped. Files that deliberately plant one are pinned."""
    path = REPO / rel
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:  # pragma: no cover - unreadable blob
        return
    if HASHY.search(rel):
        return

    found = hits_in(text)
    counted: dict[str, int] = {}
    for name, _ in found:
        counted[name] = counted.get(name, 0) + 1

    for name, count in sorted(counted.items()):
        allowed = DECLARED_PLANTS.get((rel, name), 0)
        assert count <= allowed, (
            f"{rel}: {count} unallowed {name} hit(s), {allowed} declared. "
            f"{[value for shape, value in found if shape == name]}"
        )


def test_the_sweep_actually_looked():
    """A parametrised sweep passes vacuously on an empty file list."""
    assert len(sweepable()) >= 50


@pytest.mark.parametrize(
    "shape, planted",
    [
        ("email", "somebody@a-real-company.co.uk"),
        ("phone", "he can be reached on 9123456789 any evening"),
        ("linkedin slug", "https://www.linkedin.com/in/jordan-mcallister-7f21/"),
        ("company id", "/company/98765432"),
        ("member token", "urn%3Ali%3Afsd_profile%3AACoAAZz9Yy8Xx7Ww6Vv5Uu4Tt3Ss2Rr1Qq0Pp"),
        ("urn id", "urn:li:ugcPost:7511111111111111111"),
        # NOT an li_at-shaped value: tests/test_no_committed_credential.py
        # hunts "AQ" + 40 chars across every tracked file and caught the
        # first version of this plant. Its guard is right and this control
        # does not need that shape -- so the plant moved rather than the
        # file being added to that guard's exemption list.
        ("credential", "sessionid=7hQ2mNbVc9XpLw3ZrYt6JkSd8FgHjKl0Zx"),
    ],
)
def test_every_shape_can_actually_fail(shape, planted):
    """Each check, shown failing on a synthetic violation of its own shape.

    Never a real identifier: a control that needs one has the same defect as
    the fixture it is guarding.
    """
    names = {name for name, _ in hits_in(planted)}
    assert shape in names, (shape, names)


@pytest.mark.parametrize(
    "shape, benign",
    [
        ("email", "write to nobody@example.com or team@evil.example.org"),
        ("phone", "id=ab7dc03f-6282-46a6-a3b9-7312345620e2 is a uuid"),
        ("phone", "the placeholder 9876543210 is not a person"),
        ("linkedin slug", "https://www.linkedin.com/in/alex-rivera-8c21/"),
        ("company id", "/company/5417062"),
        ("member token", "ACoAAB1c2D3e4F5g6H7i8J9k0L1m2N3o4P5q6R7"),
        ("urn id", "urn:li:ugcPost:7400000000000000001"),
        ("credential", 'JSESSIONID="ajax:xxxxxxxxxxxxxxxxxxxxxxxx"'),
    ],
)
def test_the_synthetic_forms_are_allowed(shape, benign):
    """THE CONTROL for the controls. Without it every check above passes on a
    guard that refuses everything, which would make the suite unmaintainable
    and the allowlist meaningless."""
    names = {name for name, _ in hits_in(benign)}
    assert shape not in names, (shape, names, hits_in(benign))


def test_the_member_token_shape_survives_percent_encoding():
    """THE DEFECT THAT LET A REAL MEMBER URN SIT AT HEAD.

    ``\\bACoAA...`` cannot match ``%3AACoAA...``: the trailing ``A`` of the
    percent-encoded colon is a word character, so the boundary never fires --
    and percent-encoded is the form LinkedIn actually serves. All three
    spellings must match now.
    """
    body = "ACoAAZz9Yy8Xx7Ww6Vv5Uu4Tt3Ss2Rr1Qq0Pp"
    for spelling in (body, f"urn:li:fsd_profile:{body}", f"urn%3Ali%3Afsd_profile%3A{body}"):
        assert MEMBER_TOKEN_SHAPE.search(spelling), spelling
    # And the boundary version genuinely could not -- the reason, pinned.
    assert not re.compile(r"\bACoAA[A-Za-z0-9_-]{20,}").search(
        f"urn%3Ali%3Afsd_profile%3A{body}"
    )


def test_a_failure_never_prints_the_identifier():
    """A CI log is a publication channel."""
    value = "ACoAAZz9Yy8Xx7Ww6Vv5Uu4Tt3Ss2Rr1Qq0Pp"
    rendered = redact(value)
    assert value not in rendered
    assert rendered.startswith("AC") and rendered.endswith("chars>")
    assert len(rendered) < len(value)


def test_the_name_gap_is_stated_where_a_reader_will_see_it():
    """The most important sentence in this module, asserted so an edit that
    deletes it fails rather than quietly widening what green means."""
    doc = __doc__ or ""
    assert "NAMES HAVE NO SHAPE" in doc
    assert "no third-party PII" in doc


# ---------------------------------------------------------------------------
# 2. The shape of a key
# ---------------------------------------------------------------------------

#: A string shorter than this is not evidence of anything.
MIN_MEANINGFUL = 5
#: Two strings can line up by accident; three rows of the same shape is a table.
MIN_KEY_ROWS = 3


def fixture_blob() -> str:
    """Every committed fixture, concatenated once.

    The fixtures are the PUBLIC half by definition. That is what makes them the
    right thing to test a table against: a value in here is not a secret, and a
    value paired with one is the secret it replaced.
    """
    parts = []
    for path in sorted(FIXTURE_DIR.glob("*.html")):
        parts.append(path.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(parts)


def _string_rows(node: ast.AST) -> list[list[str]]:
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

    The rule, stated as the leak itself would have tripped it:

        a row is a PRE-IMAGE when one of its strings appears in a committed
        fixture and another does not.

    Both-sides-present is fine and is what a scrubbed table looks like: an
    invented name beside its invented id reveals nothing a reader cannot
    already see in the fixture. Neither-side-present is an ordinary lookup
    table about LinkedIn, not about him -- which is why this does NOT fire on
    an HTTP-header dict the way a looks-real heuristic does.
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


def test_no_tracked_file_pairs_fixture_content_with_anything_else():
    """THE ONE THAT WOULD HAVE CAUGHT IT, and the one that found a second key.

    Run against the state before the scrub it fires on ``FOLLOWED_PAGES`` --
    twenty rows each pairing an invented Page name that IS in
    ``manage_pages_following.html`` with a real name that is not.
    """
    blob = fixture_blob()
    assert len(blob) > 100_000, "the fixtures did not load; this would pass on nothing"

    found: dict[str, list[tuple[str, int]]] = {}
    for rel in sweepable():
        if not rel.endswith(".py"):
            continue
        offenders = key_shaped_tables(
            (REPO / rel).read_text(encoding="utf-8", errors="replace"), blob
        )
        if offenders:
            found[rel] = offenders
    assert found == {}, found


def test_that_detector_fires_on_the_shape_it_was_written_for():
    """THE CONTROL, reconstructed from INVENTED values only."""
    blob = fixture_blob()
    in_fixtures = "Ashgrove Systems"
    assert in_fixtures in blob, "fixture content changed; pick another"

    source = "PAGES = [\n" + "".join(
        f"    ('Real Company {n} Ltd', {in_fixtures!r}),\n" for n in range(3)
    ) + "]\n"
    offenders = key_shaped_tables(source, blob)
    assert offenders and offenders[0][0] == "PAGES", offenders


def test_the_detector_does_not_fire_on_a_table_that_reveals_nothing():
    """An invented name beside its invented id is not a key: both halves are
    already visible in the fixture. Neither is a lookup table about the
    platform -- which is why an HTTP-header dict stays quiet."""
    blob = fixture_blob()
    both_sides = "PAGES = [\n" + "".join(
        "    ('Ashgrove Systems', 'Ashgrove Systems'),\n" for _ in range(4)
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
# 3. The spelling expansion, which is why a literal list is not enough
# ---------------------------------------------------------------------------


def test_a_phrase_is_hunted_in_its_url_spellings_too():
    """The defect that let a real job title through a 69/69 PASS.

    The forbidden list held the spaced spelling; the ATS apply link in the same
    file spelled it with hyphens. Driven on a synthetic phrase, so this test
    names no real title.

    THE MEASURED COST OF THE LITERAL APPROACH, since it is the argument for
    every shape above: scrubbing ONE city took three passes. Each pass replaced
    the spelling it could see and reported clean; the next found another -- the
    full form, the bare city, then the bare city inside an assertion written to
    match the input the previous pass had just changed.
    """
    spellings = url_spellings("Some Real Job Title")
    assert "Some Real Job Title" in spellings
    assert "Some-Real-Job-Title" in spellings
    assert "Some%20Real%20Job%20Title" in spellings
    assert "SomeRealJobTitle" in spellings
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
