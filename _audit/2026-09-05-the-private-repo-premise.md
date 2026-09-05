# The private-repo premise: it did not fail to hold, it STOPPED holding, at 2026-08-24T17:03:32Z

**`Sundeepg98/linkedin-mcp` is a PUBLIC repository today.** Three committed audit
documents say it is private and reason from that. **They were right when they were
written**, and this file exists to say so precisely, because the obvious correction --
"the repo is public, so that reasoning was wrong" -- is itself false and was one edit away
from being written into the record.

A corrector can name what it corrects; a corrected document cannot name its corrector. So
the arrow points one way and every reader who starts at one of those claims reaches the
wrong document first. The three back-pointers below close that. What they hand the reader
is not a refutation. It is a **boundary in time**.

**CORRECTS:** `_audit/2026-08-23-measure-linkedin.md` -- its line 84 rules the remote PRIVATE on a direct gh repo view reading; that was accurate for the repository object then live, which was replaced on 2026-08-24T17:03:32Z by the public object present today, so the ruling is sound as a dated reading and must not be carried forward as a description of this repository.

**CORRECTS:** `_audit/2026-08-24-out-of-scope-wave.md` -- not its fact but its scope: its line 724 blames the Actions allowance on this private repo for three zero-step CI failures, and those runs are ~9 hours older than the public repository object that exists today, so the allowance reasoning applied to the predecessor and cannot be read as pricing anything here.

**CORRECTS:** `_audit/2026-08-24-perform-save-unsave.md` -- not its fact but its scope: its line 199 withholds a push partly because it spends metered runner minutes on a private repo, which was true of the predecessor object it was measuring; that object was replaced on 2026-08-24T17:03:32Z and runner minutes are free on the public one.

No document was rewritten. All three claim lines are byte-identical; each file gained one
marker line beneath its claim paragraph and nothing else. The sentences that carried the
premise are the most useful evidence these files hold -- they are how the propagation can
be seen at all.

## The measurement that decides it, and it does not depend on any SHA mapping

    $ gh repo view --json name,isPrivate,visibility,nameWithOwner
    {"isPrivate":false,"name":"linkedin-mcp",
     "nameWithOwner":"Sundeepg98/linkedin-mcp","visibility":"PUBLIC"}

    $ gh api repos/Sundeepg98/linkedin-mcp --jq '{created_at,visibility}'
    {"created_at":"2026-08-24T17:03:32Z","visibility":"public"}

    $ gh api repos/Sundeepg98/linkedin-mcp/actions/runs --jq '.total_count'
    79
    $ ... --jq '[.workflow_runs[].created_at] | sort | .[0:3]'
    ["2026-08-24T17:03:45Z","2026-08-24T17:03:49Z","2026-08-24T18:43:37Z"]

All read-only, 2026-09-05, VERIFIED-BY-INSTRUMENT.

**THE REPOSITORY OBJECT SERVING THIS CODE WAS CREATED AT 2026-08-24T17:03:32Z**, and its
entire Actions history begins thirteen seconds later. Local history, by contrast, starts
at `2026-08-21T10:27:38+05:30` and runs to 432 commits. The commits are three days older
than the repository that holds them.

**So any CI run either August document describes, earlier in that day than 17:03:45Z, did
not happen on this repository.** Two independent confirmations, neither needing the
dead-to-live SHA mapping:

* `2026-08-24-perform-save-unsave.md` cites run **32661307599** as its evidence.
  `gh api repos/Sundeepg98/linkedin-mcp/actions/runs/32661307599` returns **HTTP 404**.
  That run id does not belong to this repository.
* `2026-08-24-out-of-scope-wave.md` tabulates a green run at **07:19** and its three
  failures at **08:04, 08:14, 08:15** -- all earlier the same day than this repository's
  first run at 17:03:45Z.

Corroborating, and reproducible from `git log` alone once the mapping supplies the live
SHAs: those three failures land on commits dated `13:34`, `13:44` and `13:45` IST
(UTC+5:30), matching the audit's three UTC times **to the minute, three for three**. The
mapping itself lives in an untracked working note, so it is named as corroboration rather
than as the argument.

## When it changed, visible in this repository's own history

The repository object was created at `2026-08-24T17:03:32Z`, which is **22:33:32 IST**.
The two commits immediately before that instant are:

    fdb108e  2026-08-24T22:17:37+05:30  fix(privacy): stop the repository stating his
                                        employment situation
    b20791a  2026-08-24T22:21:25+05:30  docs: add LICENSE -- proprietary, published to be
                                        read rather than run

A privacy pass and a licence describing the work as *published to be read* land twelve and
sixteen minutes before a public repository object appears. **That is the going-public
event, on the record, in this repository's own log.** Nothing here needed to be inferred
from the absence of the old object.

## What this means for each document

### `_audit/2026-08-23-measure-linkedin.md`

Its line 84 is the head of the chain, and it is the strongest-sounding statement of the
premise anywhere in the corpus: it is labelled a correction, it names `gh repo view
--json visibility` as its instrument, and it overrules three agents who had inferred
"public" from a remote existing and a push working. **Its method was right and its reading
was right.** The rule it states -- visibility comes from that command alone -- is the same
rule that produces PUBLIC today, against a different object.

**Nothing in it falls.** It gains only a boundary: the object it measured is gone.

### `_audit/2026-08-24-out-of-scope-wave.md`

**Stands, with its scope named.** Its PROBABLE CAUSE section reasons about the account's
metered minutes, the Linux-equivalent conversion that doubles Windows and multiplies macOS
by ten, and roughly thirteen runs this wave added. Against a private predecessor those are
the right quantities, and the section already labelled itself PROBABLE and declined to
confirm. This correction does not withdraw the hypothesis; it says the hypothesis was
about a repository that no longer exists, and so cannot be tested from here.

**Stands, untouched.** Every observation: nine cells reporting zero steps, two runs
completing in three seconds, a failing commit that changed one markdown file, the empty
step arrays, the `BlobNotFound` logs, the workflow unchanged and green forty minutes
earlier. And the list of commits recorded as UNCERTIFIED, which follows from the runs
never executing rather than from any account of why.

**One thing genuinely closes.** The runs are not merely undiagnosed, they are now
**unreachable**: they were on an object that is gone, so no future reader can settle the
cause. The open question should be closed as permanently unanswerable rather than left
looking like an errand.

### `_audit/2026-08-24-perform-save-unsave.md`

**Stands, with its scope named.** Its line 199 welds two independent reasons for not
pushing. Against the predecessor, both were sound: the push really would have spent
metered minutes, and a push really is outward-facing.

**The outward-facing half is the one that survives the boundary, and it strengthens.** A
push to a public repository publishes. **The cost half does not survive it** -- runner
minutes are free on public repositories, so on the object that exists today that reason
prices nothing.

**Unchanged.** The decision the sentence records: the author did not push, the wave lead
pushed after verifying independently, and the gap was named in a commit title rather than
quietly omitted.

## Where the premise actually did damage, and it is not in these three files

`.github/workflows/ci.yml` carried the same sentence as a **live instruction** -- "this is
a PRIVATE repository, so runner minutes come out of the account's free allowance and a
Windows minute is billed at 2x a Linux one" -- and sized the CI matrix on it. That comment
was corrected in place on 2026-09-05, and correcting it was right: a workflow comment
describes the repository the workflow runs in **now**, and now it is public.

**The distinction is the whole finding.** A dated audit entry is a reading; a workflow
comment is a standing claim. The premise did not rot in the audit documents -- it rotted
where it was carried forward unscoped, which is exactly what a live comment does by
existing. One precision on that correction's own account: it reads as though the premise
never held. It held, and stopped holding at a measurable instant.

## What this correction does not reach, so nobody re-derives it

**No code, test verdict, tool count or capability claim in any of the three documents
depends on repository visibility.** CI counts, completeness-gate output and mutation-scan
results are untouched.

**`_audit/2026-08-30-linkedin-nine.md` matches the same grep and is a different subject.**
Its line 100 rules that LinkedIn's settings index is a private surface -- the page shows
the operator his own values and tells no other party that he opened it. That concerns a
LinkedIn surface, not a repository, and nothing there reasons from anything corrected
here. Confirmed by reading the line; deliberately left alone.

**The sweep, stated so it can be re-run.** A case-insensitive grep for `private` across
every `.md` file `git ls-files` reports under `_audit/` returns the three sites corrected
above, the unrelated LinkedIn-settings site named above, and a remainder that uses the
word in unrelated senses -- private keys, private mode, private conversations, private
lists. A second grep for runner-cost vocabulary (`runner minute`, `actions allowance`,
`metered`, `linux-equivalent`, `billed at 2x`, `free allowance`, `spending limit`) adds no
further site that reasons about repository billing.
