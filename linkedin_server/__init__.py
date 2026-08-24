"""linkedin: an MCP window onto the operator's own LinkedIn account.

Reads his profile views, applications, saved jobs, job search, profile and
notifications through his own signed-in browser.

IT ALSO WRITES, and this docstring denied that for a day after it stopped
being true. It said "a strictly read-only MCP window" and "There is no write
path in this package". Three write tools ship: save, unsave and unfollow. The
package docstring is the first thing a reader trusts and was the last thing
updated, which is the whole reason this sentence now names the correction
instead of quietly replacing it.

What IS true, and what ``readonly.py`` enforces: exactly ONE mutating call
exists in the package, writes are off unless a per-process flag is set, and
every write needs a single-use token from its own preview. See ``writes.py``.
"""

from linkedin_server.config import SERVER_NAME, SERVER_VERSION

__all__ = ["SERVER_NAME", "SERVER_VERSION", "__version__"]
__version__ = SERVER_VERSION
