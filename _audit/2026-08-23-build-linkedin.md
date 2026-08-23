# linkedin, 2026-08-23 -- leak walker, and a write design that is scoped rather than unlocked

## Verdict first: the leak walker was blind, and it is measured blind

**Read this before the numbers.** *The server was not leaking.* The finding is that the
TESTS were incapable of noticing if it ever started. Every measurement below is against a
DELIBERATELY leaking build injected by a control plugin, so "34 of 54 green" means "34 ways a
future leak would have gone unnoticed", never "34 leaks shipped". The proof of the
distinction is the diff: this wave changed **zero lines of `linkedin_server/`**. It is
entirely tests and instruments.

1. The naukri warning transfers to this repo EXACTLY, and it is worse here: the credential
   is a 365-day one. Every leak assertion was `assert SECRET not in json.dumps(result)`.
2. MEASURED with `scripts/credential_echo_control.py` (a pytest plugin that echoes the
   test's OWN planted `li_at` back out of all five auth entry points) gridded by
   `scripts/leak_matrix.py`: **34 of 54 cells GREEN. Green = the leak shipped.**
3. Five of nine transforms were invisible to all six assertions: **b64, b64url, hex,
   value-split-across-two-fields, and log-only.** A result carrying the ENTIRE session
   cookie, base64'd, passed every "no cookie value leaks" test in the package.
4. Honest counter-note: `percent` and `repr_escaped` came back red for an uninteresting
   reason -- for an ASCII base64url token `quote()` and `repr()` are near-identity, so the
   substring survives by accident. Not coverage.
5. The MARKERS were half the defect. Plants were `"live"`, `"stale"`, `"x"`,
   `"secret-token-value"` -- none li_at-length, li_at-charset or li_at-entropy, so no test
   ever showed the guard the kind of value an encoding or truncating redaction fires on.
   `prefix12`'s one red was an artifact: `"live"[:12]` still contains `"live"`.
6. The weakest thing in the package was the CONTROL. `test_that_leak_check_can_actually_fail`
   planted the credential verbatim -- the one case the old hunt already handled -- so it
   certified the only thing that was never broken. **This generalises past leak walkers and
   is the most portable thing in this document: a control that exercises only the working
   path is not a control.**
7. FIXED. `tests/leakwalk.py`: 13 renderings, every 12-char RUN (so a truncating redaction
   or a split value counts), a total object WALK (dict keys, bytes, exception args, unknown
   types via repr), plus the LOG. And `find_credential_shaped`, which hunts the SHAPE of a
   li_at with no marker at all -- the half that catches the REAL credential on a path no
   test plants into.
8. RE-MEASURED, same grid: **0 of 54 green.** All nine transforms caught by all six tests.
9. NEW `tests/test_no_committed_credential.py` sweeps every git-tracked file for a
   credential shape -- the fixture that leaked here before walked past a guard made of five
   literal NAMES, and a name cannot see a value. Clean: 72 tracked, 71 swept, 1 exempt by
   exact path (the module that DEFINES the plant), and that exemption is itself asserted to
   be the only one and to still hold a plant.
10. Read-only boundary untouched: `readonly.py`, `test_readonly.py`, `test_launch_boundary.py`
    are **zero-line diffs** against oldsha01 and in the working tree.
11. A guard that is right today can be reverted tomorrow and the suite stays green, so
    `test_each_guarded_test_still_runs_through_the_walker` reads the six guarded tests by AST
    and fails if one stops calling the walker. Driven at a REAL revert of a real test: it
    fired and named it, while `test_auth.py` itself still passed -- which is the decay.
12. 786 -> 911 passed, 0 skipped. Commits `oldsha16`, `oldsha09`, `oldsha25`, `+1`.
    CI **success** on `oldsha25`, run id **32616918805**.
13. **A second writer was live in this tree the whole time** -- see the last section.

---

## BUILT 2026-08-23, after the operator's ruling: the cage, not the animal

The operator **cut apply, connect and InMail** and approved **save/unsave, follow, Open To
Work** behind an off-by-default flag. `linkedin_server/writes.py` + `tests/test_writes.py`
(76 tests) land the boundary those three will pass through, and deliberately **do not land the
click**.

**Why no click, and why that is the deliverable rather than a gap.** The permission classifier
still refuses LinkedIn writes, so a click authored today could not be exercised even once. The
standing rule is that anything unexercisable does not ship -- and the click is *precisely* the
unexercisable part. `writes.perform()` raises. Everything around it is real and tested.

The happy consequence: **no mutating Playwright call enters the package**, so
`scan_source_for_mutations` still reports zero for every file including the new one, and
`readonly.py` / `test_readonly.py` / `test_launch_boundary.py` keep their zero-line diffs. The
read-only guarantee is not degraded by a single line to make room for a write that cannot
happen yet.

**Shipped and exercised:** the grant (one action, one target, single-use, 120s TTL, never
persisted -- a grant that outlived the process is one a scheduler could pick up); the separate
url door that *rebuilds* the target from the grant so a caller has nothing to influence; the
forbidden list unshortened with per-action `==` exemptions (all three currently exempt
**nothing**); the conservation law; and `render_preview`, which **enforces** the
measured-reversibility rule rather than documenting it. All three specs are unmeasured today,
so all three print `UNMEASURED` plus the procedure that would settle them. That is the rule
biting its own author.

**Open To Work was NOT specced, and the omission is deliberate:** there is no capture of it at
any hydration state, its surface is not on the navigation allowlist, and its recruiters-only
vs all-members choice is visible to a current employer -- the single setting where a blind toggle is
least acceptable.

### Two findings while building it, both against my own work

1. **A loophole in my own conservation law.** It says a name leaves `FORBIDDEN_TOOLS` only by
   arriving in `SANCTIONED_WRITES` -- but says nothing about a name that was *never* forbidden.
   `linkedin_follow_company` is exactly that: it sanctions a follow while `linkedin_follow`
   sits on the forbidden list looking untouched. Quiet widening by renaming. **Closed.**

2. **`readonly.name_implies_write` is BLIND TO UNDO VERBS -- needs a ruling.** `WRITE_VERBS`
   holds `save` and `follow` but **no `un`-prefixed verb at all**, so `linkedin_unsave_job`,
   `linkedin_unfollow`, `linkedin_unlike`, `linkedin_unsubscribe` and `linkedin_disconnect`
   all read as **not a write**. Undoing a write is still a write. They are caught today only
   because somebody hand-listed two of them -- *this pass's whole theme, one level up: the
   literal list sees the instances someone remembered, the generalising check cannot see the
   class.*

   **Not fixed here on purpose.** `readonly.py` is under a zero-line-diff constraint, and
   quietly editing the read-only guard while shipping a write module is exactly the move that
   should draw suspicion. The gap is **pinned** by a test that asserts the bug and instructs
   its own deletion when fixed, and the proposed one-line fix ships as executable evidence in
   `_write_verbs()`. **Its limits are measured too:** it closes `unsave`/`unfollow`/`unlike`
   and does **not** close `unsubscribe` or `disconnect`, where the base verb is absent from the
   list or the prefix is not `un`. Reported that way because a fix announced as closing "the
   undo gap" that closes three names of five is the overclaim this project keeps paying for.

### The future click's anchor, pinned now so it is not a guess later

`button[aria-label="Save the job"]` and `button[aria-label="Follow"]`, both **frozen at both
hydration states**, anchored on the accessible name -- never `data-view-name` (absent
pre-hydration) and never a class (a build hash). With the blocker recorded where it will be
hit: **both are TOGGLES and the captures only ever show the OFF state**, so nothing can yet
tell Save from Unsave, and a gate that cannot say which way it moves a toggle is not a gate.
Solvable for save through the existing `linkedin_saved_jobs` read; **not** solvable for follow,
which is why follow needs a follow-state read before it ships.

---

## Write design: a grant, not a mode

**The one idea.** Today `readonly.py` answers "is this a read?". A write-capable server must
answer a strictly HARDER question: *"is this the one write he confirmed, on the one target he
was shown, right now?"* That is a narrower gate than the current one, not a weaker one. So no
mechanism is removed anywhere below; each gains a **keyed exception that is per-action,
per-target, single-use and time-boxed.** If any item reads as "writes are allowed", it is
wrong and should be cut.

### 1. The protocol: every write is two calls

A write tool called WITHOUT `confirm_token` performs **nothing** and returns a PREVIEW. The
preview mints a `WriteGrant` -- bound to one action, one target id, one process, consumed on
first use, expiring in 120s. The second call must echo the token back. A grant cannot be
minted except by a preview that actually re-read the target live, so the operator is never
confirming an id he cannot check.

Modelled on `uplers_apply(confirm=True)` and `linkedin_logout(confirm=True)`, which already
work this way in this family -- but with a TOKEN rather than a boolean, because a boolean can
be set by a caller that never saw a preview.

### 2. What each gate shows

Uniform for every action: WHAT (plain words) / WHERE (target re-read live -- job title,
company, id; never a bare id) / COST / REVERSIBILITY / WHAT IT CANNOT UNDO.

| # | Write | Gate must additionally show | Reversibility |
|---|---|---|---|
| 2a | `save` / `unsave` job | the posting, re-read | reversible -- **ship first, it is the only clean one** |
| 2b | `follow` / `unfollow` company | company, current follower state | reversible |
| 2c | Open To Work | **recruiters-only vs all-members**, verbatim | reversible, but the public badge is visible to a current employer |
| 2d | `apply` (Easy Apply) | every prefilled answer, the resume file, the count of screening questions | **UNMEASURED** |
| 2e | `connect` | weekly invite quota remaining | **UNMEASURED** (withdraw has a cooldown) |
| 2f | `message` / InMail | recipient, full body, **credits before and after** | **IRREVERSIBLE, spends a credit -- highest stakes, ship last** |

**Hard rule: a gate may not print a reversibility claim that has not been measured.** Three of
the six are unmeasured today, so those three cannot ship until each is measured once. That is
a precondition, not a caveat.

### 3. Mechanism 1, navigation allowlist -- narrowed, not opened

`assert_read_url` keeps a **zero-line diff**. Writes go through a *separate*
`assert_write_url(url, grant)` in a new `linkedin_server/writes.py`, which requires a match
against a per-action pattern with **the target id interpolated from the GRANT, not from the
caller**. `_FORBIDDEN_URL_SUBSTRINGS` is **not shortened**: each action names the ONE
substring it needs exempted and the exemption is compared `==`, exact. A grant for `apply`
exempts `/jobs/application` and nothing else; `/messaging` stays forbidden on that grant.

### 4. Mechanism 2, source scanner -- narrowed by confinement plus AST

`scan_source_for_mutations` keeps running over every module and must stay at **zero hits for
all of them except `writes.py`**. Every mutating Playwright call in the package lives in that
one file. `writes.py` then gets a STRICTER check the others do not have: an AST pass asserting
every mutating call sits inside a function that takes a `grant: WriteGrant` and consumes it as
its first statement, plus a frozen table of permitted call sites, so a new `.click()` cannot
appear without a diff to that table. The `# readonly-ok` waiver is untouched.

### 5. Mechanism 3, tool surface -- a conservation law

`WRITE_VERBS` unchanged. A name may leave `FORBIDDEN_TOOLS` **only by arriving in a new frozen
`SANCTIONED_WRITES` map** (name -> action -> gate spec), enforced by a test asserting
`FORBIDDEN_TOOLS | set(SANCTIONED_WRITES)` still covers the original frozen set. Nothing can
be quietly deleted from the forbidden list. `docstring_write_claims` inverts rather than
relaxes: a read tool still permits zero affirmative claims; a sanctioned write tool permits
exactly its own verb AND must carry the confirm-gate sentence.

### 6. Mechanism 4, launch boundary -- permanently unchanged

Zero-line diff, forever. Writes need no third flag. Performing an action he confirmed and
evading automation detection are different activities, and the second one is not on the table
at any point in this design.

### 7. Permanently forbidden -- no grant is ever minted for these

Feed posts, comments, likes, shares (public speech in his name); endorsing or recommending
another person (a statement about someone else); de-anonymising a viewer or fetching anything
about a third party beyond the row LinkedIn renders him; profile edits beyond the Open To Work
toggle; delete/withdraw of anything; `linkedin_notifications` mark-read; auto-accepting
invitations or auto-replying to messages; any N>1 loop, sweep or scheduled write.

### 8. Blast radius

Off by default at config level, so a fresh clone is read-only. One write per invocation. A
per-action daily cap persisted to disk. A kill switch. **No scheduler may ever hold a grant** --
the 120s TTL is chosen to make an unattended write structurally impossible.

### 9. How it gets exercised, given the classifier still refuses

Shipping an unexercised write against LinkedIn is the worst outcome, and the harness blocks
live exercise today. So: build against a **local fake LinkedIn** (fixture server) that
exercises every gate path end to end without touching linkedin.com; then the first real
exercise is **one operator-supervised `save` then `unsave`** -- the only cleanly reversible
action -- on a throwaway posting. Nothing else goes live until that round trip is clean.

### 10. What I would cut

**Cut 2d, 2e, 2f from this round.** Apply, connect and InMail are the three unmeasured,
least-reversible actions on the least tolerant platform in the family, and this is his only
account. Ship 2a/2b/2c behind the flag, prove the grant machinery on the reversible ones,
measure the other three, then revisit. Approving all six at once buys a mechanism nobody has
watched work.

---

## Reads: what I did not build, and why

`_audit/2026-08-22-parity-linkedin.md` ranked "skill endorsement counts" as the smallest real
win at **0 extra page loads**. **That is mis-specified, measured:** `tests/fixtures/profile_skills.html`
carries **zero** endorsement counts -- no `N endorsements` text anywhere in the capture. The
"already loaded" half is right; the *capture* does not exist, so the build needs a fresh live
page load and a re-freeze, not zero.

What the frozen fixture DOES carry and no tool reports: per-skill corroboration lines
(`"2 experiences at Northwind and 1 other company"`, `"Passed LinkedIn Skill Assessment"`).

Read `test_a_skill_keeps_only_its_name_not_its_evidence_lines` before acting on that, and read
it carefully -- I nearly got this wrong. It forbids those lines from becoming ENTRIES IN THE
SKILLS LIST, which is right: they are not skills. It does **not** decide that the evidence
must be thrown away. Surfacing them as structured per-skill attributes would not contradict
it, provided they never rejoin the flat list.

**But** the skills fixture exists at ONE hydration state only -- there is no
`profile_skills_hydrated.html` -- and the standing rule here is that a parser is frozen at
both, because a fix that passed every test while returning nothing on the hydrated render has
already happened in this repo. So it is a one-page-load slice, not the zero-page-load one the
parity audit advertised, and I did not build it blind.

Search appearances (rank 1) needs a new surface and a live capture. Job recommendations
(rank 3) overlaps the `linkedin-jobs` Gmail skill, which reads the same digests for free.
Post/follower analytics (rank 4): he is not posting. My read is that **none of the four earns
its page load this pass** ahead of the write design being ruled on.

Still open from the parity audit and NOT resolved here: the `linkedin-jobs` skill's Scope
clause (`SKILL.md:341-342`) says *"do not revive mcp-servers/linkedin/"*, which this wave
contradicts. It needs a decision, not a silent override.

## Tree hazard: I was not the sole writer

The brief said tree clean, HEAD `oldsha01`, all other agents done. Disk disagreed. The
`auth-lifecycle` agent was live and committed twice after my session began (`oldsha17` 09:02:06,
`oldsha19` 09:02:55). **`oldsha19` swept three of my in-flight files into itself** --
`credential_echo_control.py`, `leak_matrix.py`, the first draft of `leakwalk.py` -- under a
commit message entirely about `renewal.uses_browser`, which never mentions them, and which
claims "782 -> 786, all green" for a tree containing my unfinished walker.

Not reverted: the content is correct where it sits, and reverting would delete my own files to
fix an attribution problem. Instead I pinned the remainder immediately as `oldsha16` with a
provenance note, and did not open a single tracked file until the tree had been clean and HEAD
still for eight minutes. Escalated to the lead twice; only the operator can kill a live
duplicate.

**`oldsha19`'S TEST COUNT CANNOT BE ATTRIBUTED -- do not reconstruct history from it.** Its
message reads *"782 -> 786 tests, all green"*. That tree already contained my `leakwalk.py`,
`credential_echo_control.py` and `leak_matrix.py`, so the four are not cleanly that agent's
four: they are some mixture of its work and mine, and nobody can now say which. It is the same
defect family as a query publishing its `LIMIT` as a total -- a number that means something
other than what it says. The first count in this repo that is cleanly attributable again is
`oldsha25`'s.

**A METHOD NOTE AGAINST MYSELF.** Four of my five commits staged with `git add -A`. Audited
afterwards, all ten files across all five commits are mine and nothing alien was swept -- I had
checked `git status` before each -- but checking status and then running `add -A` leaves a race
window that naming the paths would have closed outright. Two agents swept files they did not
own this way within one hour today, one of them pushing real third-party PII. The outcome here
was verified, not protected. Explicit paths from here.

**FOUR-SERVER SHAPE PARITY: PASSED**, re-run at this HEAD before pushing rather than left for
CI. `_audit/auth_shape_parity.py` asked all four servers `session_info(verify_live=False)` in
their own venvs: **3 named differences, 0 unnamed** (linkedin `browser_mode` + `supporting.note`,
naukri `supporting.why_unknown`). Its `--self-test` came back **FAILED with 6 violations**, so
the checker is shown rejecting rather than merely passing. This wave could not have moved that
result -- it changed zero lines of `linkedin_server/` -- which makes the run a confirmation
rather than a near miss.
