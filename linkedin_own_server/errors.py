"""Exception types.

Every one of these exists so a failure can be reported as a failure. None of
them has a fallback that invents a plausible answer: an empty list because the
page did not render is a lie that looks exactly like an empty list because the
operator has no saved jobs, and the two must never be confusable.
"""

from __future__ import annotations


class LinkedInReaderError(Exception):
    """Base class for everything this server raises deliberately."""

    kind = "error"


class NotAuthenticatedError(LinkedInReaderError):
    """No live LinkedIn session -- measured, not guessed."""

    kind = "not_authenticated"


class AuthUnknownError(LinkedInReaderError):
    """The signed-in question could not be answered either way.

    Distinct from :class:`NotAuthenticatedError` on purpose. "I could not
    tell" collapsing into "you are signed out" is how a server ends up
    confidently telling the operator to log in again while his session is
    perfectly fine.
    """

    kind = "auth_unknown"


class BrowserUnavailableError(LinkedInReaderError):
    """Playwright is missing, or the browser died mid-call."""

    kind = "browser_unavailable"


class ExtractionFailedError(LinkedInReaderError):
    """The page loaded but nothing recognisable could be read from it.

    Carries the url so the operator can open the same page by hand and see
    what this server saw. Raised INSTEAD of returning an empty result set.
    """

    kind = "extraction_failed"

    def __init__(self, message: str, url: str = "", hint: str = ""):
        self.url = url
        self.hint = hint
        super().__init__(message)


class WriteAttemptError(LinkedInReaderError):
    """A navigation target outside the read-only allowlist was requested.

    This should be unreachable in normal operation. It exists so that a
    future edit which tries to point the browser at an action url fails
    loudly here rather than quietly changing something on LinkedIn.
    """

    kind = "write_attempt_blocked"
