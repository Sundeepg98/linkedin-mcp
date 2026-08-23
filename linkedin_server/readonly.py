"""The read-only invariant, written down as something that can fail.

"Read-only by design" is a claim. This module is the executable version of it,
in four parts:

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

4. **A launch boundary.** :func:`assert_launch_flags_permitted` and
   :func:`scan_source_for_evasion` hold the line on HOW the browser is
   started: two sanctioned Chromium flags, and no anti-detection library
   pulled in through the back door. ``browser.py`` runs the first of those
   before every launch, so it binds at runtime and not only in the tests.

The guarantee those four buy: this server can open a fixed set of LinkedIn's
own read pages in the operator's browser and read what rendered. It has no
code path that clicks, types, submits a form, or issues a non-GET request,
and it reaches LinkedIn as the ordinary Chrome it is.
"""

from __future__ import annotations

import re
from typing import Iterable

from linkedin_server.errors import WriteAttemptError

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
    # The job tracker, which is where /my-items/saved-jobs/ now redirects (the
    # cardType query is dropped on the way, and that older address is no longer
    # on this list because nothing builds it any more). ``?stage=`` selects
    # which of his own lists renders. It is a read: measured 2026-08-22 by
    # opening three stages in turn and re-reading the default view afterwards,
    # where every tab count was unchanged. The tab strip itself is a set of
    # client-side radios with no url of their own, so ``?stage=`` is the ONLY
    # way to reach the applied list without clicking -- which is exactly why
    # this pattern exists rather than a click.
    #
    # The two stages are ENUMERATED rather than left as ``?[^#]*``. LinkedIn's
    # own payload also names interview, archived, draft and clicked_apply, and
    # a wildcard would have admitted all of them plus ``?stage=withdraw`` and
    # ``?apply=1`` -- unreachable today, since the stage is a literal in
    # server.py and never a tool argument, but an allowlist should permit what
    # is opened rather than what happens to be harmless. A third stage needs a
    # deliberate edit here, which is the point.
    re.compile(
        r"^https://www\.linkedin\.com/jobs-tracker/\?stage=(saved|applied)$"
    ),
    # Job search results.
    re.compile(r"^https://www\.linkedin\.com/jobs/search/?(\?[^#]*)?$"),
    # ONE job posting, addressed by its numeric id and nothing else.
    #
    # No query string is permitted here, unlike every other pattern on this
    # list. LinkedIn hangs tracking parameters off its own job links
    # (``?refId=``, ``?trackingId=``, ``?eBP=``) and a real posting url in the
    # wild carries them, so admitting ``\?[^#]*`` would look like the
    # neighbourly thing to do. It is not: this server BUILDS the url from an
    # integer, so it never has a query to preserve, and a pattern that accepts
    # one is a pattern that accepts whatever a caller appends.
    #
    # The slug form LinkedIn also serves --
    # ``/jobs/view/senior-node-engineer-at-acme-4600000042`` -- is refused for
    # the same reason. A slug is a job TITLE, which is a string, and a string
    # in a url is the thing an allowlist exists to prevent. The numeric id is
    # the whole of what identifies a posting, and ``dom.JOB_HREF`` already
    # captures exactly that group out of either form.
    re.compile(r"^https://www\.linkedin\.com/jobs/view/\d{6,}/?$"),
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

    # Whitespace is refused up front, before any pattern sees the string.
    # Python's ``$`` matches before a trailing newline and ``[^#]*`` happily
    # eats a CRLF, so every anchored pattern below would otherwise accept
    # "https://www.linkedin.com/feed/\n" and a query carrying "\r\nHost: ...".
    # No caller can build such a string today; this closes the shape rather
    # than the instance.
    if any(character.isspace() for character in url):
        raise WriteAttemptError(
            f"navigation blocked: {url!r} contains whitespace. A url this "
            "server builds never does, and a newline inside one is how an "
            "anchored pattern is talked past."
        )

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
    # Added 2026-08-23 with the negation prefixes below: without the base verb
    # on this list, "unsubscribe" cannot be reached by stripping "un".
    "subscribe",
)

#: Prefixes that NEGATE a verb without stopping it being a write.
#:
#: MEASURED 2026-08-23. ``name_implies_write`` split a tool name into segments
#: and looked each up in :data:`WRITE_VERBS`, which holds ``save`` and
#: ``follow`` but held no negated form at all. So every one of these read as
#: NOT-A-WRITE:
#:
#:     linkedin_unsave_job   linkedin_unfollow   linkedin_unlike
#:     linkedin_unsubscribe  linkedin_disconnect
#:
#: **Undoing a write is still a write.** They were caught only because somebody
#: had hand-listed two of them in the tool-surface test's ``FORBIDDEN_TOOLS``,
#: which is the failure this module exists to avoid: a literal list sees the
#: instances someone remembered, and the generalising check cannot see the
#: CLASS.
#:
#: Verified against every live tool when this landed: all five are now caught
#: and NONE of the thirteen read tools became a false positive.
NEGATION_PREFIXES: tuple[str, ...] = ("un", "dis", "de")

#: THE RESIDUE, stated rather than left for someone to rediscover.
#:
#: 1. ``re`` is NOT in the set above, and that is a judgement rather than an
#:    oversight. It would correctly catch ``reset``, ``resend``, ``reapply``,
#:    ``repost`` and ``reconnect`` -- all genuine writes -- but it also turns
#:    ``remark`` into ``re`` + ``mark``, and a guard that cries wolf on an
#:    ordinary English word is a guard somebody switches off. Revisit only with
#:    a real ``re``-prefixed tool to justify it.
#: 2. This rule generalises over NEGATIONS OF KNOWN VERBS, not over unknown
#:    verbs. ``linkedin_boost_profile`` or ``linkedin_publish`` would still
#:    pass, because ``boost`` and ``publish`` are on no list. :data:`WRITE_VERBS`
#:    remains a hand-kept list at its root and the only honest fix for that is
#:    to keep adding to it.


def _segments_that_are_write_verbs(text: str) -> set[str]:
    """Every segment of ``text`` that is a write verb, negated or plain.

    One implementation shared by the name check and the docstring check, so the
    two can never drift into disagreeing about what a write verb is.
    """
    found: set[str] = set()
    for segment in re.split(r"[^a-z]+", text.lower()):
        if not segment:
            continue
        if segment in WRITE_VERBS:
            found.add(segment)
            continue
        for prefix in NEGATION_PREFIXES:
            if segment.startswith(prefix) and segment[len(prefix) :] in WRITE_VERBS:
                found.add(segment)
                break
    return found


def name_implies_write(name: str) -> bool:
    """True if a tool name contains a write verb as a whole word segment.

    A NEGATED write verb counts: ``linkedin_unsave_job`` advertises a mutation
    exactly as loudly as ``linkedin_save_job`` does.
    """
    return bool(_segments_that_are_write_verbs(name))


def iter_write_verbs_in(text: str) -> Iterable[str]:
    """Yield write verbs appearing as whole words in ``text``, negations too."""
    yield from sorted(_segments_that_are_write_verbs(text))


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

#: Every spelling a docstring could make a write claim in: the plain verbs and
#: their negated forms. ``\bsubscribe\b`` does not match inside
#: ``unsubscribe`` -- there is no word boundary between the two halves -- so
#: without this the docstring check carried the same blind spot the NAME check
#: did, and "this tool will unfollow the company" read as a claim about
#: nothing. Sorted longest-first so a negated form is reported as itself rather
#: than as the bare verb hiding inside it.
_CLAIMABLE_VERBS: tuple[str, ...] = tuple(
    sorted(
        set(WRITE_VERBS)
        | {
            prefix + verb
            for verb in WRITE_VERBS
            for prefix in NEGATION_PREFIXES
        },
        key=lambda word: (-len(word), word),
    )
)


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
    for verb in _CLAIMABLE_VERBS:
        for match in re.finditer(rf"\b{re.escape(verb)}\b", lowered):
            window_start = max(0, match.start() - _NEGATION_WINDOW)
            window = lowered[window_start : match.start()]
            if any(negator in window for negator in _NEGATORS):
                continue
            context = lowered[window_start : match.end() + 30].strip()
            claims.append((verb, context))
    return claims


# ---------------------------------------------------------------------------
# 4. The launch boundary
# ---------------------------------------------------------------------------

#: The flag NAMES this server may hand Chromium, with their values stripped
#: off. The complete list it actually passes is ``config.LAUNCH_ARGS``; this
#: is the gate that list has to get through, and
#: ``tests/test_launch_boundary.py`` puts it through it.
#:
#: Two flags, and the reason the line is drawn immediately after them:
#:
#: * ``--disable-blink-features=AutomationControlled`` switches off the one
#:   Blink feature that sets ``navigator.webdriver = true``. Without it the
#:   browser announces on every page load that it is automated, and LinkedIn
#:   will not complete a sign-in. It flips one boolean. The browser still
#:   reports the user agent, platform, canvas, font list and timezone of the
#:   Chrome it actually is.
#: * ``--remote-debugging-port`` opens the DevTools port on 127.0.0.1 that
#:   the recovery path attaches to (``cdp_bridge.py``).
#:
#: Anything past those two is a different activity rather than a bigger
#: version of the same one: a stealth plugin, a spoofed user agent or
#: platform, a patched canvas/WebGL/font/audio fingerprint, a proxy,
#: randomised "human-like" delays, a captcha solver. This server does none of
#: them. The check exists because whoever reaches for one will be fixing a
#: real failure at the time, and this boundary should be something they have
#: to raise with the operator rather than something a reviewer has to happen
#: to notice in a diff.
PERMITTED_LAUNCH_FLAGS: tuple[str, ...] = (
    "--disable-blink-features",
    "--remote-debugging-port",
)

#: The only Blink feature that may be switched off. The flag takes a
#: comma-separated LIST and can disable arbitrary web-platform behaviour, so
#: permitting the flag NAME is not enough: this one value is sanctioned, and
#: every other value -- including this one with anything appended to it -- is
#: not.
_PERMITTED_BLINK_FEATURE = "AutomationControlled"


def assert_launch_flags_permitted(args: Iterable[str]) -> None:
    """Return quietly if every launch flag is permitted, else raise.

    Args:
        args: the arguments as handed to Chromium -- ``config.LAUNCH_ARGS``
            in practice. Each entry is ``--name`` or ``--name=value``.

    Raises:
        WriteAttemptError: an argument's name is not in
            :data:`PERMITTED_LAUNCH_FLAGS`, or ``--disable-blink-features``
            carries a value other than ``AutomationControlled``. It is the
            same error the navigation allowlist raises, for the same reason:
            this server was asked to do something it has no business doing,
            and the only correct outcome is a loud stop.
    """
    for arg in args:
        name, _, value = str(arg).partition("=")
        if name not in PERMITTED_LAUNCH_FLAGS:
            raise WriteAttemptError(
                f"launch flag {name!r} is not permitted. This server passes "
                f"exactly {len(PERMITTED_LAUNCH_FLAGS)} Chromium flags -- "
                f"{', '.join(PERMITTED_LAUNCH_FLAGS)} -- and nothing else: "
                "no stealth plugin, no user-agent or platform spoofing, no "
                "fingerprint patching, no proxy, no captcha solver. That is "
                "a deliberate boundary, so widening it is the operator's "
                "call to make and not a code review's."
            )
        if name == "--disable-blink-features" and value != _PERMITTED_BLINK_FEATURE:
            raise WriteAttemptError(
                f"launch flag {name!r} may switch off "
                f"{_PERMITTED_BLINK_FEATURE!r} and nothing else, not "
                f"{value!r}. That one feature is what sets "
                "navigator.webdriver, and turning it off is the difference "
                "between a sign-in completing and being refused; the same "
                "flag can disable arbitrary Blink behaviour, which is a "
                "different thing and needs the operator's say-so, not a "
                "code review's."
            )


def _import_pattern(*packages: str) -> re.Pattern[str]:
    """Compile a pattern matching an import statement for any of ``packages``.

    Anchored to the start of a line under ``re.MULTILINE``, so it fires on
    ``import x`` and on ``from x import y`` and on nothing else. A package
    named in a sentence, a docstring or a comment is prose, and prose is not
    a dependency.
    """
    names = "|".join(re.escape(package) for package in packages)
    return re.compile(rf"^\s*(?:import|from)\s+(?:{names})\b", re.MULTILINE)


#: Anti-detection libraries, matched on the IMPORT LINE ONLY. Pulling one of
#: these in would cross the boundary above in a second way -- not through a
#: flag but through a dependency -- so it gets its own scan, run over every
#: module of this package by ``tests/test_launch_boundary.py``.
#:
#: Anchoring on ``import``/``from`` rather than on a bare substring is
#: load-bearing, not tidiness: this package says out loud, in this very
#: module, that it does not use a stealth plugin and does not spoof a user
#: agent. A substring check would make documenting the boundary impossible,
#: which is a worse outcome than not checking at all.
EVASION_IMPORT_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "stealth",
        _import_pattern(
            "playwright_stealth", "selenium_stealth", "puppeteer_stealth"
        ),
    ),
    ("undetected", _import_pattern("undetected_chromedriver")),
    (
        "captcha",
        _import_pattern("twocaptcha", "2captcha", "anticaptcha", "capsolver"),
    ),
    ("useragent_spoofing", _import_pattern("fake_useragent", "user_agents")),
    ("tls_spoofing", _import_pattern("curl_cffi", "tls_client")),
    ("fingerprint", _import_pattern("browserforge", "fingerprint_suite")),
)


def scan_source_for_evasion(source: str) -> list[tuple[int, str, str]]:
    """Return ``(line_number, label, line)`` for every evasion import found.

    Three kinds of line are skipped -- the same three
    :func:`scan_source_for_mutations` skips, and for the same reason, since
    the table above is built out of the very package names being hunted:

    * comments;
    * ``re.compile(...)`` lines;
    * any line ending in ``# readonly-ok``, so a genuine false positive is
      waived visibly in the diff rather than by quietly loosening a pattern.

    The fourth skip in :func:`scan_source_for_mutations` -- a line that is
    nothing but a quoted string -- is not repeated here because it cannot
    matter: these patterns match an import STATEMENT, and a bare literal is
    never one.
    """
    hits: list[tuple[int, str, str]] = []
    for lineno, line in enumerate(source.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if "re.compile(" in stripped:
            continue
        if stripped.endswith("# readonly-ok"):
            continue
        for label, pattern in EVASION_IMPORT_PATTERNS:
            if pattern.search(line):
                hits.append((lineno, label, stripped))
                break
    return hits
