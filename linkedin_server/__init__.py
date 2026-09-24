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

**AND IT WENT STALE A THIRD TIME, 2026-09-19, IN A NEW DIRECTION.** Not by
understating the write surface -- twelve is still twelve -- but by a count
that moved underneath this sentence. ``readonly.SANCTIONED_MUTATIONS`` went
from FIVE to SEVEN at 12:12 that day, when ``press.py``'s disclosing press
added a ``click`` and a ``press``: two real calls in a new module, not a
reclassification of anything already here. Nothing was argued about and no
line changed meaning. The number simply moved and this sentence did not.

**WHAT IS DIFFERENT THIS TIME IS THAT SOMETHING NOTICED.** The paragraph above
says this docstring "is pinned by nothing" and diagnoses the remedy as
building something that would notice rather than writing a better sentence.
That sentence is now out of date, and this is the happiest way for a claim to
go stale: ``test_the_package_docstring_agrees_about_writes_and_mutations``
reads THESE WORDS, derives the write count from the live registry and the
mutation count from ``SANCTIONED_MUTATIONS``, and went red on its own three
hours after the table moved. It is left standing above rather than edited,
because the correction is the record.

**AND A FOURTH TIME, 2026-09-23, WHERE THE GUARD WAS RIGHT AND NOBODY RAN
IT.** ``readonly.SANCTIONED_MUTATIONS`` went from seven to nine in c523769
(a decided reveal and a view switch, two presses on recorded calls) and this
sentence still said seven. The test above went red on that commit, on
schedule -- and stayed red for six commits, because the gate run on each was
chosen by hand and did not include it. The instrument worked; the selection
of instruments did not. The count is twelve now: the same lane added three
for the copy link of the operator's own post.

WHAT IS TRUE, measured rather than remembered: fifteen write tools ship,
twelve sanctioned mutating calls exist, writes are off unless a per-process
flag is set, and every write needs a single-use token from its own preview --
a token that works once, and a redeemed grant that ``perform`` will not act on
twice. (This read "fourteen write tools" until lane L5's merge of master
66aaa95, 2026-09-24, which brought ``linkedin_send_reply`` -- the fourteenth
on that lane's branch; "thirteen write tools" until lane L7's merge the same
day brought ``linkedin_mark_company_interest``; and "twelve write tools"
until 2026-09-23, when ``linkedin_follow_company_page`` shipped. The
mutating-call count moved for none of the three: each click is ``perform``'s
existing one, and ``send_reply``'s fill is ``perform``'s own too. It moved
for the live lane's five presses, above, which the lane merge of 2026-09-24
brought in.) See
``writes.py``, and prefer ``server.py``'s docstring over this one for counts,
because that one is checked.
"""

from linkedin_server.config import SERVER_NAME, SERVER_VERSION

__all__ = ["SERVER_NAME", "SERVER_VERSION", "__version__"]
__version__ = SERVER_VERSION
