# The sixty dangling: 60 was 49, and the open set was 2

**Wave:** sha-repair-sixty. **Date:** 2026-09-20. **Measured at** `800b617`,
185 tracked files under `_audit/`, and re-measured at `8b58dcb` where the
figure I was handed was taken.

I was handed a number that had already been corrected once. A census reported
**325** dangling commit citations; a sibling wave found that 280 of them were
LinkedIn Help Center article ids and handed on **60**. I was told to re-derive
it and to trust my own measurement if it disagreed.

It disagrees, twice over.

| | distinct | occurrences |
|---|---:|---:|
| handed to me as commit-shaped and dangling | 60 | 138 |
| **re-derived, same rule, same ref** | **49** | **126** |
| of those, actually cited as commits of THIS repository | **26** | -- |
| of those 26, not already repaired before my wave started | **2** | **3** |

**The open set was two tokens.** One of them was created the same day, by the
repair wave immediately before mine, in the document whose entire subject is
unresolvable citations.

**And the real population is somewhere else.** A guard built for this wave
finds **22 distinct SHAs across 29 citations that no clone can resolve**, and
only one of them is in the handed-down 60. They are not wreckage from a
history rewrite. They are commits made on `worktree-agent-*` branches by waves
that then reported their work by SHA, on branches that never merged -- so each
citation was unresolvable **from the moment it was written**. That is a live
generator, and it is still running.

---

## 1. The extraction, and the exclusion rule stated

Corpus: every tracked file under `_audit/` (185 at `800b617`; 166 at
`8b58dcb`). Token: a run of lowercase hex standing as a word.

**THE RULE I WAS HANDED WAS `^a[0-9]{6,7}$` IN THE `source` POSITION. I did
not adopt it, because it is wrong in both directions and I can show each.**

**It deletes real commits.** `a540461` and `a604394` are shaped exactly like
help-article ids and are real commit objects. `a604394` is cited as
*"**Now at 4 of 5** -- committed at `a604394`"* and does **not** resolve on
`master` -- a genuine finding the blanket exclusion swallows. `a540461` is
cited as *"Shipped `a540461` 2026-09-02, could not navigate once"* and does
resolve.

**It is also too narrow for the ids it targets.** Nine help-article ids in the
corpus are `a` + **8** digits (`a10376002`, `a14250134`, and seven more), all
sitting in the census `source` column. A `{6,7}` rule misses every one.

**And the companion "not all digits" pre-filter -- used by both censuses --
deletes signal at the same rate.** Sixteen all-digit tokens in this corpus
resolve as commits. Three of them matter:

| token | what it is |
|---|---|
| `5480246` | `jobcore`'s baseline commit, cited in `2026-08-31-jobcore-paths.md:5` |
| `5581950` | one of the SIX that `2026-09-20-the-six-unremapped.md` repaired |
| `9580360` | a **live twin** in an existing mapping table -- the repaired side |

A filter that drops a repair's own output is not removing noise.

**WHAT I USED INSTEAD.** No shape exclusion at extraction. Every token is
extracted, and **KIND is decided by SLOT** -- the column it sits in, the
grammar around it, the document it is in -- before any resolver is asked
anything. The one shape rule that survived measurement is in section 6, and it
excludes exactly one length, on a printed table of what was seen at every
length.

**THE PREDICATE, throughout:**

    git merge-base --is-ancestor <sha> master      # read by EXIT CODE only

never `git cat-file`. This repository keeps a `pre-purge-restore` tag and 80+
`worktree-agent-*` branches, so `cat-file` answers "commit" for objects no
clone can reach. Measured: the branch tip `integrate-1821` gives
`cat-file -e` exit 0 and `--is-ancestor` exit 1. A guard on `cat-file` is
green on exactly the citations that are broken.

---

## 2. Reconciliation: where 60 became 49, exactly

I re-ran the sibling wave's own rule, quoted from its text -- *"every 7-8
character lowercase-hex token standing as a word and not all digits"* -- at its
own ref, `8b58dcb`.

| tokenizer left boundary | distinct | occurrences | resolving | help-shaped dangling | **commit-shaped dangling** |
|---|---:|---:|---:|---:|---:|
| `\b` (word char) | 721 | 1,985 | 392 | 280 | **49** |
| `(?<![0-9a-zA-Z])` | **732** | **1,997** | **392** | **280** | **60** |
| *their published figures* | *732* | *1,997* | *392* | *280* | *60* |

The second row reproduces their headline to the token. **The entire difference
is one regex boundary**, and all 11 tokens it admits come from two lines:

    | `class` | `bb9bff38 _7917aabf _7ca7bc04 _7000baa9 _2e9433c3 _620e686c
      _5c9fde69 _7edff741 _84ad9c8b ea47fa53 _94f56fd5 _6ccb2f15 a1a56b0e
      _41aad4b0` | BYTE-IDENTICAL to the left column |
        _audit/_slice-unfollow-census.md:302

    ... obfuscated CSS class names (`bb9bff38 _7917aabf`), sanitised vanity
    slugs ...
        _audit/2026-09-03-hygiene-boundary-and-record.md:245

They are **LinkedIn's obfuscated CSS class-name fragments.** Python's `\b`
treats `_` as a word character, so `_7917aabf` has no boundary before the hex
and the narrow pattern skips it; a boundary written as "not alphanumeric" cuts
the `_` off and mints a fresh token. **Eleven phantom citations, from a
character class.**

The corpus had already enumerated this kind, seventeen days earlier, in the
document that built the sanitiser. `2026-09-03-hygiene-boundary-and-record.md:243`
lists it among the shapes that made a first pass report 127 dead citations
where the real count was 24: *"UUID segments, obfuscated CSS class names
(`bb9bff38 _7917aabf`), sanitised vanity slugs, sha256 prefixes and 11-digit
LinkedIn job ids."* Three censuses have now rebuilt that list independently,
none of them having read it.

---

## 3. The sixty, by KIND -- all 63 at HEAD

At `800b617` the same rule yields **63 distinct / 158 occurrences**: the 60,
plus three tokens newly cited by documents written after `8b58dcb`. Adjudicated
by reading every occurrence of every token.

| kind | distinct | how it was decided |
|---|---:|---|
| **Not commit citations at all** | **33** | slot and grammar, quoted below |
| Cross-repo commit citations, **correct** | 4 | the containing document names its repository |
| In-repo dead, **already repaired 2026-09-03** | 24 | mapping table + header note, verified in section 5 |
| In-repo dead, **open when my wave started** | **2** | section 4 |

### 3.1 The 33 that were never commit citations

| kind | n | receipt from the corpus |
|---|---:|---|
| obfuscated CSS class fragments | 14 | `\| \`class\` \| \`bb9bff38 _7917aabf ...\` \|` -- `_slice-unfollow-census.md:302` |
| UUID first segments | 9 | `componentkey="e205ae22-..."` -- `_slice-otw-census.md:58` |
| DOM component keys | 6 | `jobs.ApplyInterceptModal#4e38fb36` -- `_slice-apply-census.md:339` |
| truncated sha256 prefixes | 2 | `sha256 BEFORE 959cb67f...469ad3` -- `2026-09-05-census-hygiene.md:106` |
| sanitised vanity-slug suffix | 1 | quoted at `2026-09-03-hygiene-boundary-and-record.md:246` as an example of the slug SHAPE |
| `diff` normal-format hunk header | 1 | `119a120,124` -- `2026-09-20-the-three-held-defects.md:386` |

The last one is worth a sentence on its own. `119a120` is not an identifier of
any kind: it is the `diff` instruction *"after line 119 of file a, append lines
120-124 of file b"*, sitting in an indented diff block. It is seven lowercase
hex characters because `1`, `9`, `a`, `0` and `2` all are. **A token census
cannot see punctuation it did not tokenise.**

Two of the 33 are additionally self-convicting, and both were already settled
in writing before either census ran:

* *"`a528144` is a LinkedIn help-article id that returns HTTP 404, and
  `5db0579` is a component key."* -- `2026-09-03-hygiene-boundary-and-record.md:248`

### 3.2 The 4 cross-repo citations, and the fifth the filter hid

`2026-08-31-jobcore-paths.md` is one of the three documents I was handed as
the target cluster. **It contributes zero in-repo dangling citations.** Its
title is *"The leak was upstream: jobcore's first sweep, and the pin that could
not move"*, and it names its repository at every citation.

| token | repository | resolves there? |
|---|---|---|
| `5480246` | jobcore | yes -- ancestor of a freshly fetched `origin/master`, disambiguates to 1 |
| `6acc7e6` | jobcore | yes -- same |
| `b2f5d16` | jobcore | yes -- same |
| `fff1438` | jobcore | yes -- it is that repository's `HEAD` and `origin/master` |
| `fe21292` | ats-jobs | yes -- that repository's `HEAD`, 0 commits ahead of its remote |

Every `linkedin` SHA in the same file (`fbe2aef`, `dcf0a68`, `76667d4`)
resolves as an ancestor of `master`. The document mixes two registries and
labels each citation in prose; **the containing document is the slot, and it
decides which repository to ask.** Asking this repository about a jobcore
commit is the same error, one level out, as asking `cat-file` about a
help-article id.

`5480246` is all-digit, so it was never in the 60 at all -- the fifth
cross-repo citation, invisible to both censuses.

**MEASUREMENT PROVENANCE, stated because it is not mine.** A worktree-isolated
agent cannot run git against another repository: `git -C <jobcore> rev-parse`
is refused by policy, not by accident, and I confirmed the refusal against my
own worktree rather than taking it on report. The five cells above were run by
the coordinator, which is not worktree-isolated, on a remote fetched at the
time of measurement. **The isolation boundary was not routed around.** A child
I had assigned this slice reported BLOCKED with zero cells rather than a
partial table, and declined to hand-parse `.git/objects` as a workaround --
correctly: a loose-object scan misreports packed commits as absent, and a
hand-rolled ancestry walk fails in the direction that looks like a finding.

---

## 4. The open set: two tokens, and one was minted today

### `50e00eb7` -- a one-character slip, REPAIRED

`_audit/2026-09-20-the-six-unremapped.md:155` cited the eight-branch merge as
`50e00eb7`. No such object exists. `git rev-parse --disambiguate=50e00eb`
returns exactly one commit, `50e00eb0e064` (*"Merge branch
'worktree-agent-aa255d5b6ed0788c7' into integrate-1821"*, 2026-09-19T19:09:02+05:30),
whose eighth character is `0`.

**REPAIRED IN PLACE**, not annotated, and the distinction is the whole method:
a rewritten hash is the key a reader arrives with and must be kept; a mistyped
one never named anything and has no reader to serve. The corrected form is
itself branch-only (`--is-ancestor 50e00eb0 master` exits 1), and that is now
stated at the citation rather than left for a fourth census to find.

**It was written the same day, by the repair wave immediately before mine, in
the document whose subject is unresolvable citations.** That is the cheapest
available proof that this class is *generated*, not inherited.

### `c4e7cd3` -- already correct, LEFT ALONE

`2026-09-03-typeahead-name-matching-is-dead.md:321` reads:

> The range was first written as `e923355..c4e7cd3`. Hours later the unpushed
> history was rewritten [...] and `c4e7cd3` became a commit on a backup branch
> and nowhere on `master`. **It still RESOLVED**, which is the trap:
> `git cat-file -e` said yes, and the reference was already wrong.

The document repaired itself in place (the live range is now named by subjects
with `5a4117f`), kept the dead token as narration, and disclosed its status in
its own words. **No repair. It is the correct shape, and it named the
`cat-file` trap seventeen days before the wave that formalised it.**

---

## 5. The 24 that were already repaired -- verified, not assumed

`2026-08-24-perform-save-unsave.md` (8 SHAs) and
`2026-08-24-out-of-scope-wave.md` (16) were repaired on 2026-09-03. My
independent extraction reproduces **exactly 8 and exactly 16**.

The repair kept every dead hash and added two things: a note at the very top of
each file (*"EVERY SHORT SHA IN THIS FILE IS DEAD"*), and a
`## Dead hashes, recovered` table mapping each dead hash to the commit SUBJECT
-- which survives a rewrite -- and to the live hash.

**I re-verified all 22 mapped rows under the stricter predicate**, because the
2026-09-03 repair predates the ruling that `cat-file` is the wrong instrument.
Controls first: a known-good abbreviation resolved, a nonsense token did not,
and a known off-`master` branch tip gave exists=TRUE / ancestor=FALSE. Then,
per row: live hash exists, is an ancestor of `master`, its subject byte-matches
the table cell, that subject occurs **exactly once** on `master` (so the key is
unambiguous), the dead hash is absent, and the dead hash prefixes no object.

**22 of 22 clean. Zero anomalies.** The repair holds.

### The two UNMAPPED, and why they stay that way

`94600de` and `db99276` were left unmapped in 2026-09-03 because the evidence
conflicts. I tried to settle them with a measurement that wave did not run --
enumerate the whole live window and see what is unclaimed -- and it does not
settle them, which is itself the answer:

* The window spanned by the 22 live hashes holds **31 commits on `master`**.
  22 are claimed. **9 are unclaimed**, so counting forces nothing.
* Every commit that has EVER touched `2026-08-24-perform-save-unsave.md`
  (`460bd40`, `3ea7a8e`, `d2e1c70`, `a11d077`) is already claimed by a
  different dead hash -- so `db99276`'s own hypothesised reading has no
  candidate left that does not double-claim.

**And there is a mechanism that explains both without a twin existing at all.**
`db99276` entered the corpus in `460bd40`, *the commit that created the file*,
under a self-referential title convention -- it named a commit that did not yet
exist when it was written. That is not speculation: the sibling document's own
history contains `a9986ff`, subject **"docs(audit): correct three shas I wrote
before the commits existed"**, whose diff replaces `1e0e1a0` -- a hash that
never named anything -- in a title and two body positions.

**So "UNMAPPED" is not a shortfall. A guessed hash has no twin to find.**
Recording the gap is the repair, and filling these two on ordering alone would
produce rows indistinguishable from the twenty-two correct ones.

---

## 6. What the guard found, which is the part that matters

`scripts/check_cited_shas_resolve.py` decides kind by slot, then resolves by
ancestry, then suppresses where the document has already discharged the
burden. **22 distinct SHAs, 29 citations, across 19 documents.**

Only `a604394` is in the handed-down 60. The rest were invisible to a
shape-and-resolve census because that census was pointed at the August rewrite.

**THEY SHARE A CAUSE, and it is not a rewrite.** Almost every one is a commit
made on a `worktree-agent-*` branch by a wave that then wrote up its work
citing that SHA. The branch never merged; the SHA never reached `master`.
**The citation was unresolvable the moment it was written** -- including
`c4d2be2` (3 sites), `12c20e1` (3 documents, cited as a *ruling* three separate
waves depend on), `1349fe6` (2 documents), `c1991ac` (2), and `889f488` (2).

A wave that writes "the ruling at `12c20e1`" has written a pointer that two
sibling waves then copied, and none of the three can be checked from a clone.

**NOT REPAIRED, deliberately.** They live in nineteen documents belonging to
other waves, three of which are live right now. They are PINNED in
`tests/test_a_cited_sha_resolves.py` with a two-way ratchet: red on a new one,
and red when a pinned one disappears -- because "it was fixed" and "the
detector stopped seeing it" look identical from outside and only one is good
news.

### The suppressors, and why a guard needs them here

**A repaired citation and an unrepaired one have the same token shape.** The
2026-09-03 repair left 24 unresolvable tokens in the tree on purpose. A guard
that fires on them punishes the repair and gets switched off, so each
suppressor was read off the corpus rather than invented:

| verdict | sites | corpus wording it keys on |
|---|---:|---|
| `MARKED-MAPPED` | 14 | column 0 of a `## Dead hashes, recovered` table |
| `MARKED-DISCLOSED` | 11 | *"do not resolve on `master`"*, *"no clone can reach"*, *"nowhere on `master`"* |
| `MARKED-CROSS-REPO` | 6 | the containing document names another repository |
| `MARKED-DEAD-DOC` | 2 | *"EVERY SHORT SHA IN THIS FILE IS DEAD"* |

**The disclosure suppressor exists because the guard's first run convicted the
three documents that had done the right thing** -- including the sentence
*"and no clone can reach `5a69147`"*, a document being correct out loud in the
exact words this guard recommends.

### The one shape rule, measured

| length | ANCESTOR | LOCAL-ONLY | ABSENT |
|---:|---:|---:|---:|
| 7 | 186 | 29 | 22 |
| 8 | 1 | 0 | 0 |
| 12 | 10 | 2 | 0 |
| 16 | 0 | 0 | 3 |

Commit citations here are 7, 8 or 12 characters (12 because
`linkedin_server_info` reports `build.code.commit` at that width). **No
resolving citation is 16 characters, and all three 16-character tokens in a
commit slot are 64-bit content digests** -- *"`<functions>` is byte-identical
at `eb16cd07f5cf369d`"*. Corpus-wide, 47 distinct 16-hex tokens, zero resolve.
The bound excludes 16 alone; it does not exclude 32, 40 or 64, because a full
SHA is a legitimate citation and tidiness is not evidence.

### One slot phrase measured and DROPPED

A bare ``in `X` `` selects 44 occurrences and **8 of them are help-article
ids**, including `2026-09-05-decide-retire-rulings.md`'s own *"found in
`a1341821`, an article neither..."* -- the document naming the kind in the same
clause. Rejected, and recorded here with what it matched, because a refusal
that names only what it did NOT match is half a measurement.

---

## 7. What the controls caught in my own instrument

**A union assertion over a redundant corpus cannot detect a lost source.** My
first mutation control stripped one mark and asserted the citation came back.
It failed on both cases -- because the two repaired documents each carry a
declaration **and** a mapping table, so removing either leaves the other
covering the token. If the mapping-table parser broke tomorrow, a
"is it still suppressed?" test would stay green on the declaration alone. The
controls now assert **per source**: break one mark, and *that verdict* must
stop being handed down.

**A suppressor with no exclusive corpus example is a hole.** Chasing the above
showed `MARKED-DEAD-DOC` claims only 2 real sites, both on hashes that resolve
anyway -- everything it would cover is already covered by `MARKED-MAPPED`. It
is kept, because declaring a document's SHAs dead *without* a mapping table is
exactly what you do when no honest twin exists, and it is now controlled on a
planted document with its thinness stated rather than hidden.

**An assertion satisfied by an empty result cannot fail.** An empty candidate
set is a broken slot regex reporting a spotless corpus, so it exits 2.

---

## 8. Honest ledger

**WHAT I DID NOT SETTLE.**

1. **`94600de` and `db99276` are still unmapped**, and I believe they are
   unmappable. I have a mechanism (ahead-of-commit authorship, proven to have
   occurred in this wave) and an exhausted candidate list, but not a proof that
   neither ever named an object. The pre-rewrite objects are gone:
   `refs/original/refs/heads/master` is from the *September* rewrite and
   carries the August commits under their current hashes.
2. **Cross-repo resolution is not my measurement.** Five cells were run by the
   coordinator. I verified the isolation refusal myself and did not route
   around it; I did not verify their git output.
3. **I did not repair the 22 the guard found.** Nineteen documents, other
   waves' territory, three of them live. Pinned and handed over.
4. **The two line-locator overruns are not in my path.**
   `2026-09-19-the-remaining-partials.md:166` cites line 400 of a 263-line
   document, and `_census/mcp-inventory.md:206` cites line 1456 of a 1,299-line
   one. Neither citing file is one I touched, and the second is a census slice
   another wave holds. Left, and said so.
5. **The guard checks that a cited SHA RESOLVES, never that it says what the
   document claims.** A citation can resolve and still be wrong about its own
   content. Different, more expensive instrument.
6. **Occurrence-level recall is unmeasured.** I know the slot's kind precision
   on this corpus; I do not know how many commit citations sit in positions
   none of the 13 slot phrases reserve.

**ONE THING FOR A HYGIENE WAVE, NOT MINE TO RULE.**
`2026-09-03-hygiene-boundary-and-record.md:246` illustrates the sanitised-slug
SHAPE using a given-name-plus-surname-plus-hex example. I read it as a generic
placeholder used to describe a format, not a capture, and it is the document
that *built* the sanitiser. Flagging rather than editing: it is a public repo,
the judgement is not a citation judgement, and I am not the right wave to make
it.

**WHAT CHANGED IN THE TREE.**

    scripts/check_cited_shas_resolve.py     new -- the guard
    tests/test_a_cited_sha_resolves.py      new -- 16 controls and the pin
    _audit/2026-09-20-the-six-unremapped.md typo repaired + branch-only note
    _audit/2026-08-31-jobcore-paths.md      stale publication claim annotated
    _audit/2026-09-20-the-sixty-dangling.md this document
    _audit/INSTRUMENTS.md                   one entry, with its failing receipt

**THE NUMBER, one more time, with where each step went:**

    325   census, shape only
     60   minus 280 help-article ids                  (sibling wave)
     49   minus 11 CSS class fragments from one regex boundary
     26   minus 23 non-commit kinds and cross-repo citations
      2   minus 24 already repaired on 2026-09-03 and re-verified here
      0   open, after this wave

    22   found by asking the question a different way

---

**CORRECTS:** `_audit/2026-09-20-the-six-unremapped.md` -- section 3 cited the eight-branch merge as `50e00eb7`, which names no object; the merge is `50e00eb0e064`, and the corrected form resolves only via `integrate-1821`. Repaired in place in that document, which now carries the note.

**CORRECTS:** `_audit/2026-08-31-jobcore-paths.md` -- its "is the pinned commit `b2f5d16` on origin/master? NO -- unpushed" block, and the sentence that `git show b2f5d16:...` cannot resolve in a clone. Re-measured 2026-09-20 against a freshly fetched jobcore remote: `b2f5d16`, `6acc7e6` and `5480246` are all ancestors of `origin/master` there. That document now carries the dated note in place.
