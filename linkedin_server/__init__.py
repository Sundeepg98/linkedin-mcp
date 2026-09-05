"""linkedin: an MCP window onto the operator's own LinkedIn account.

Reads his profile views, applications, saved jobs, job search, profile and
notifications through his own signed-in browser.

IT ALSO WRITES, and this docstring denied that for a day after it stopped
being true. It said "a strictly read-only MCP window" and "There is no write
path in this package". The package docstring is the first thing a reader
trusts and was the last thing updated, which is the whole reason this sentence
names the correction instead of quietly replacing it.

**AND THEN IT WENT STALE AGAIN, IN THE SAME DIRECTION, MEASURED 2026-09-05.**
It said *"Three write tools ship: save, unsave and unfollow"* and *"exactly
ONE mutating call exists in the package"*. Measured off the live registry and
off ``readonly.SANCTIONED_MUTATIONS``:

    write tools            12   (this docstring said 3)
    sanctioned mutations    5   (this docstring said 1)

**THIS PARAGRAPH IS THE POINT AND THE NUMBERS ARE NOT.** The sentence above
diagnoses its own failure mode correctly -- *the first thing a reader trusts
and the last thing updated* -- and then the file repeated it, because the
remedy chosen was to write a better sentence rather than to build something
that would notice. `server.py`'s module docstring carries the same counts and
IS pinned: a test reads those words and fails when they disagree with the
registry. **This docstring is pinned by nothing, and neither is `README.md`'s
opening headline, which was found stale by nine tools in the same hour.** The
two highest-traffic count claims in the repository are the two unguarded ones.

It was stale in the direction that matters: understating the write surface by
NINE TOOLS, five of which are irreversible.

WHAT IS TRUE, measured rather than remembered: twelve write tools ship, five
sanctioned mutating calls exist, writes are off unless a per-process flag is
set, and every write needs a single-use token from its own preview. See
``writes.py``, and prefer ``server.py``'s docstring over this one for counts,
because that one is checked.
"""

from linkedin_server.config import SERVER_NAME, SERVER_VERSION

__all__ = ["SERVER_NAME", "SERVER_VERSION", "__version__"]
__version__ = SERVER_VERSION
