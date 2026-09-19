# Four pieces of debt, and the two that were about the record rather than the code

2026-09-03. Four items, all offline, no LinkedIn access. Two are boundary work
and two are about whether this directory tells a reader the truth. The second
pair turned out to be the more interesting.

**Everything below was re-verified before it was acted on.** The wave arrived
with a list of ten addresses and a claim about each; the list was re-derived
from scratch against the live guard rather than inherited, and doing that
changed the framing of two of the ten and found one thing the handover did not
predict.

---

## 1. A per-address fix for a class defect -- ten members, closed as a class

### What was true, and it is not an open door

`readonly._FORBIDDEN_URL_SUBSTRINGS` describes itself as "a second,
independent gate" and as "belt and braces: a future pattern edited too loosely
still cannot reach these". Asked MECHANICALLY for the first time -- *which
addresses does the anchored allowlist refuse ALONE?* -- ten came back:

    /mypreferences/d/change-password
    /mypreferences/d/two-factor-authentication
    /mypreferences/d/verifications
    /mypreferences/d/member-cookies
    /mypreferences/d/job-application-accounts
    /mypreferences/d/profile-visibility-for-partners
    /public-profile/settings
    /uas/login
    /badges/profile/create
    /mwlite/settings

**NONE OF THEM WAS EVER REACHABLE.** The anchored allowlist refused all ten
and refuses them still. This is a defence-in-depth asymmetry -- one layer where
the module promises two -- and stating it in that order matters more than the
fix, because the fix is small and the temptation to describe it as a closed
hole is not.

Verified independently, not inherited: `_audit/_scratch/_probe_class_defect.py`
put all ten plus three controls through the live guard and read back which
layer refused each. The controls -- `/close-accounts`, `/hibernate-account`,
`/mypreferences/d/categories/privacy` -- each came back with a forbidden hit AS
WELL as the allowlist miss, which is what makes the ten a finding rather than a
listing.

### What the handover did not predict

`/public-profile/settings/` and `/mwlite/settings/` -- WITH a trailing slash --
were **already caught**, by the `"/settings/"` entry that has been on the list
since the beginning. Only the SLASHLESS spelling escaped. Two of the ten are
therefore a spelling defect in an existing entry rather than a missing entry,
and that reframing is what identified the class.

Also measured: `/mwlite/mypreferences/d/close-accounts` IS refused, by
`/close-accounts`. The substring gate is tree-agnostic already, so the mobile
tree inherits every entry that names a PAGE. What it did not inherit is every
entry that names a PATH.

### The class

**The list was anchored to path spellings on the desktop tree.** Three ways
past it, and all ten members are accounted for by one of them:

| way past | member(s) | closed by |
|---|---|---|
| a second SPELLING | `/public-profile/settings`, `/mwlite/settings` | `settings` (bare) |
| a legacy NAMESPACE | `/uas/login` | `/uas/` |
| a parallel TREE | `/mwlite/settings` | `/mwlite/` |
| a missing VERB | `/badges/profile/create` | `/create` |
| the settings sub-tree | the six `/mypreferences/d/` pages | six word entries -- see the blocker |

Ten entries were added. **Ten entries is not ten literals, and the difference
is asserted rather than claimed**: `tests/test_the_second_gate_covers_the_class.py`
puts a real address through the real guard FOR EVERY NEW ENTRY, choosing an
address that is *not* one of the ten. An entry that closed only its own member
goes red there. `/mwlite/` is the cheapest line in the change -- one entry, an
unbounded family, an entire mobile-web mirror of the site that no desktop
pattern anticipated.

`"/settings/"` was KEPT rather than replaced by the bare word. The bare word is
a strict superset, so replacing would have been a DELETION from a list that has
only ever grown -- needing its own review and buying nothing.

### The blocker, measured rather than argued

Six of the ten live under `/mypreferences/d/`. That prefix is the natural
close and **it cannot be taken**, for two reasons and the second is the one
that decides:

1. The six share with the two ADMITTED urls under that prefix -- the settings
   index and `/mypreferences/d/dark-mode` -- only the prefix itself. No
   substring separates them. The same mechanical fact already recorded for
   `/feed/update` on 2026-08-31.
2. `readonly._FORBIDDEN_SUBSTRING_EXEMPTIONS` could hold the two admitted urls
   for the READ door. **`writes.assert_write_url` does not consult that table
   at all.** It iterates the forbidden tuple directly and honours only
   `spec.exempt_substring`, which is `None` on the settings write. Measured:

        write blocked: 'https://www.linkedin.com/mypreferences/d/dark-mode'
        contains '/mypreferences/d/', which this action does not exempt
        (it exempts None)

**So the prefix closes six read addresses and breaks the only settings write
this server ships.** The repair is one line -- `exempt_substring="/mypreferences/d/"`
on the `update_setting` spec at `linkedin_server/writes.py:1347` -- and
`writes.py` was not this wave's to edit. It is left as a decision for whoever
owns it, pinned by
`test_the_subtree_prefix_is_absent_and_the_blocker_is_shown`, which drives the
breakage rather than describing it.

**The word entries are not merely the fallback.** `password` refuses the
password page at EVERY address -- desktop tree, mobile tree, legacy namespace,
whatever LinkedIn ships next. The prefix would refuse it at one. On this axis
the second-best close is the broader one.

### One residue, recorded

A word entry matches the WHOLE url, and `/in/<vanity>/` is on the allowlist, so
a member whose vanity slug contains one of these words is now refused.
`cookies` and `visibility` are the two that could plausibly appear in a real
handle. **Measured before accepted:** every `linkedin.com/in/<slug>` in this
repository was extracted -- 16 distinct slugs, ZERO refused by any new entry.
The failure mode is the safe one: a loud error naming the substring, never a
silent wrong read.

### What moved

    _FORBIDDEN_URL_SUBSTRINGS  afcb7f0d14c481a0 -> b0291a66ec9bd51e

and **nothing else at all**. `<functions>` is unchanged, so `assert_read_url`
is byte-identical across a change that added ten refusals to it: no gate taught
an exception, no check reordered, no clause relaxed. The whole change is DATA.
Zero casualties, measured before applied, against every census surface, every
readable setting and every write target rebuilt from its own spec.

**Verified under 3.13.14 only** -- the box carries one interpreter, and that is
a real gap in the ritual rather than one to paper over. What limits the risk is
the shape of what moved: a tuple of plain string literals, the class this
file's own history records as matching on every Python through both interpreter
splits. The 3.10 cell in CI is the actual verification.

---

## 2. The system of record was stale about a repaired tool

`update_profile_field` shipped on 2026-09-02 in "feat(writes):
update_profile_field performs -- the eleventh, and the best verified"
(`a540461`). **It could not navigate once.** Three independent fatal blockers,
any one sufficient: no arm in `anchor_label_for`, so it raised at the FIRST
guard with `NAVIGATIONS ATTEMPTED: []`; a landing check comparing the whole url
against a surface measured to redirect; and a reader that dropped the `dom_id`
its own aiming used.

**And it was not one action.** `send_invitation` -- shipped the day before as
"the FIRST that reaches another person" -- failed the second blocker too. Two
of the eleven writes used a self-profile surface and both were dead.

**The shape was the worst available.** `grant_is_possible` asks membership and
addressing and NOT aiming, so `mint` issued a LIVE CONFIRM TOKEN: the operator
read a real preview off a real read of his own profile, **approved it**, and
the second call died at the first guard. It shipped unable to act while minting
live confirm tokens he approved. That is the sentence, and it belongs in the
record in those words.

Repaired the same day in "fix(writes): update_profile_field could not act, and
neither could send_invitation" (`ea5354d`).

**THE FINDING IS THE GAP, NOT THE BUG.** That repair reached the commit log and
the server's own tool description on 2026-09-02 and **zero audit files**. For a
day, anyone reading `_audit/` alone -- including a future agent booting from it
-- learned that the action refuses. The sharpest form was
`_audit/2026-08-31-linkedin-perform.md`, which carried
`-> STILL TRUE, verified 2026-09-02`: a false claim wearing the date of the day
it was falsified. Two adjacent items in the same section were stale too -- the
`/edit/` write ruling, and a `SANCTIONED_MUTATIONS` count of three that is now
four.

Corrected in place, as a dated block ABOVE the stale heading rather than a
rewrite. The sections are contemporaneous records and their reasoning was sound
on the day; what a reader needs is to meet the correction before the claim.

**Nothing in this repository was watching for this.** A system of record
updated by the code but not by the record is not one.

---

## 3. The ignore rule was an exact path, not a glob

`.gitignore` named `_audit/_sanitisation_key.json` as an exact path. A working
backup called `_sanitisation_key.json.bak-preneedle-20260903` was **fully
committable** -- the one file that reverses every scrubbed fixture, untracked
and un-ignored, one `git add -A` from a public commit. It was moved out of the
tree by hand.

**Measured with `git check-ignore`, git's own answer rather than a reading of
the file. Six of seven spellings were committable, and the last one is the one
the handover did not predict:**

    IGNORED      _audit/_sanitisation_key.json
    COMMITTABLE  _audit/_sanitisation_key.json.bak-preneedle-20260903
    COMMITTABLE  _audit/_sanitisation_key.json.bak
    COMMITTABLE  _audit/_sanitisation_key.backup.json
    COMMITTABLE  _audit/_sanitisation_key-copy.json
    COMMITTABLE  _audit/_sanitisation_key.json.orig
    COMMITTABLE  scripts/_sanitisation_key.json     <- a COPY AT ANOTHER PATH

The rule was anchored to the DIRECTORY as well as to the name, so a copy beside
the sweep that READS the key -- where a copy would most naturally land -- was
never covered either.

Closed with `_sanitisation_key*`, carrying **no leading directory** so it
matches that basename at every depth. The exact line is kept: it costs nothing
and `test_no_committed_identity.py` asserts that string is present.

`tests/test_the_sanitisation_key_is_unignorable_under_any_name.py` puts eleven
spellings through `git check-ignore` and **asserts from the other side too** --
that the glob does not swallow the sweep script beside it. An over-broad ignore
fails silently: a file that should be tracked simply never appears in
`git status`.

The instrument is `git check-ignore` and not a grep of `.gitignore`,
deliberately. A grep can only confirm that a line somebody wrote is still
there. The exact-path rule would have passed a grep every day it was
insufficient.

---

## 4. Dead cross-references, and the rule they teach

`_audit/2026-08-24-out-of-scope-wave.md` cites **16** distinct pre-rewrite
hashes across 30 occurrences; `_audit/2026-08-24-perform-save-unsave.md` cites
**8** across 14. **Twenty-four distinct, none resolving.** A rewrite scrubbed a
name out of every blob and message, so each commit kept its subject and author
date and took a new hash; a garbage collection then removed the old objects
locally too. On a fresh clone every citation reads `unknown revision`.

**The count is 24 and not 25**, counting distinct hashes in the two named files
with the method below. Stated rather than adopted.

**Counting them needed the structure, not the shape.** A first pass matched any
7-40 char hex run and reported 127 dead "citations" -- because this corpus also
carries UUID segments (`componentkey="e205ae22-..."`), obfuscated CSS class
names (`bb9bff38 _7917aabf`), sanitised vanity slugs
(`priya-sharma-8a41b207`), sha256 prefixes and 11-digit LinkedIn job ids. Two
of the survivors were still false positives after tightening and were
classified by reading them: `a528144` is a LinkedIn help-article id that returns
HTTP 404, and `5db0579` is a component key.

### The recovery

Both files now carry a header note and a mapping table: **19 CONFIRMED, 3
LIKELY, 2 UNMAPPED.** The evidence is stronger than expected. The tracked `.md`
files are blobs, so their text kept the OLD hashes byte for byte; several LIVE
commit message BODIES restate the same facts -- run ids, measured counts, a
specific 1393-vs-1407 correction -- using the NEW ones. Where both sides
describe one event that is a direct cross-reference, not an inference. Two
structural checks anchor it: `git log -1 c89d0b2^` returns `a11d077`, matching
"pre-wave `a1360d1`"; `git rev-list --count 67f7988..d2e1c70` returns 8,
matching "the gap existed for eight commits".

**One mapping was confirmed cryptographically.** `test_readonly_boundary_invariant.py`
told a reader to re-derive its baseline with `git show
5277dfc:linkedin_server/readonly.py` -- a dead command in the file whose whole
job is noticing when something moved. Running `ast_digest` over `git show
7eee070:linkedin_server/readonly.py` reproduces **all four** documented
constant digests exactly and yields `<functions> = 9f0a86dafffc2299`, the value
that file names as its own pre-2026-08-24 value. Five independent 64-bit
agreements. A subject could be a coincidence; five digests are not.

**Two were left UNMAPPED, and that is the answer rather than a shortfall.**
`94600de` and `db99276` each have CONFLICTING evidence: the obvious positional
reading points at a commit already claimed, on stronger self-referential
evidence, by a different dead hash, and two dead hashes cannot be one commit.
Both conflicts are written out in full at the foot of that file. A table that
filled them on ordering alone would read exactly like the fourteen rows above
it and be wrong.

### The rule

**CITE THE SUBJECT FIRST AND THE HASH SECOND.**

A subject survives a rewrite; a hash does not. **A reference pinned to a hash
goes false without anybody editing the file it lives in** -- which is the same
trap as a claim pinned to a moving HEAD, arriving from the other side. In both
cases the document is unchanged, the world moved, and nothing in the text can
tell a reader that it happened.

And the trap has a sharper edge, recorded in
`_audit/2026-09-03-typeahead-name-matching-is-dead.md` on the same day: a hash
orphaned onto a backup branch **still resolves**. `git cat-file -e` says yes
while the reference is already wrong. Resolvability is not correctness.

The live hashes in both recovery tables are themselves perishable and the
subjects are not. They are given because they are useful today, not because
they are the reference. If those tables need remaking after the next rewrite,
remake them from the subjects.

---

## Where this wave's work landed, and who committed it

Three agents were writing this tree throughout. Twice the protocol fired in
both directions: this wave PINNED another agent's uncommitted work in
"pin: another agent's in-flight radio-label-binding work, adopted not authored"
(`0db1a62`), and another agent pinned THIS wave's in-flight boundary change in
`8e20f27` and `d77c88f`, both titled "adopted not authored". Nothing was lost
either way, and the class close is therefore in history under a commit that
correctly disclaims authorship of it. The reasoning lives in the code and the
tests, which is where it is useful.

**One thing surfaced by a pin and worth naming.** Committing another agent's
untracked test file made it visible to the identity guard, which went red on an
undeclared urn id in it -- an untracked file is not scanned, so tracking it is
what revealed the condition. It was fixed by its author in "fix(identity): a
shape-valid urn, taken from the allowlist instead of invented" (`b17bf8f`).
The pin did not cause it; it found it.

## Tests run, and what was NOT run

Run and green: `test_readonly.py` (186), `test_readonly_boundary_invariant.py`
(9), `test_the_second_gate_covers_the_class.py` (28),
`test_the_sanitisation_key_is_unignorable_under_any_name.py` (13),
`test_writes.py`, `test_writes_nine.py` (146), `test_path_hygiene.py`,
`test_no_committed_identity.py` (244), `test_navigation_is_never_derived.py`,
`test_addressing_is_not_permission.py`,
`test_messaging_recipient_addressing.py`.

**The full suite was NOT run** -- it belongs to the team lead's gate. Not
covered by this wave's targeted runs: `test_server_surface.py`,
`test_surface_census.py`, `test_reader_reachability.py`, and every fixture,
dom, apply, typeahead, session and auth module.

**A batched run over a moving tree is not evidence, and this wave learned it
twice.** An early combined run reported 29 failures; every one of them was
another agent editing `dom.py` and `writes.py` mid-run, and each file passed
cleanly on its own afterwards. Both readings were re-taken with the tree
settled before anything was concluded from them.
