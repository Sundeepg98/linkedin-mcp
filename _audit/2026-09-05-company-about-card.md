# The About-the-company card, and 55 lines in my commit that are not mine

Wave `company-page`, 2026-09-05. Commit `bc5c2eb`.

## 1. THE CREDIT, FIRST, BECAUSE IT IS OWED

**`bc5c2eb` carries 55 insertions and all 13 of its deletions from another
wave.** They are three hunks in `linkedin_search_jobs`' docstring; my own work
is two hunks in `linkedin_job_detail`, +73/-0. The split, measured off
`git diff bc5c2eb~1 bc5c2eb -U0` rather than estimated:

| hunk | lines | whose |
|---|---|---|
| `@@ -2416,4 +2416,24 @@ linkedin_search_jobs` | +20 -4 | **not mine** |
| `@@ -2425,7 +2445,24 @@ linkedin_search_jobs` | +17 -7 | **not mine** |
| `@@ -2452,2 +2489,7 @@ linkedin_search_jobs` | +5 -2 | **not mine** |
| `@@ -2705,0 +2748,38 @@ linkedin_job_detail` | +38 -0 | mine |
| `@@ -2891,0 +2972,35 @@ linkedin_job_detail` | +35 -0 | mine |

**I DO NOT VOUCH FOR THE 55 LINES.** I did not write them, did not review the
measurement behind them, and did not run the probe they cite. Pinning a file
adopts the author's disclosure as well as their design, so what I did check is
the disclosure: `test_no_committed_identity` passes on `linkedin_server/server.py`
at this commit. That is the whole of my claim about them.

**The work is worth naming rather than merely returning.** It replaces the
docstring's `start=25` paging advice with a measured one: the search reader's
window is **seven postings per call**, measured over seventeen live loads
across two professions, two cities, five filters and three job-type values,
and seven every time -- on one query whose own LinkedIn count was 2915. So
`start` offsets by ones and the old advice silently skipped eighteen postings
in every twenty-five. It also converts the single-location limitation from an
unmeasured omission into a measured refusal.

**Owner, named by ARTIFACT and not by wave name**, per the standing rule that
`git log --oneline -3 -- <path>` names an owner and nothing else does. These
lines were uncommitted, so there is no log to read. The artifacts they cite
and sit beside are `scripts/_probe_job_search_paging_stride.py`,
`scripts/_probe_job_search_result_ceiling.py` and
`scripts/_probe_job_search_result_sets.py` -- three untracked probes on job
search. That is what I matched on, and I am saying so so that a wrong match is
visible rather than silent. The capability is the census's `JOB-SEARCH-PARAMS`.

### How it happened, and the rule it defeats

`git diff --numstat` on all three of my files read `+121 / +73 / +301`, **zero
deletions**, immediately before the commit. The commit reported 13 deletions.
The neighbour wrote `server.py` in the seconds between my reading and my
`git commit --only`.

**`--only` worked exactly as designed and could not have helped.** It kept
four staged files of a THIRD wave (`events.py` and its probes and tests) out
of my commit, which is the failure it prevents. The 55 lines were inside a
path I named. That is the distinction the freeze file records at 14:10 --
a neighbour's STAGED FILES are prevented, a neighbour's LINES inside a file
you both edit are not -- and this is a fourth instance of it in one day.

**NOT REWRITTEN, deliberately.** Rewriting HEAD in a multi-writer tree trades
a mis-attributed commit for something genuinely hard to undo, and their lines
are byte-identical in history. The author has been told directly.

## 2. WHAT THE WAVE ACTUALLY BUILT

`COMPANY-PAGE-SURFACE` is 18 rows, 13 of them reads, all 18 filed behind
putting `/company/` on the read allowlist. **Four of the thirteen reads do not
need it**, and they now ship in `linkedin_job_detail.company_about`:

| census row | capability | where it actually renders |
|---|---|---|
| `N 53` | a Page's follower count | the posting's About-the-company card |
| `J 106` | About tab: industry and size | the same card |
| `N 101` | employees, as a count | the same card, "N on LinkedIn" |

A fourth, `J 107` (the Page's Jobs tab), was already resolved by the previous
wave through `/jobs/search/?f_C=<id>`. And a fifth row moved without becoming
a capability: **`J 86` / `P I14`, "privately signal interest in a company", is
filed as a write with no surface and it HAS one** -- LinkedIn draws an
interest control on this card. Nothing here presses it and no tool does;
`company_about.interest_control` reports that it is drawn, because "no
surface" and "a surface nobody has fired" are different rows.

**No page load was added, no address was admitted, and no company Page was
opened.**

## 3. THE THIRD-PARTY QUESTION, ANSWERED AS FAR AS IT CAN BE

I was asked to establish whether a company Page carries a signal equivalent to
the durable record a member profile view leaves, BEFORE building anything that
opens Pages in bulk. **It does not resolve, and here is the shape of the
not-resolving rather than an assumption dressed as an answer.**

The member case is settled by an INSTRUMENT: `linkedin_who_viewed_me` returns
rows reaching 365 days back, so a profile view is demonstrably recorded and
demonstrably readable by the person it was spent on. That is the whole
argument of
`writes.PERMANENTLY_FORBIDDEN["load_a_third_partys_profile_to_measure_a_control"]`.

The organisation-side equivalent of that instrument is a Page ADMIN analytics
surface. **This account does not appear to hold one.** The tracked Manage
Pages capture heads "58 Pages" and returns **zero** hits for `admin`,
`Super admin`, `Page admin`, `analytics` or `visitors`; the whole surface is a
FOLLOWING manager. Grepping every tracked fixture for visitor-analytics
markers returns zero files.

**So the cost of a Page view is UNMEASURED from this account, and unmeasured
is not zero.** Two things follow and only the first is comfortable:

1. **The four reads above sidestep the question rather than answering it.**
   They are taken off a render he already performs. That is a true and
   sufficient reason to ship them, and it is NOT a finding that Pages are
   free to open.
2. **The remaining eight reads stay blocked**, and they are blocked on a
   measurement this account cannot take rather than on a ruling nobody has
   made. Recording which is which matters: a wave that reads "blocked" as
   "needs a ruling" will go and ask for one, and the ruling would be made on
   the same silence.

**The one route that would settle it** is a Page this account administers --
its visitor analytics would say directly whether LinkedIn identifies a Page's
visitors to its owner, the way `who_viewed_me` does for a member. Nobody
should spend a load hunting for one on the strength of this note; establishing
whether he administers any Page at all is a question for him, not for a probe.

## 4. THREE MEASUREMENTS THAT SHAPED THE CODE

**4a. The generic card harvest cannot reach these fields, and depth is not
why.** `dom.harvest_linked_cards` over the tracked fixtures at six depths
(1, 2, 3, 4, 6, 8): the card anchored on the `/company/.../life/` link is
**16 characters at every one of them** and carries none of the three meta
fields at any depth. The cause is the walk's own stop rule,
`if (keysWithin(node).size > 1) break` -- the About section holds two distinct
`/company/` targets (the name link and the Premium-insights link), so the
climb halts at the anchor before it reaches the element the meta lines hang
off. Raising `max_hops` cannot help, because the walk is not stopping for want
of budget. A test asserts this, so the day the generic walk CAN do it,
somebody gets to delete a function instead of maintaining two.

**4b. The container arrives before its contents.** `job_detail_following.html`
carries the `componentkey` container with a shimmer bar, no SDUI attribute and
**no text at all**. A reader anchored on the container alone would publish
"this employer has no followers" -- a fact about hydration wearing a fact
about the employer. `unhydrated` is a state of its own for that reason, and
`absent` is a different one.

**4c. The meta row is a ROW.** LinkedIn draws
`<industry> BULLET <size band> BULLET <N on LinkedIn>`, and the industry is
the only one of the three with no pattern of its own. Matched by position
alone it is whatever happens to sit in that slot, so the row's shape is
asserted first -- both bullets and the headcount line where the row says they
are -- and the industry read at an offset from an anchor that CAN refuse. A
missing bullet costs the industry and leaves the size band, which has a
pattern of its own.

## 5. THREE NUMBERS FOR ONE COMPANY, AND NONE OF THEM IS WRONG

On a single posting the same employer is described three ways:

    51-200 employees   the band the ORGANISATION declared
    304 on LinkedIn    the member profiles LINKEDIN attributes to it
    288 total          the Premium insights panel's own headcount

A reader that folded these into one `size` field would publish one of them as
the answer. They are separate fields and the docstring says which is which.
The third was found by accident: a test of mine asserted `"employees" not in
text` over every `/company/` card and went red on the Premium panel, which
legitimately says "Total employees". The word was never the claim; the
assertion was corrected to the capability rather than weakened.

## 6. THE DESCRIPTION IS COUNTED AND NEVER PUBLISHED

A ruling, not an oversight, and it is reversible by whoever disagrees.

The card's tail is the organisation's own free prose. **It is the only field
on this card a person's name can appear inside**, and no instrument in this
package can clear it: `census_substitute` was measured on 2026-09-05 returning
a person's name UNCHANGED, because a name carries no urn, no `/in/` path and
no digit run for a shape rule to catch. `membership_row` already ships that
defect and it is recorded as a known one. Adding a second instance the same
day, in a field that costs nothing to withhold, would be indefensible.

So `description_lines`, `description_chars` and `description_words` go out and
the prose does not -- enough to tell a company that wrote three paragraphs
from one that wrote none. `description_truncated` reports LinkedIn's own
*Show more*, so the character count is not read as a length.

**The case against this ruling, stated so it can be argued with:** the
description is public marketing copy on a page he can open himself, and the
hazard is a name appearing inside it rather than the field being a name. If
somebody rules that acceptable, the change is one line and the test that
asserts the withholding names itself.

## 7. SHOWN FAILING

Four mutations, in an isolated copy that REFUSES to run unless
`linkedin_server` resolves inside it -- the previous wave on this surface
mutated the live tree and said afterwards that nothing being lost was luck
rather than method. Four kills, zero survivors, each by its own named test:

    row_shape_check_removed          KILLED
    industry_shape_gate_removed      KILLED
    unhydrated_folded_into_absent    KILLED  (two tests)
    unnamed_keeps_its_booleans       KILLED

## 8. WHAT I DID NOT DO

* **The queued L1 live verification was NOT taken.** It asks whether
  `currentCompany` is really the employer's Page id, and it remains the one
  reading everything in the previous wave's build rests on. The route I
  designed for it is better than the one queued and is written down here so
  the next wave does not re-derive it: read the numeric ids off
  `/mynetwork/network-manager/company/` (already admitted, already read by
  `linkedin_followed_companies`), then load `/jobs/search/?f_C=<one of those
  ids>` -- also already admitted -- and call `linkedin_job_detail` on a
  posting it returns. **LinkedIn's own filter and this server's resolver then
  name the employer independently**, which is what the fixtures cannot do,
  because their two sanitisers used different name tables. Three loads, three
  seconds apart, with `dom.read_invitation_badge` read before and after. It
  would also verify `f_C` works, which `JOB-SEARCH-PARAMS` needs.
* **No allowlist pattern was added.** The previous wave's numeric-form
  proposal still stands unapplied and I did not apply it; the four reads
  shipped here needed no address, and a boundary opened with nothing behind it
  is still a capability that exists on paper.
* **The five writes were not fired and no write tool was built.** One of them
  gained a located surface and nothing more.
* **The About card has not been read on a LIVE posting.** Every reading here
  is off committed, sanitised fixtures plus one untracked raw capture. The
  parser is therefore verified against markup as of the day those were taken,
  not against today's.

## 9. TWO REDS FROM `bc5c2eb`, CLEARED -- AND THE FIX LANDED IN SOMEBODY ELSE'S COMMIT

Added 18:20. `bc5c2eb` left two reds in `tests/test_server_surface.py`:
`test_no_docstring_claims_a_write` and
`test_the_docstring_exemption_does_not_cover_the_reads`. Blast radius was
exactly one read tool and one sentence in it.

**The guard is right and the cause is small.** The sentence compared
`company_about`'s verdict shape to `company_id`'s, and the word it used to
draw that comparison is one of `readonly.WRITE_VERBS` -- the same word names
a reaction on this platform. A docstring is a PUBLISHED CLAIM, so a read
tool whose prose reads as though it writes is a disclosure problem rather
than a style one. This repository's rule that a surface may not print a
claim it cannot derive binds a claim it must not make just as hard.

**Rephrased, not exempted.** The second failing test exists precisely to
catch somebody reaching for `DOCSTRING_WRITE_TOOLS` instead.

**AND THE FIRST REPAIR WAS STILL RED, WHICH IS THE PART WORTH KEEPING.** It
explained the fix by NAMING the offending word in the new prose. The guard
matched it again, correctly: **it cannot tell a quotation from a claim, and
a guard that tried to would be a worse guard.** The note now describes the
term without spelling it, and says so, so the next reader does not
reintroduce the word while documenting it.

Verb hits were measured with `readonly.docstring_write_claims` itself
rather than guessed -- one hit before, zero after.
`tests/test_server_surface.py`: **50 passed.**

### The commit is not mine, and I am the author this time

I staged the fix as a single hunk with `git apply --cached` rather than
`--only`, because `server.py` also carried an uncommitted
`linkedin_events_home` hunk belonging to the events wave and `--only` would
have taken it. The staged diff was read line by line and was eight lines,
all mine.

**In the seconds between staging and committing, the events wave committed
`server.py` and my eight lines went in with it, as `a40e368`.** My own
commit then reported "nothing added to commit", which is how I found out.

**This is the exact mirror of section 1**, one hour later and with the roles
reversed: there I sweept 55 of the job-search wave's lines, here the events
wave swept 8 of mine. Both times `git status` and `git diff` were read
correctly and both times the tree moved in between. That is now the FIFTH
instance today, and it is worth stating plainly that **staging a precise
hunk does not narrow this window at all** -- the window is between the
staging and the commit, and it is open however small the change is.

**NOT REWRITTEN and NOT RE-LANDED.** The lines are byte-identical in
history, the guard is green at HEAD, and re-applying them would produce a
no-op commit claiming work that is already in the tree. The record is here
instead, which is the whole point of the protocol: the sweeper credits the
author, and where the sweeper has not yet noticed, the author says so.

**So this wave's work sits in three commits and one of them is not mine:**

    bc5c2eb  mine    the reader, the shaper, the tests
    25cb74e  mine    the credit for the 55 lines I swept
    a40e368  theirs  carries my 8-line docstring repair
