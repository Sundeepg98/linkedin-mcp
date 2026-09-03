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
| COVERED-PROVEN -- a tool exists and is recorded working | 45 | 5.9% |
| COVERED-UNFIRED -- a tool exists, never run live | 26 | 3.4% |
| COVERED-CANNOT-DELIVER -- fired live, measured unable | 8 | 1.1% |
| EXCLUDED-RULED -- no tool, written reason exists | 273 | 35.9% |
| **GAP -- no tool, no reason: nobody considered it** | **409** | **53.7%** |
| **total enumerated** | **761** | |

By slice: jobs 150, profile/settings/privacy 260, messaging/content 142,
network/people 209.

## THE NUMERATOR HAS NEVER MOVED

Three passes. The denominator grew every time and the covered count did not
change once:

| pass | enumerated | proven | what changed |
|---|---:|---:|---|
| 1 | 661 | **45** | the first walk of the Help Center topic tree |
| 2 | 721 | **45** | rulings found in test docstrings; Groups and Events recovered |
| 3 | 761 | **45** | LinkedIn's OWN help search replaced external search |

**Every re-check found a bigger hole and zero hidden coverage.** Three
independent slices reported the same shape in the same words -- jobs +18 all
GAP, network +34 all GAP, messaging/content +22 of which 21 GAP. That is the
strongest single result here: the uncertainty in this census is entirely in
the denominator, and it runs one way.

**761 IS STILL A FLOOR.** It is not converged: the stop condition was a flat
discovery curve and the curve has not flattened.

## THE INSTRUMENT THAT CHANGED THE NUMBERS

    https://www.linkedin.com/help/linkedin/search?q=<terms>

The parameter name is the whole trick: `?query=`, `?keywords=`, `?searchTerm=`,
`?term=` and `?text=` all return HTTP 400. It queries LINKEDIN'S OWN article
index, so unlike an external engine it cannot miss an article nobody crawled.
It should be the default for any further Help Center work, and it belongs in
the instrument register.

**AND IT CAUGHT A WRONG CLAIM, NOT ONLY MISSING ONES.** Pass 1 asserted a
hashtag-following capability sourced to `a528144`, which returns **HTTP 404** --
the url reached the census from an external engine serving a stale index with a
mangled locale suffix. Two independent index queries return no such article.
The row was retired IN PLACE rather than deleted. No topic-tree walk could have
caught that, and it is the only place a pass produced a false positive rather
than an omission.

## THREE WAYS AN ENUMERATION UNDERCOUNTS, RANKED BY HOW WELL THEY HIDE

1. **A thin index that reads as exhaustive -- the worst.** "Share Content" and
   "Post" each list SIXTY articles and still omit collaborative articles,
   newsletter analytics, poll voting, photo tagging, mention permissions, the
   verified-comments filter and article visibility. A 60-article listing looks
   complete. Nothing about it invites a second query.
2. **A topic page that renders `0 articles` for a product that exists** --
   Events and LinkedIn Live. An unwalked area reads exactly like an absent one.
3. **A product with no topic home at all** -- Sign in and security, Visibility,
   Notifications, Advertising data had to be assembled article by article.

## THE FINDING UNDER THE NUMBER

**ONE of twelve writes has ever changed anything on LinkedIn.** `save_job`,
proven four ways -- the ON label `"Unsave the job"` exists only because a real
save produced it. Everything else:

| write | state |
|---|---|
| `save_job` | LANDED |
| `apply_job` | fired once on a real posting, **did not submit** -- the gate held on its OWN logic, one of `_apply_submit_gate`'s five conditions. Both defects that firing exposed were about REPORTING the outcome, not causing the refusal. **So the next fire is the first real submit, not a de-risked repeat.** |
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
2. **`publish_post` broadcasts at an audience nobody chose -- and the control
   was SEEN.** Signature is `(text, confirm_token)`; no visibility parameter,
   and the docstring never says visibility, audience, "Anyone" or "connections
   only". This is not an unknown surface: a live capture of the composer
   dialog, 31 controls read, records "and an audience control" in three words
   at `_audit/2026-08-31-linkedin-perform.md:166`. Seen, written down, never
   named, never read, never wired.

   **The collision that hid it:** the spec's `residue` uses the word "audience"
   to mean REACH and quantifies it -- 275 followers, 103/308/1,284 impressions
   -- so the word is present and the SETTING is absent. **The gate tells him
   how many may see a post and never who may.** Closing it costs one read on an
   already-allowlisted address, which makes it the cheapest unclaimed
   capability in the inventory. It is a PRECONDITION of any `publish_post`
   fire, not a note.
3. **The system of record is stale about a repaired tool.** The 2026-09-02
   ship-and-repair of `update_profile_field` and `send_invitation` appears in
   ZERO audit files. `_audit/2026-08-31-linkedin-perform.md:3436` still tells a
   reader the action REFUSES.
4. **A per-address fix for a class defect -- and the class has TEN known
   members, not three.** `/close-accounts` and `/hibernate-account` are
   refused TWICE (forbidden list AND allowlist-miss). Machine-checked against
   all 23 forbidden substrings, these ten are refused ONCE, by allowlist-miss
   alone:

       /mypreferences/d/change-password        <- the password page
       /mypreferences/d/two-factor-authentication
       /mypreferences/d/verifications
       /mypreferences/d/member-cookies
       /mypreferences/d/job-application-accounts
       /mypreferences/d/profile-visibility-for-partners
       /public-profile/settings
       /uas/login
       /badges/profile/create
       /mwlite/settings                        <- an ENTIRE parallel mobile tree

   **Everything here is closed today.** Nothing is reachable, and this is not
   an open door. It is a defence-in-depth asymmetry: the fix taken on
   2026-08-31 was per-address when the thing found was a CLASS, and the class
   includes the account's password and its second authentication factor. The
   mobile tree is the sharpest instance -- a whole settings surface nobody
   enumerated, guarded by nothing but not being on a list of 22 patterns.
5. **`send_invitation` can only reach whoever LinkedIn drew into the rail on
   his OWN profile** -- third-party profiles are permanently forbidden. The
   docstring says where it acts, never that this bounds WHO is invitable.

## WHERE THE GAP IS CHEAPEST

* **13 job read capabilities render on a page `linkedin_job_detail` ALREADY
  LOADS.** Parser work, zero extra page loads.
* **`my_profile` DECLARES `experience_entries` and `education_entries`, fires
  live, and returns `None` for both by construction** (`server.py:1714-1715`).
  The lead first recorded this as "nothing navigates to them", which was the
  wrong diagnosis of the right symptom: the fields are declared and hardcoded
  `None`, so this is a tool that runs and cannot deliver two of its own stated
  outputs -- not a capability nobody considered. `skills_listed` is `None` on
  the same line.
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
* **File upload is closed, deliberately, and is ONE OPERATOR ANSWER FROM
  OPENING.** `set_input_files` sits on the mutation-pattern list and in no
  sanction, closing every photo, video, document and attachment path -- 9
  capabilities. **The lead first recorded this as "undiscussed" and was
  wrong.** `tests/test_readonly.py:310-341` carries the full reasoning, scans
  every module, plants a mutation to prove the pattern still bites, and
  asserts the kind absent from `SANCTIONED_MUTATIONS` BY NAME. Its argument:
  *"UPLOADING IS A DIFFERENT CAPABILITY FROM TYPING. A fill puts his words in
  a box; a file input puts a FILE from this machine into somebody else's
  inbox, chosen by a path string. Nothing in this package should be one edit
  away from that, and the operator has never been asked about it."* Nothing
  needs measuring first. It needs an answer.

* **AND THAT DISCREPANCY IS ITSELF A FINDING ABOUT THIS CENSUS.** Several of
  this repository's sharpest rulings live in TEST DOCSTRINGS rather than in
  `_audit/` -- `set_input_files` has ONE mention across 51 audit files, and
  that one is a zero count. A census reading only `_audit/` scores such a
  ruling as never-considered. **So GAP=360 is over-counted by an unknown
  amount, and EXCLUDED-RULED=227 is under-counted by the same amount.** The
  totals move in opposite directions from the topic-page hazard below, and
  neither correction has been measured. Any future pass should grep test
  docstrings before calling anything unconsidered.
* **72 of 105 settings exclusions are ONE ruling** (admitted by name or not at
  all). The ruling is correct, and it means nobody has an opinion about 71
  individual settings.
* **People search is 23 gaps and largely unconsidered** -- not ruled against,
  not weighed.
* **JOB SEARCH IS THE ONLY SEARCH.** No people, company or content search has
  an address on the allowlist at all. So several capabilities that LOOK blocked
  by a missing write are blocked EARLIER, by having no way to find the target.
  Also absent: company Pages (`/company/<slug>/`) -- which is exactly the
  slug-versus-numeric-id gap behind the follow/unfollow aiming failure -- and
  `/pulse/`, even though `/article/new/` is allowed.

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
