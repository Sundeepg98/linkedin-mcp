"""The read-only invariant, written down as something that can fail.

"Read-only by design" is a claim. This module is the executable version of it,
in three parts:

1. **A navigation allowlist.** :func:`assert_read_url` is the only door to
   ``page.goto``. Every url this server may open is enumerated below as a
   pattern. A keyword the operator types cannot become a navigation to an
   action url, because the built url has to match one of these first.

2. **A source scanner.** :func:`scan_source_for_mutations` greps this package
   for the Playwright calls that could change something -- clicking, typing,
   submitting, non-GET requests. ``tests/test_readonly.py`` runs it over every
   module in the package AND over a deliberately bad sample, so the check is
   shown catching something rather than merely passing.

3. **A verb list.** :data:`WRITE_VERBS` is what the tool-surface test uses to
   assert that no tool name or docstring implies a mutation.

The guarantee those three buy: this server can open a fixed set of LinkedIn's
own read pages in the operator's browser and read what rendered. It has no
code path that clicks, types, submits a form, or issues a non-GET request.
"""

from __future__ import annotations

import re
from typing import Iterable

from linkedin_own_server.errors import WriteAttemptError

# ---------------------------------------------------------------------------
# 1. Navigation allowlist
# ---------------------------------------------------------------------------

#: Every url this server is permitted to open, as an anchored pattern.
#: Query strings are allowed only where a read surface genuinely needs them
#: (job search filters, the saved/applied card type).
_ALLOWED_URL_PATTERNS: tuple[re.Pattern[str], ...] = (
    # Own profile views (Premium analytics view, and the classic one).
    re.compile(r"^https://www\.linkedin\.com/analytics/profile-views/?(\?[^#]*)?$"),
    re.compile(r"^https://www\.linkedin\.com/me/profile-views/?(\?[^#]*)?$"),
    # Saved / applied jobs. cardType selects which list renders; both are reads.
    re.compile(r"^https://www\.linkedin\.com/my-items/saved-jobs/?(\?[^#]*)?$"),
    # Job search results.
    re.compile(r"^https://www\.linkedin\.com/jobs/search/?(\?[^#]*)?$"),
    # Own profile. /in/me/ redirects to whoever is signed in.
    re.compile(r"^https://www\.linkedin\.com/in/me/?$"),
    re.compile(r"^https://www\.linkedin\.com/in/[A-Za-z0-9\-_%]+/?$"),
    re.compile(
        r"^https://www\.linkedin\.com/in/[A-Za-z0-9\-_%]+/details/"
        r"(skills|experience|education)/?(\?[^#]*)?$"
    ),
    # Notifications list.
    re.compile(r"^https://www\.linkedin\.com/notifications/?(\?[^#]*)?$"),
    # Feed, used only as a corroborating auth measurement.
    re.compile(r"^https://www\.linkedin\.com/feed/?$"),
    # The login page, opened for the operator to sign in himself.
    re.compile(r"^https://www\.linkedin\.com/login/?(\?[^#]*)?$"),
)

#: Substrings that must never appear in a navigation target, checked before
#: the allowlist as a second, independent gate. Belt and braces: a future
#: pattern edited too loosely still cannot reach these.
_FORBIDDEN_URL_SUBSTRINGS: tuple[str, ...] = (
    "/jobs/application",
    "easyapply",
    "easy-apply",
    "/messaging",
    "/invite",
    "invitation",
    "/connect",
    "/follow",
    "/unfollow",
    "/endorse",
    "/post/",
    "/feed/update",
    "sharing/share",
    "/settings/",
    "opentowork",
    "open-to-work",
    "/edit/",
    "action=",
    "/delete",
    "/withdraw",
)


def assert_read_url(url: str) -> str:
    """Return ``url`` if it is a permitted read surface, else raise.

    Raises:
        WriteAttemptError: the url is not on the allowlist, or contains a
            forbidden substring. Callers must not catch this and continue --
            it means a navigation was attempted that this server has no
            business making.
    """
    if not isinstance(url, str) or not url:
        raise WriteAttemptError("empty navigation target")

    lowered = url.lower()
    for bad in _FORBIDDEN_URL_SUBSTRINGS:
        if bad in lowered:
            raise WriteAttemptError(
                f"navigation blocked: {url!r} contains {bad!r}, which is not a "
                "read surface. This server has no write path; if you reached "
                "this, a url was built wrong."
            )

    for pattern in _ALLOWED_URL_PATTERNS:
        if pattern.match(url):
            return url

    raise WriteAttemptError(
        f"navigation blocked: {url!r} is not on the read-only allowlist. "
        "Add a pattern to readonly._ALLOWED_URL_PATTERNS only if the target "
        "is genuinely a page that displays the operator's own data."
    )


def is_read_url(url: str) -> bool:
    """Non-raising form of :func:`assert_read_url`."""
    try:
        assert_read_url(url)
    except WriteAttemptError:
        return False
    return True


# ---------------------------------------------------------------------------
# 2. Source scanner
# ---------------------------------------------------------------------------

#: Playwright (and requests) calls that can change state. Matched against the
#: package source. ``page.goto``, ``page.content``, ``inner_text``, ``locator``
#: and ``request.get`` are all absent from this list on purpose: they read.
_MUTATION_CALL_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("click", re.compile(r"\.click\s*\(")),
    ("dblclick", re.compile(r"\.dblclick\s*\(")),
    ("fill", re.compile(r"\.fill\s*\(")),
    ("type_text", re.compile(r"\.type\s*\(")),
    ("press", re.compile(r"\.press\s*\(")),
    ("check", re.compile(r"\.(check|uncheck)\s*\(")),
    ("select_option", re.compile(r"\.select_option\s*\(")),
    ("set_input_files", re.compile(r"\.set_input_files\s*\(")),
    ("drag", re.compile(r"\.drag_to\s*\(")),
    ("tap", re.compile(r"\.tap\s*\(")),
    ("dispatch_event", re.compile(r"\.dispatch_event\s*\(")),
    ("form_submit", re.compile(r"\.(submit|form_submit)\s*\(")),
    ("http_post", re.compile(r"\.(post|put|patch|delete|fetch)\s*\(")),
    ("keyboard", re.compile(r"\.keyboard\b")),
    ("mouse", re.compile(r"\.mouse\b")),
    # evaluate() runs code inside the page and COULD mutate. The handful of
    # read-only harvesters in dom.py waive it with a trailing
    # ``# readonly-ok``, which means any NEW evaluate call fails this check
    # until somebody deliberately waives it in a reviewable diff.
    ("evaluate", re.compile(r"\.evaluate\w*\s*\(")),
    ("add_init_script", re.compile(r"\.add_init_script\s*\(")),
    ("route", re.compile(r"\.route\s*\(")),
)


#: A line consisting only of a quoted string, optionally with a trailing
#: comma: a token-table entry, never a call.
_BARE_STRING_LINE = re.compile(r"""(['"])(?:(?!\1).)*\1,?""")


def scan_source_for_mutations(source: str) -> list[tuple[int, str, str]]:
    """Return ``(line_number, kind, line)`` for every mutating call found.

    Four kinds of line are skipped, and the first three exist because this
    module's own tables are made of the very strings being hunted, so the
    scanner would otherwise always find itself:

    * comments;
    * ``re.compile(...)`` lines;
    * lines that are nothing but a quoted string (a token-table entry) -- a
      bare literal is data, and data cannot call anything;
    * any line ending in ``# readonly-ok``, so a genuine false positive is
      waived visibly in the diff rather than by quietly weakening a pattern.
    """
    hits: list[tuple[int, str, str]] = []
    for lineno, line in enumerate(source.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if "re.compile(" in stripped:
            continue
        if _BARE_STRING_LINE.fullmatch(stripped):
            continue
        if stripped.endswith("# readonly-ok"):
            continue
        for kind, pattern in _MUTATION_CALL_PATTERNS:
            if pattern.search(line):
                hits.append((lineno, kind, stripped))
                break
    return hits


# ---------------------------------------------------------------------------
# 2b. The injected JavaScript
# ---------------------------------------------------------------------------

#: This server injects a small amount of JavaScript to read the rendered DOM
#: (``dom.py``). Injected code is the one place where "we only call read
#: methods in Python" stops being a sufficient argument, so the JS gets its
#: own scan: any token that could change the page, submit something, or issue
#: a request fails the check.
JS_MUTATION_TOKENS: tuple[str, ...] = (
    ".click(",
    ".submit(",
    ".focus(",
    ".blur(",
    "dispatchEvent",
    "setAttribute",
    "removeAttribute",
    "innerHTML =",
    "outerHTML =",
    ".value =",
    ".remove(",
    "appendChild",
    "insertBefore",
    "replaceChild",
    "fetch(",
    "XMLHttpRequest",
    "navigator.sendBeacon",
    "localStorage.setItem",
    "sessionStorage.setItem",
    "document.cookie =",
    "window.location =",
    "location.href =",
    "history.pushState",
    "eval(",
)


def scan_js_for_mutations(js: str) -> list[str]:
    """Return every mutating token found in an injected script."""
    return [token for token in JS_MUTATION_TOKENS if token in js]


# ---------------------------------------------------------------------------
# 3. Verb list for the tool-surface check
# ---------------------------------------------------------------------------

#: Verbs whose presence in a tool NAME would advertise a mutation.
WRITE_VERBS: tuple[str, ...] = (
    "apply",
    "save",
    "post",
    "send",
    "message",
    "invite",
    "connect",
    "endorse",
    "follow",
    "like",
    "comment",
    "share",
    "delete",
    "remove",
    "update",
    "edit",
    "set",
    "toggle",
    "mark",
    "withdraw",
    "submit",
    "upload",
    "create",
    "add",
    "dismiss",
    "archive",
    "accept",
    "decline",
)


def name_implies_write(name: str) -> bool:
    """True if a tool name contains a write verb as a whole word segment."""
    parts = re.split(r"[^a-z]+", name.lower())
    return any(part in WRITE_VERBS for part in parts if part)


def iter_write_verbs_in(text: str) -> Iterable[str]:
    """Yield write verbs appearing as whole words in ``text``."""
    words = set(re.findall(r"[a-z]+", text.lower()))
    for verb in WRITE_VERBS:
        if verb in words:
            yield verb


#: Words that turn a write verb into a boundary statement rather than a claim.
#: "has no way to add or remove" is exactly the sentence a read-only tool
#: SHOULD contain, so a docstring check that banned the verbs outright would
#: forbid the clearest possible documentation of the boundary.
_NEGATORS = (
    "no ",
    "not ",
    "never",
    "cannot",
    "can't",
    "without",
    "out of scope",
    "deliberately",
    "nothing",
    "none",
    "does not",
    "do not",
    "did not",
    "rather than",
    "instead of",
    "is not",
    "there is no",
)

#: How far back to look for a negator, in characters.
_NEGATION_WINDOW = 80


def docstring_write_claims(text: str) -> list[tuple[str, str]]:
    """Return ``(verb, context)`` for write verbs used as an AFFIRMATIVE claim.

    A tool docstring may say what the tool cannot do; it may not say it does
    something that changes LinkedIn. Every occurrence of a write verb is
    checked for a negator in the preceding
    :data:`_NEGATION_WINDOW` characters, and only the unnegated ones come
    back.
    """
    lowered = (text or "").lower()
    claims: list[tuple[str, str]] = []
    for verb in WRITE_VERBS:
        for match in re.finditer(rf"\b{re.escape(verb)}\b", lowered):
            window_start = max(0, match.start() - _NEGATION_WINDOW)
            window = lowered[window_start : match.start()]
            if any(negator in window for negator in _NEGATORS):
                continue
            context = lowered[window_start : match.end() + 30].strip()
            claims.append((verb, context))
    return claims
