# The LinkedIn capability census -- the denominator, at last

**THE QUESTION.** "Everything I can do on LinkedIn directly -- can I do it
through this MCP?" It had never been answerable, because nobody had
established the denominator. Refusals can be grepped; what nobody considered
cannot. This is the count.

**METHOD.** Five parallel slices. Four walked LinkedIn's own Help Center as an
EXTERNAL taxonomy -- imported, never brainstormed, every row citing the page it
came from -- because an enumeration from memory measures the memory. The fifth
worked inward: 35 tools by evidence class, 12 writes by reversibility. No
browser, no session, no page load against the account. 3,205 lines across five
files in `_audit/_census/`.

## THE NUMBER

| state | count | share |
|---|---:|---:|
| COVERED-PROVEN -- a tool exists and is recorded working | 45 | 6.8% |
| COVERED-UNFIRED -- a tool exists, never run live | 27 | 4.1% |
| COVERED-CANNOT-DELIVER -- fired live, measured unable | 2 | 0.3% |
| EXCLUDED-RULED -- no tool, written reason exists | 227 | 34.3% |
| **GAP -- no tool, no reason: nobody considered it** | **360** | **54.5%** |
| **total enumerated** | **661** | |

By slice: jobs 132, profile/settings/privacy 240, messaging/content 120,
network/people 169.

## THE FINDING UNDER THE NUMBER

**ONE of twelve writes has ever changed anything on LinkedIn.** `save_job`,
proven four ways -- the ON label `"Unsave the job"` exists only because a real
save produced it. Everything else:

| write | state |
|---|---|
| `save_job` | LANDED |
| `apply_job` | fired once on a real posting, **did not submit** -- the gate held |
| `send_message` | fired live, **cannot deliver** (name addressing measured dead) |
| `update_profile_field` | fired once, failed `NAVIGATIONS ATTEMPTED: []`, repaired, never re-driven |
| `follow_company` | **never fired** -- see below |
| the other seven | no evidence of any kind |

**WHY THIS WAS MISCOUNTED, AND IT IS A TRAP FOR THE NEXT READER.** This corpus
uses PERFORMED / PERFORMABLE as a CAPABILITY word -- "the gate no longer
refuses this" -- never as a firing record. `_audit/2026-08-30-linkedin-writes.md`
headers `#8 follow a company. PERFORMED.` at line 273 and states
`writes performed: NONE. No confirm_token was passed to anything, by anyone, at
any point` at line 27 OF THE SAME FILE. A keyword count read the header and
missed the ledger. The lead made exactly that error and reported four working
writes where there is one.

So the gate machinery -- mint, consume, perform, verify -- has essentially
never been exercised end to end. THAT is the gap: not missing tools, a write
path nobody has driven.

## DEFECTS THIS SURFACED, RANKED BY WHAT THEY COST HIM

1. **The consent text lies about recovery.** `update_profile_field`'s
   `reversible_by` says the previous value is "which nothing here records" and
   the editor is unreachable "in either direction". Both false at HEAD:
   `writes.py:7724` reads the prior value before typing, `:8010` packages it,
   `:8040` returns it to him. He would decline a change believing it
   unrecoverable when the undo was already built. Three sibling defects sit in
   the same field, and **the tests pin the stale phrases**, locking the wrong
   text in rather than catching it.
2. **`publish_post` broadcasts at an audience nobody chose.** Signature is
   `(text, confirm_token)`; no visibility parameter, and the docstring never
   says visibility, audience, "Anyone" or "connections only". The gate names
   impressions while not naming who sees it.
3. **The system of record is stale about a repaired tool.** The 2026-09-02
   ship-and-repair of `update_profile_field` and `send_invitation` appears in
   ZERO audit files. `_audit/2026-08-31-linkedin-perform.md:3436` still tells a
   reader the action REFUSES.
4. **A per-address fix for a class defect.** `/close-accounts` and
   `/hibernate-account` are refused twice (forbidden list AND allowlist-miss);
   `/mypreferences/d/two-factor-authentication`, `/verifications` and
   `/job-application-accounts` are refused ONCE, by allowlist-miss alone. All
   five are closed today; three lack the second layer, and one of those is the
   account's second authentication factor.
5. **`send_invitation` can only reach whoever LinkedIn drew into the rail on
   his OWN profile** -- third-party profiles are permanently forbidden. The
   docstring says where it acts, never that this bounds WHO is invitable.

## WHERE THE GAP IS CHEAPEST

* **13 job read capabilities render on a page `linkedin_job_detail` ALREADY
  LOADS.** Parser work, zero extra page loads.
* **`/details/experience/` and `/details/education/` are already allowlisted
  and nothing navigates to them.** `my_profile` hands out both urls and reports
  `None` for both counts.
* **`who_viewed_me` already opens the analytics page and discards** the trend
  graph, top companies and top locations.
* **45 of the 88 messaging/content gaps are reversible, private, and notify
  nobody.** Saved posts is one allowlist entry from being `save_job`; hashtag
  follow is `follow_company`. The design budget went to the irreversible half.
* **Six job search filters are pure parameter work.** LinkedIn documents ten;
  the server offers four.

## WHAT IS STRUCTURAL RATHER THAN MISSING

* The read allowlist is **22 patterns** and reaches no Groups, Events,
  newsletters or hashtags -- most of one slice's 88 gaps in one line.
* `set_input_files` sits on the mutation-pattern list and appears in NO
  sanction and NO document. That single undiscussed omission closes every
  photo, video, document and attachment path -- 9 gaps nobody argued about.
* **72 of 105 settings exclusions are ONE ruling** (admitted by name or not at
  all). The ruling is correct, and it means nobody has an opinion about 71
  individual settings.
* **People search is 23 gaps and largely unconsidered** -- not ruled against,
  not weighed.

## HOLES IN THE DENOMINATOR, DECLARED RATHER THAN SCORED AS ZERO

661 is a **floor**, not a measurement.

* Two Help TOPIC pages render `0 articles` for products that plainly exist
  (Events, LinkedIn Live). An empty topic page reads exactly like a product
  with no features; both were recovered by search. **Anything else hiding
  behind an empty topic page is uncounted.**
* Groups and Events help trees not walked at all in the network slice.
* Notification categories are not public, so that block is counted at page
  granularity and the true toggle count is larger by an amount nobody outside
  LinkedIn can state.
* Four job filter chips are documented by no help page; if they exist the gap
  rises by four.
* Mobile-only surfaces, Recruiter, Sales Navigator, Learning, Services
  Marketplace and Pages-admin: deliberately unwalked.
* The intro-editor control set changed COMPLETELY between 2026-08-31 and
  2026-09-02, so six aiming claims rest on a one-day-old reading of a surface
  with a two-day half-life.

## THE ORDER THIS IMPLIES

1. **Fire the cheapest write end to end.** `update_setting` on dark mode: no
   audience, no other member can observe it, no feed, no notification, and the
   same tool sets it back. One round trip converts an UNKNOWN reversibility
   class to a measured one and exercises mint/consume/perform/verify where a
   defect costs nothing.
2. **Fix the consent text and the audience parameter** before any further write
   is fired -- they are what he reads when deciding.
3. **Harvest the free reads** -- the three items above, at zero page loads.
4. **Build the identifier route** that makes `send_message` real.
5. **Then the ruled gaps, by job-search value.**

Detail lives in `_audit/_census/` -- `jobs.md`, `profile.md`,
`messaging-and-content.md`, `network.md`, `mcp-inventory.md`.
