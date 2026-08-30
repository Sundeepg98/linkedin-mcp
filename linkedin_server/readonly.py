"""The read-only invariant, written down as something that can fail.

"Read-only by design" is a claim. This module is the executable version of it,
in four parts:

1. **A navigation allowlist.** :func:`assert_read_url` is the only door to
   ``page.goto``. Every url this server may open is enumerated below as a
   pattern. A keyword the operator types cannot become a navigation to an
   action url, because the built url has to match one of these first.

   **THIS ALLOWLIST IS NAVIGATION-ONLY, AND THAT IS A SCOPE RATHER THAN AN
   OVERSIGHT.** Stated here explicitly on 2026-08-24 because the sentence
   above is exact and reads as broader than it is: "the only door to
   ``page.goto``" is a claim about NAVIGATIONS, and a request issued with
   ``page.request.get`` is not one. It never reaches this function.

   There is exactly one such request in the package -- ``auth.py`` asks
   ``config.ME_API`` whether the session is live, because a page load cannot
   answer that honestly -- and **it would be REFUSED by this allowlist if this
   allowlist were consulted**: ``is_read_url(ME_API)`` is ``False``. Nothing is
   wrong with the request. It is one hardcoded module constant, GET only, with
   no url a caller can influence. What was wrong until this paragraph existed
   is that a reader of this module had no way to know the path was there.

   It is covered instead by an ENUMERATION rather than by a pattern:
   ``tests/test_api_call_sites.py`` walks the package's syntax tree, pins the
   set of direct HTTP call sites to that one entry -- with its first argument
   pinned AS SOURCE TEXT -- and fails if a second appears or this one moves.
   ``linkedin_server_info`` reports it as ``direct_api_reads``.

   **Why the path was not simply added to the patterns below.** Doing that
   would move a frozen boundary structure and fire the AST invariant in
   ``tests/test_readonly_boundary_invariant.py``, in order to authorise a
   constant nobody can redirect -- buying a widened allowlist to solve a
   problem that is really a documentation gap. A boundary that states its own
   edge is worth more than one that implies a coverage it does not have.

2. **A source scanner.** :func:`scan_source_for_mutations` greps this package
   for the Playwright calls that could change something -- clicking, typing,
   submitting, non-GET requests. ``tests/test_readonly.py`` runs it over every
   module in the package AND over a deliberately bad sample, so the check is
   shown catching something rather than merely passing.

   Since 2026-08-23 the package contains exactly ONE mutating call, and the
   scanner still reports it. What changed is not the SCANNER but the POLICY
   applied to what it finds: :data:`SANCTIONED_MUTATIONS` enumerates, by
   ``(path, function, kind)``, the calls that are permitted, and
   :func:`partition_mutation_hits` splits a scan into the sanctioned and the
   rest. The measurement was deliberately left exact -- a scanner taught to
   stop seeing ``page.click`` is worth nothing, and the whole value of this
   one is that its finding is unconditional and its ALLOWLIST is the thing a
   reviewer reads.

3. **A verb list.** :data:`WRITE_VERBS` is what the tool-surface test uses to
   assert that no tool name or docstring implies a mutation.

4. **A launch boundary.** :func:`assert_launch_flags_permitted` and
   :func:`scan_source_for_evasion` hold the line on HOW the browser is
   started: two sanctioned Chromium flags, and no anti-detection library
   pulled in through the back door. ``browser.py`` runs the first of those
   before every launch, so it binds at runtime and not only in the tests.

WHAT THIS MODULE GUARANTEED UNTIL 2026-08-23, AND WHAT IT GUARANTEES NOW.
The old sentence was: *this server has no code path that clicks, types,
submits a form, or issues a non-GET request.* It was true, it was proven here
rather than asserted, and IT IS NO LONGER TRUE. Leaving it in place would have
made this module the first thing a reader trusts and the first thing that
lies to them.

What is true now, and is what the four parts above enforce:

* This server can open a fixed set of LinkedIn's own read pages in the
  operator's browser and read what rendered.
* It contains **exactly one** call that can change anything on LinkedIn: the
  click in ``writes.perform``, named in :data:`SANCTIONED_MUTATIONS`. It does
  not run unless a per-process flag is set, a human has read a confirm gate
  built from a live read, and a single-use grant is redeemed against it. See
  ``writes.py``.
* It still types nothing, submits no form, issues no non-GET request, and
  reaches LinkedIn as the ordinary Chrome it is. Read that list as what it
  says: "no non-GET request" is not "no request outside the allowlist". One
  GET goes to ``ME_API`` without passing :func:`assert_read_url` -- see part 1
  -- and enumerating what this server does not do, without naming the one
  thing it does, is how a true list misleads.

The list in :data:`SANCTIONED_MUTATIONS` is the whole of the difference, which
is why it is one line long and why widening it is a test failure rather than a
judgement call.
"""

from __future__ import annotations

import ast
import re
from typing import Iterable, Optional

from linkedin_server.errors import WriteAttemptError

# ---------------------------------------------------------------------------
# 1. Navigation allowlist
# ---------------------------------------------------------------------------

#: Every url this server is permitted to open, as an anchored pattern.
#: Query strings are allowed only where a read surface genuinely needs them
#: (job search filters, the saved/applied card type).
_ALLOWED_URL_PATTERNS: tuple[re.Pattern[str], ...] = (
    # HIS OWN MESSAGE SURFACE, added 2026-08-26 on the operator's ruling.
    #
    # Both forms are here deliberately. Asking for the first lands on the
    # second: LinkedIn redirects /messaging/ into one specific conversation
    # thread of its own choosing, measured twice. Listing only the first would
    # have meant the server routinely sitting on a url its own allowlist does
    # not cover -- true today because the landed url is not re-checked, and a
    # trap the moment anybody adds that check.
    #
    # SENDING IS STILL IMPOSSIBLE: /messaging/compose remains on the forbidden
    # substring list, which is checked BEFORE this one.
    re.compile(r"^https://www\.linkedin\.com/messaging/?(\?[^#]*)?$"),
    re.compile(
        r"^https://www\.linkedin\.com/messaging/thread/[A-Za-z0-9%\-_=]+/?(\?[^#]*)?$"
    ),
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
    # The stages are ENUMERATED rather than left as ``?[^#]*``. LinkedIn's own
    # payload also names interview, archived and clicked_apply, and a wildcard
    # would have admitted all of them plus ``?stage=withdraw`` and ``?apply=1``
    # -- unreachable today, since the stage is a literal in server.py and never
    # a tool argument, but an allowlist should permit what is opened rather
    # than what happens to be harmless. A third stage needs a deliberate edit
    # here, which is the point, and on 2026-08-26 ``draft`` was given one. Its
    # token was READ off LinkedIn's own anchors rather than guessed from the
    # tab: tests/fixtures/jobs_tracker_row.html -- tracked, so the evidence
    # survives a clone -- carries href=".../jobs-tracker/?stage=draft". The
    # two disagree, and that is the trap: the tab is LABELLED "In Progress"
    # and ADDRESSED as ``?stage=draft``, so the word on the tab is the one
    # guess that does not work. interview, archived and clicked_apply remain
    # deliberately absent -- nothing builds them.
    re.compile(
        r"^https://www\.linkedin\.com/jobs-tracker/\?stage=(saved|applied|draft)$"
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
    # The company Pages he follows -- LinkedIn calls the surface "Manage
    # Pages". Added 2026-08-23. A pure read, and the ONLY one LinkedIn offers
    # for this list: the profile's Interests section renders a Companies tab,
    # but that tab is a client-side radio with no url of its own and no href
    # anywhere in the DOM -- the same shape as the jobs-tracker tab strip,
    # except that this one has no ``?stage=``-style escape hatch. Measured by
    # loading the Interests page and finding zero candidate hrefs on it.
    #
    # No query string, for the same reason as the job posting below: nothing
    # builds one, so nothing needs to be preserved.
    #
    # RECORD THE SIBLING THAT IS NOT HERE, because the obvious later "fix" is
    # to reach for it. The PEOPLE he follows live at
    # ``/mynetwork/network-manager/people-follow/following/``, which contains
    # the substring ``/follow`` and is therefore refused by
    # :data:`_FORBIDDEN_URL_SUBSTRINGS` below before this list is even
    # consulted. The company url happens not to contain it. That is luck, not
    # design -- and the right response to the luck running out is to leave the
    # people list unread, never to shorten the forbidden list.
    re.compile(
        r"^https://www\.linkedin\.com/mynetwork/network-manager/company/?$"
    ),
    # THE SETTINGS INDEX, AND ONLY THE INDEX. Added 2026-08-30 so that
    # linkedin_surface_census can measure it; nothing else in this package
    # builds this url.
    #
    # NO QUERY STRING AND NO SUB-PATH, and the anchoring is the whole of the
    # permission. ``/mypreferences/d/`` renders a LIST OF SECTIONS. The
    # toggles live one level down, on ``/mypreferences/d/categories/<name>``,
    # and those are refused twice over: they fail this anchored pattern, and
    # they now also contain a FORBIDDEN SUBSTRING (below). A census wants the
    # index -- which sections exist, and whether a section is url-addressed or
    # a modal -- and the index is exactly what this admits.
    #
    # THE SIDE-EFFECT RULING THAT PRECEDED THIS ENTRY, since a read surface is
    # admitted here only after one. Loading the index consumes no unread
    # counter (this surface carries no badge -- unlike notifications and
    # messaging, whose badges are MEASURED to reset on load, which is why
    # neither is a census key), emits nothing another person can observe, and
    # changes no value the account holds. Where LinkedIn interposes a re-auth
    # challenge instead of serving the page, the landing url carries
    # ``/checkpoint/`` and ``config.AUTHWALL_MARKERS`` already turns that into
    # a reported failure rather than a silent half-read. Recorded in full in
    # ``_audit/2026-08-30-linkedin-nine.md``.
    #
    # WHY NOT ``/psettings/``: it is the legacy address for the same surface
    # and nothing builds it, so it is on the forbidden list instead of here.
    re.compile(r"^https://www\.linkedin\.com/mypreferences/d/?$"),
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
    # NARROWED 2026-08-26 from the blanket "/messaging", on the operator's
    # ruling that reading his own inbox is his to do. SENDING stays forbidden
    # and this is the entry that keeps it so: /messaging/compose is the
    # pre-filled composer LinkedIn opens from a job page, and nothing here may
    # reach it.
    #
    # WHY THE BLANKET ENTRY COULD NOT SIMPLY BE DROPPED, and why this is not
    # the smaller change it looks like: /messaging/ DOES NOT STAY ON A LIST.
    # Measured twice -- LinkedIn redirects it into one specific conversation
    # thread that LinkedIn, not the caller, chooses. And assert_read_url gates
    # the REQUESTED url only; the landed url is never re-checked. So leaving
    # "/messaging/thread" forbidden while permitting "/messaging/" would have
    # produced a guard that forbids a destination it knowingly delivers you
    # to -- a fiction, and a worse one than an honest permission, because the
    # next reader would trust it.
    #
    # So the thread surface is ALLOWED and the cost is stated where a caller
    # meets it, in linkedin_open_messaging's own name and docstring, rather
    # than being denied by a list that cannot enforce it.
    "/messaging/compose",
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
    # THE TWO SETTINGS ENTRIES BELOW WERE ADDED 2026-08-30, and they were
    # added because ``"/settings/"`` above was MEASURED NOT TO COVER THE
    # SURFACE IT IS NAMED FOR.
    #
    # The measurement, run against this very function rather than reasoned
    # about: ``is_read_url("https://www.linkedin.com/mypreferences/d/")`` and
    # ``is_read_url("https://www.linkedin.com/psettings/")`` were both False
    # -- but both were refused BY THE ALLOWLIST, not here. ``"/settings/"``
    # matched neither. LinkedIn moved its settings to ``/mypreferences/d/``,
    # and the legacy address is ``/psettings/``, which does not contain
    # ``"/settings/"`` because the character before ``settings/`` is a ``p``.
    # The only address the old entry ever caught is a ``/settings/`` LinkedIn
    # no longer serves.
    #
    # WHY THAT MATTERED ENOUGH TO FIX. The net refusal held, so nothing was
    # ever reachable that should not have been. What did not hold is this
    # list's stated job: it is documented above as a "second, independent
    # gate" and as "belt and braces: a future pattern edited too loosely still
    # cannot reach these". For the settings family there was no second gate at
    # all, and the allowlist has now been deliberately loosened -- the index is
    # admitted, one line up -- which is exactly the situation the backstop
    # exists for. The category pages carry the toggles; they are the part that
    # must stay unreachable however the allowlist is edited later.
    #
    # ``"/settings/"`` IS KEPT rather than replaced. It costs nothing, and an
    # address LinkedIn stopped serving is one it can start serving again.
    "/mypreferences/d/categories/",
    "/psettings/",
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
                "read surface. This is the READ door and it refuses; a write "
                "goes through assert_write_url, which is narrower still. If "
                "you reached this, a url was built wrong."
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
# 2a. The one sanctioned mutation, named
# ---------------------------------------------------------------------------

#: THE COMPLETE LIST of mutating calls this package is permitted to contain,
#: as ``(path, function, kind)``. Anything the scanner finds that is not on
#: this list is a defect, and anything on this list that the scanner does NOT
#: find is a stale entry -- ``tests/test_readonly.py`` asserts both directions,
#: so the list cannot rot in either.
#:
#: WHY A LIST AND NOT A RELAXED RULE. The scanner's value is that it is
#: unconditional: it reports every mutating call in the package, INCLUDING the
#: sanctioned one, and it would report a second. Teaching it to ignore clicks
#: in ``writes.py``, or to ignore a line wearing some new waiver comment, would
#: convert a measurement into an opinion -- and the very next click would
#: arrive wearing the same clothes as this one. So the SCAN is untouched and
#: the POLICY is this tuple, which a reviewer reads in full in one breath.
#:
#: THE TRIPLE IS THE POINT, and each of its three parts refuses something real:
#:
#: * the PATH, so a click cannot appear in ``dom.py`` or ``browser.py`` under
#:   this exemption;
#: * the FUNCTION, so a click cannot appear in a helper elsewhere in
#:   ``writes.py`` -- ``perform`` is the only function that redeems a grant --
#:   and attribution is to the INNERMOST enclosing function, so burying one in
#:   a closure inside ``perform`` does not inherit the exemption either;
#: * the KIND, so this entry buys a ``click`` and nothing else. A ``fill`` or
#:   an ``http_post`` inside ``perform`` is refused by the very list that
#:   permits the click.
SANCTIONED_MUTATIONS: tuple[tuple[str, str, str], ...] = (
    ("linkedin_server/writes.py", "perform", "click"),
    # THE SECOND ENTRY, added 2026-08-26, and it is on a READ path -- which is
    # why it is here rather than being waved through. The list is what a
    # reviewer reads, so a click that is not on it does not exist, and one
    # that is on it has to argue for itself in this comment.
    #
    # WHAT IT DOES: activates one of seven named filter pills on the messaging
    # surface. dom.MESSAGING_FILTERS is a CLOSED SET matched before any
    # selector is built, so an arbitrary string can never become a click
    # target. The permission is not "may click on that page", it is "may
    # activate one of these seven pills".
    #
    # WHY A READ PATH MAY CLICK AT ALL. Measured: all six pills are <button>
    # with no href, so the filter surface is not reachable by navigation --
    # established by READING their destinations rather than guessing a
    # ?filter= parameter. A pill SENDS NOTHING and CHANGES NOTHING on
    # LinkedIn's servers; it alters which rows are displayed. Counted by
    # EFFECT rather than by verb, which is how this family classifies
    # everything, a view filter is a read.
    #
    # And the argument that settles it: linkedin_open_messaging ALREADY opens
    # somebody's conversation and may fire a read receipt, and ships with that
    # stated as an accepted cost. Refusing the lesser act while performing the
    # greater one is backwards.
    ("linkedin_server/dom.py", "activate_messaging_filter", "click"),
)


def enclosing_function(source: str, lineno: int) -> Optional[str]:
    """Name the INNERMOST function containing ``lineno``, or ``None``.

    Innermost rather than outermost, deliberately: a nested helper is reported
    as ITSELF, so a mutating call hidden one scope down inside a sanctioned
    function does not inherit that function's exemption. Module-level code has
    no enclosing function and comes back ``None``, which no entry in
    :data:`SANCTIONED_MUTATIONS` can match.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    best: Optional[tuple[int, str]] = None
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        end = getattr(node, "end_lineno", None)
        if end is None or not node.lineno <= lineno <= end:
            continue
        # Innermost == the enclosing candidate that starts latest.
        if best is None or node.lineno > best[0]:
            best = (node.lineno, node.name)
    return None if best is None else best[1]


def partition_mutation_hits(
    module_path: str, source: str
) -> tuple[list[tuple[int, str, str]], list[tuple[int, str, str]]]:
    """Split one module's scan into ``(sanctioned, unsanctioned)``.

    ``module_path`` is the module's path RELATIVE TO THE REPO ROOT in posix
    spelling -- ``linkedin_server/writes.py``. Relative and normalised because
    an absolute path differs between this machine and each of the three CI
    cells, and an allowlist keyed on something that varies per checkout is an
    allowlist that silently stops matching.

    THE CONSERVATION PROPERTY, which is what makes this safe to introduce at
    all: ``sanctioned + unsanctioned`` is exactly what
    :func:`scan_source_for_mutations` returned, partitioned -- nothing is
    dropped and nothing is invented, so a caller can check the union. A filter
    that quietly consumed a hit would be the same defect as a scanner that
    stopped seeing one.
    """
    sanctioned: list[tuple[int, str, str]] = []
    unsanctioned: list[tuple[int, str, str]] = []
    normalised = str(module_path).replace("\\", "/").lstrip("./")
    for hit in scan_source_for_mutations(source):
        lineno, kind, _line = hit
        function = enclosing_function(source, lineno)
        if (normalised, function, kind) in SANCTIONED_MUTATIONS:
            sanctioned.append(hit)
        else:
            unsanctioned.append(hit)
    return sanctioned, unsanctioned


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
    # ADDED 2026-08-30, and it was SHOWN MISSING before it was added: on the
    # day linkedin_react_to_item was registered as a sanctioned write,
    # name_implies_write("linkedin_react_to_item") returned False. A write
    # tool whose name the write-verb guard does not recognise is the exact
    # hole this list exists to close, and it was invisible until a tool wore
    # the verb.
    #
    # MEASURED BEFORE ADDING, because this list feeds the DOCSTRING check too
    # and a verb that is also ordinary prose turns a guard into noise: across
    # every registered tool description, "react" appears as a whole word in
    # exactly ONE -- the tool named for it. Zero false positives.
    "react",
)

#: A THIRD RESIDUE, measured the same day, and the record of what was done
#: INSTEAD of widening this list -- because the first instinct was to widen it
#: and that instinct was wrong.
#:
#: ``linkedin_change_setting`` was registered on 2026-08-30 as a sanctioned
#: write, and ``name_implies_write`` returned False for it: "change" is on no
#: list. The obvious fix was to add "change" here. MEASURED FIRST: across every
#: registered tool description, "change" appears as a whole word in SIX, and
#: three of those are READS using it to describe the boundary ("has no way to
#: change anything about the posting"). Adding it would have fired the
#: DOCSTRING check -- which shares this list -- on three tools behaving
#: correctly, and a guard that cries wolf is a guard somebody switches off.
#:
#: SO THE TOOL WAS RENAMED INSTEAD, to ``linkedin_update_setting``. "update" is
#: already here, it is on the frozen conservation baseline in test_writes.py,
#: and the new name announces the write that the old one concealed. That is
#: the OPPOSITE of the rename loophole
#: ``test_a_sanctioned_write_cannot_evade_the_law_by_being_renamed`` exists to
#: close: that one is renaming so a write passes as a read, this is renaming so
#: a write stops passing as one. The guard found an under-declaring name and
#: the name was corrected, which is the guard working.
#:
#: The residue that remains is the general one, unchanged: a verb that is also
#: ordinary English cannot join this list while the name check and the
#: docstring check share it. Revisit with a segmenter that tells a verb in a
#: tool NAME from a verb in prose.

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
