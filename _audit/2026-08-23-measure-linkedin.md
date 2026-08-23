# linkedin, 2026-08-23 -- the three blockers were reads, and the reads are done

Every number is at `oldsha22`. Reads landed at `oldsha04` and were verified green ALONE in a
bare worktree (1038 passed, 6 skipped -- the 6 need a sibling jobcore checkout) before the gate
went on top. Nine live page loads, one at a time, nothing clicked.
**986 -> 1055 passed. CI success on `oldsha22`, run id 32625271124**, all three matrix legs.

> **THE COUNT IN BOTH COMMIT MESSAGES SAYS 1044 AND IS WRONG BY 11.** It was a local run taken
> BEFORE the commit, when eleven of this wave's own files were still untracked --
> `test_no_committed_credential.py` parametrises over `git ls-files`, so tracking 6 scripts,
> 4 fixtures and 1 test module added **exactly 11** tests. Both numbers are true of different
> trees; only 1055 is true of the tree that shipped, and 986 was CI's number at `oldsha05`, so
> 986 -> 1055 is the only same-instrument comparison. Corrected here rather than quietly, and
> the happy half is real: those four new fixtures are now swept for credential shapes by that
> parametrisation, automatically, because they are tracked.

1. **TOGGLE DIRECTION -- FOLLOW SOLVED, SAVE SOLVED FROM A DIFFERENT SOURCE.** On the posting
   page the control is `aria-label="Follow"` when not following and `aria-label="Following"`
   when following, measured by loading a posting from a company he already follows. The two
   carry **byte-identical class attributes** and the page has no `aria-pressed` anywhere -- the
   accessible name is the entire signal, which is the anchoring rule as a measurement rather
   than a preference. `linkedin_job_detail` now reports it at **no extra page load**, off the
   page the write would act on. **Save is different and I will not paper over it: the save
   control's ON state has never been observed and cannot be -- his saved list is EMPTY (0 saved,
   0 applied), so no posting on the account can show it.** Save takes its direction from
   `linkedin_saved_jobs`, verified today: the tracker reports LinkedIn's own per-tab count and
   its empty state, so an empty list is distinguishable from a failed read. That is a different
   source, not a weaker one, and the spec names it.

2. **REVERSIBILITY -- all four REVERSIBLE, measured by observation, no write performed.**
   *save*: his saved surface renders an **Unsave** control that is absent from `?stage=applied`,
   so it is bound to the saved stage rather than being furniture. *unsave*: returns the posting
   to the state where `aria-label="Save the job"` renders, on the posting itself. *follow*: the
   strongest -- LinkedIn writes the inverse action into the control's own accessible name on
   three surfaces (`Click to stop following X`, `Following, click to unfollow X`, `Following`).
   *unfollow*: the OFF state renders `Follow` on every surface measured. **The field that nearly
   went missing is `reversible_by`:** "reversible" reads as "this tool can undo it" and for
   follow that is **false** -- no unfollow is sanctioned, so a follow performed here is one only
   he can reverse by hand. Residues kept, not swallowed: whether re-saving restores the saved
   DATE and hence list order; and **who saw a follow**, which no read reaches.

3. **OPEN TO WORK -- the capture already existed, and it says "Recruiters only".**
   `profile_topcard.html` and `..._hydrated.html` have carried `Open to work <dot> Recruiters
   only` since 22 Aug, at **both** renders; a live load today agrees. So: no new fixture, no
   extra page load, and **no allowlist entry** -- `/in/me/` was always on it. `linkedin_my_profile`
   now reports the state and the **audience**, and the gate names who can see the DESTINATION:
   all-members draws a green frame a current employer and colleagues can read. Specced with three
   states, so the destination must be named rather than derived. **It has no surface**: the
   editor is a modal nothing has loaded, so `url_template` is `None` and `assert_write_url`
   refuses it -- a gate may not name a target surface nobody has opened.

4. **THE HAZARD THAT WOULD HAVE SHIPPED SILENTLY.** New read `linkedin_followed_companies`
   (Manage Pages; one narrow allowlist pattern, no query string) renders **20 rows under a
   heading saying 58 Pages**, and 10 before it settles. "Absent from the list" is therefore not
   "not followed", and the tool answers **unknown**. Same three-valued discipline on the posting:
   a control that has not rendered is `unknown`, never `not_following` -- measured, the same
   posting drew no control before settling and `Following` after.

5. **MEASURED IN PASSING, and it is the sharpest evidence for a rule this repo already had:**
   the posting captured 22 Aug carries **15** `data-view-name` attributes; the one loaded 23 Aug
   carries **0**. Same surface, same account, one day. A parser anchored there returns nothing
   this morning with every test still green. Surface-specific, not a platform removal -- Manage
   Pages, minutes later, carried 31 -- and it is asserted against the fixtures, not against
   LinkedIn.

6. **UNCHANGED, as ordered.** `perform()` still raises; no mutating Playwright call is in the
   package; scanners report zero across all 17 modules; `test_readonly.py` and
   `test_launch_boundary.py` are **zero-line diffs** (`git diff --numstat` empty).
   `linkedin_notifications` and `linkedin_logout` were never called. The Manage-Pages harvester
   uses plain locators plus an XPath hop -- *the largest ancestor holding exactly one match*,
   stated literally -- rather than an injected script, so the boundary was not asked to grow an
   `INJECTED_SCRIPTS` entry to accommodate a read.

7. **A NEAR MISS, pinned rather than designed around.** The tool was going to be
   `linkedin_follow_state`, and `name_implies_write` **rejects** that name. Renaming until a
   guard stops complaining is the loophole closed last commit, so the rejected name is asserted
   to still be rejected beside the reason the chosen one is not that move:
   `linkedin_followed_companies` is a past-participle noun phrase, same grammar as
   `linkedin_saved_jobs`, describing a list rather than an act.

8. **PRIVACY, and one live hole found.** `_audit/` was **not gitignored** while ~14 MB of raw
   captures with his name, member ids and live tracking tokens sat there untracked -- one
   `git add -A` from the remote. Now ignored; nothing was ever committed. **Correction: that remote is
   PRIVATE** -- `gh repo view --json visibility` says so, and `oldsha04`'s message calls it public. Three
   agents including me inferred "public" from a remote existing and a push working, which is not
   evidence of anything; visibility comes from that command alone. Every alarm ran in the safe
   direction and the scrubbing was right on its merits either way. Fixtures replace
   20 company names, ids, slugs, his name and his city, and **neutralise follower counts**: an
   exact count is close to a unique key for a Page and twenty side by side reconstruct the real
   follow list even with every name changed. The risk is in the SET, not the item, which is why
   these are neutralised while the older single-count fixture is untouched. The artefact proving
   all this (`_audit/_fixture_sanitisation_check.txt`) is itself uncommittable, because it
   enumerates the strings it removed.

9. **CONTROLS.** Every refusal added has one: the three direction refusals against a
   `_direction` that raises unconditionally; the no-surface refusal against a door that has
   stopped opening; the UNMEASURED path against a renderer that has lost the ability to say it
   (all four real specs are measured now, so that control is driven at a synthetic spec -- a rule
   dies by never being exercised again, not by repeal). The read tests were mutation-checked:
   **31 mutants, 31 killed, 0 survivors**, including "absence read as not_following" and
   "`parse_open_to_work` returns False for an unread card".

10. **WHAT I DID NOT DO, deliberately.** No `unfollow` spec -- the operator's ruling named
    follow, and adding its inverse would widen the sanctioned set without an order. No capture of
    the Open To Work editor, so it stays surface-less. The Interests **Companies** tab is
    unreachable: a client-side radio with no url and no href anywhere in the DOM, the
    jobs-tracker shape without the `?stage=` escape hatch. And `/mynetwork/.../people-follow/following/`
    contains `/follow` and is refused by the forbidden-substring list before the allowlist is
    consulted -- the company url happens not to contain it. **That is luck, not design**; the
    right response to the luck running out is to leave the people list unread, never to shorten
    the forbidden list.
