# The settings rest: one ruling built into a signature, one row moved off the boundary axis entirely, and six rows that name nothing

**CORRECTS:** `_audit/2026-09-03-linkedin-gap-blockers.md` -- row 58 is queued DECIDE at cost 2 as though a ruling bound it, when the ruling was already given and what binds is a transport capability with nowhere to be written; and six further rows are costed against addresses that do not exist.

In full: row 58 `PROFILE-PDF-DOWNLOAD` carries a boundary component of 0 and is
not a settings-family row at all. And across blockers 83, 31, 29, 48, 68 and 54,
**0 of their 9 census rows names an in-product LinkedIn address.**

Wave `settings-rest`, 2026-09-05. Eight blockers were assigned -- **the eight a
predecessor reached none of** (`_audit/2026-09-05-settings-tail.md` section 5).
This document covers all eight and is explicit about which were BUILT, which
were MEASURED OFF DISK, and which never had a page opened. Everything is
measured at the working tree of this date unless it says otherwise. No write
was fired. No boundary list was edited. **No settings pattern was written.**
Nothing was pushed.

---

## 0. THE HEADLINE, IN FOUR LINES

1. **`FEED-CONTENT-READ-RULING` is BUILT** -- the lead's ruling implemented in
   the SIGNATURE rather than in a filter, because the ruling itself named the
   reason a filter cannot work here.
2. **`PROFILE-PDF-DOWNLOAD`'s unsettled half is settled, and it moves the row
   off the boundary axis entirely.** This server cannot name a downloaded file,
   and in ATTACH mode there is nowhere to write the fix.
3. **The `allowlist +1` finding reproduces for a NINTH time, over a fresh set:**
   0 of 9 rows behind six blockers name an in-product address.
4. **A fourth evidence class, and it is weaker than any of the three named
   today:** `AUDIO-EVENTS-EXISTENCE` rests on a SEARCH SNIPPET. All three of its
   candidate Help Center articles 404, including the hub.

---

## 1. `FEED-CONTENT-READ-RULING` (row 49) -- BUILT

### 1.1 The ruling, and why it could not be discharged with a filter

The lead's ruling: reading the feed means reading other people's posts; counts
and relations only, never text or names; built structurally as
`recommendations.py` and `groups.py` were. And the clause that decided the
design:

> `census_substitute` returns a person's name UNCHANGED, so no shape-based
> guard will save you -- the property has to be in the SIGNATURE, not in a
> filter.

That is correct and it is measured elsewhere, not assumed here: a newsletter
title of the form `<publication> by <author>` passes through that predicate
intact, and the defect is live in a shipped gate one surface over.

The feed is the worst possible surface for a shape filter. Its payload is a
post BODY (a name is ordinary prose), an author's DISPLAY NAME (a name with
nothing around it), and a reason header (a name inside a sentence). Every one
defeats a shape detector completely.

### 1.2 What was built

`linkedin_server/feed.py`, a new module. Four public functions, and **the
guarantee runs in BOTH directions:**

| | the property | asserted by |
|---|---|---|
| IN | no public callable accepts a parameter outside a closed, declared set | a signature sweep over every public callable |
| OUT | no public callable returns any substring of its input | a recursive sweep of every string in every return |

**The IN half is the one that is new, and it is the ruling taken literally.**
`recommendations.py` and `groups.py` guarantee only the OUT half. That is
sufficient for a surface whose input is a list of hrefs; it is NOT sufficient
here, because the obvious next commit on a feed reader is a `text=` or
`author_name=` parameter added in good faith by somebody who intends to count
something with it. **A leak needs a route in before it needs a route out.**

| function | what it answers |
|---|---|
| `author_kind(href)` | which of six entity KINDS authored a row -- never which entity |
| `feed_tally(hrefs)` | rows, identified, distinct authors, by kind, refusals |
| `authorship_concentration(hrefs)` | whether ONE author dominated, as an integer |
| `overlap(first, second)` | how many authors two sets share -- counts only |

**No identifier is published for ANY kind, including the two where one would
arguably be safe.** `groups.py` publishes an opaque numeric group id and argues
correctly that no digit run is a person's name. That argument is available here
for groups and events and is declined, because a UNIFORM guarantee is
certifiable by a signature sweep in one sentence while a per-kind one needs a
case analysis that drifts the first time a seventh kind is added -- and because
a personal-brand Page is named after its owner, so the one kind where
publishing an identifier looks obviously harmless is a kind where it is
sometimes a name.

**The cost is stated rather than hidden:** a caller cannot ask which author
dominated the feed, only that one did. `authorship_concentration` answers that
as an integer, which is the question that was worth asking.

### 1.3 The branch its two siblings do not have

`groups.py` and `recommendations.py` each nominate ONE kind their surface is
about and refuse every other as foreign. The feed has no privileged kind -- a
member post and a company post are both ordinary content -- so foreign is not a
category here. That removes a refusal and creates a new one: a path carrying
TWO entity segments would, under first-match-wins, be attributed to whichever
check ran first. **An ordering accident is not a classification**, so it is
refused outright.

### 1.4 Three mutation controls, each killing exactly its intended tests

The module was copied before each edit and restored from that copy, verified
`cmp`-identical rather than retyped -- a rollback you retype is not a rollback.

| mutation | result |
|---|---|
| ambiguity check -> `if False` | **2 failed, 26 passed** |
| publish the segment instead of the shape literal | **2 failed, 26 passed** |
| add a `text=` parameter to `feed_tally` | **1 failed, 27 passed** |
| restored, three times | **28 passed** |

**THE FIRST MUTATION CORRECTED THIS WAVE'S OWN DOCSTRING**, and the correction
is worth more than the branch. Its author wrote that neutralising the check
would resolve `/company/<x>/people/in/<y>` to `"company"`. Measured, it resolves
to **`"member"`** -- because the module inherits `shape._CENSUS_ENTITY_HREFS`'
ordering, in which `in` comes first. **A company's people directory attributed
to a PERSON is worse than the error that was guessed at**, on a surface whose
whole ruling is about not naming people. And an assertion of `kind != "company"`
would have PASSED under the mutation, which is the concrete reason a mutation is
run instead of an input being reasoned about.

### 1.5 The corpus measurement -- and it went against the branch I was proudest of

`scripts/_probe_feed_kinds_in_corpus.py` runs the module over every tracked
capture in `tests/fixtures` and `_audit` -- real LinkedIn markup off his
signed-in session, no browser attached, no page opened, no boundary consulted.

    documents read                       35
    named for the feed                    0
    anchors handed in                  1353
    resolved to an author               217   (81 distinct)
    kinds seen                            5   company 91, member 42,
                                              event 54, group 20,
                                              newsletter 10
    kinds NOT seen                        1   school
    entity_root_carries_no_identifier     3
    not_an_entity_href                 1133
    AMBIGUOUS TWO-ENTITY PATHS            0

**The ambiguity branch did not fire once in 1353 real anchors.**

That is a result about the branch and it is NOT a refutation, for a reason the
probe prints rather than leaves to be inferred: **the corpus contains no capture
of the feed** -- 0 of 35, checked and printed -- and the two-entity shape was
asserted FOR the feed. A branch deleted on a corpus that could not contain its
input is deleted on no evidence at all. It stays, and it stays labelled.

**The zero is worth something only because the same run reported presences.**
217 resolutions across five of six kinds, and the root branch firing 3 times, in
the same sweep. A blind reader and a reader seeing nothing are
indistinguishable from outside; this one is demonstrably not blind. The unseen
kind is the honest companion finding: this corpus holds no school links either,
so that zero says nothing about LinkedIn.

### 1.6 Why a corpus sweep and not a live read, because it is the finding's main caveat

`page.evaluate` and every attribute reader are TAINT SOURCES in
`tests/test_page_text_is_never_printed.py`, whose sanitiser set is
**deliberately empty**. So anything derived from a live page that reaches a
`print` is refused by a shipped guard, correctly. The sanctioned route is a
reader in `linkedin_server/` whose return a probe prints -- and adding one
contradicts `feed.py`'s own "ships no DOM reader" and moves pinned inventory
counts, an enumeration class no targeted run clears.

**The module deliberately ships no DOM reader**, for the reason the newsletter
wave gave for declining one: an invented selector fails closed and returns "his
feed has no authors", which is exactly the answer the surface exists to
produce. Whoever opens the page first writes that half, and their zero will
mean something because this half already refuses to publish a name.

### 1.7 Boundary cost: ZERO, re-derived rather than recalled

`readonly._ALLOWED_URL_PATTERNS` already admits the feed root, and
`/feed/update/` is separately admitted. **No pattern added, no list edited, no
digest touched.** The ranked table charges this row "boundary: none", and that
is correct.

---

## 2. `PROFILE-PDF-DOWNLOAD` (row 58) -- the unsettled half, settled

### 2.1 The predecessor named the half it had not answered, and it was right to

`_audit/2026-09-05-settings-tail.md` section 4 established that
`https://www.linkedin.com/in/me/` is ALREADY ALLOWED, so the row carries no
boundary cost, and said plainly: *"I answered the address and not the
question."* The question was whether the download lands as a file this server
can name.

### 2.2 It does not, and the reason is structural

Measured over tracked files only:

    accept_downloads      0 tracked files
    expect_download       0
    suggested_filename    0
    save_as               0
    downloads_path        0
    context creation      1 site -- browser.py, and it is LAUNCH mode

`accept_downloads` is a **context creation option**. In ATTACH mode -- what the
whole fleet and every tool runs -- `cdp_bridge` never creates a context: it does
`list(client.contexts)` and returns `contexts[0]` verbatim, with its own comment
explaining that a new one would be signed into nothing. **A context this package
did not create is a context whose download options it did not set, and there is
no call site in that path where it could.** Not "nobody wrote it yet" -- there
is nowhere to write it.

### 2.3 So the row is mis-filed, in the direction that makes it look cheap

It is queued DECIDE at cost 2 as though a ruling were the binding constraint.
The ruling was already given: his own profile as a file is a read of his own
data. What binds is a transport capability nobody has built, on a surface that
is not this one. **The correct re-file: blocker is a missing download
capability in the browser transport; the boundary component is 0; and it is not
a settings-family row at all.**

### 2.4 Pinned as an asserted invariant, not as a paragraph

`tests/test_profile_pdf_download_is_blocked_on_transport.py`, 9 tests. **The
detector is factored out of its assertion** and the order is the point: it is
shown saying YES to synthetic sources that carry the capability, then NO to
sources that do not, and only then aimed at the real package. Without the first
step, "no capability found" is indistinguishable from a grep with a typo in it.
It also distinguishes *creates a context without the option* from *creates no
context at all*, because those are different findings with different remedies.

A docstring is the one class the correction machinery cannot bind, and an audit
document is a dated record that rots harmlessly -- while a claim about what the
code CAN DO is read as current truth. If somebody adds download handling
tomorrow this turns red and they must read why the row said what it said.

### 2.5 A disagreement worth recording, because it was mine

My first re-take of this census read `accept_downloads` **38** and
`expect_download` **14**, and appeared to refute the measurement outright. It
had swept `venv/` -- Playwright's own source. Scoped to tracked files it reads
**0** everywhere.

**The corpus was the defect, not the finding.** This is the standing scar about
building your own version of a shipped measurement, arriving one more time:
when two instruments disagree, date and scope both readings before adjudicating
either. The relayed measurement was right and my re-take was wrong.

---

## 3. THE SIX REMAINING BLOCKERS -- 0 of 9 rows name an in-product address

Row-level lookup delegated and cross-checked against two independent derived
artifacts (`_audit/_scratch/_retire-rows-blind-check.md` and
`_audit/_scratch/_route-gap-rows.tsv`) in addition to a direct read of the raw
census file. Detail: `_audit/_scratch/_settings-rest-rows.md` (untracked
scratch).

| blocker | row id(s) | R/W | file:line | names an in-product address? |
|---|---|---|---|---|
| 83 `REPORTING-FLOWS` | `M38` | 1W | `_census/messaging-and-content.md:369` | no -- Help Center id only |
| 31 `NO-URL-AT-ALL` | `N25` | 1W | `_census/profile.md:465` | **no -- the row says so itself** |
| 29 `AUDIO-EVENTS-EXISTENCE` | `L6` | 1W | `_census/profile.md:416` | no -- and not even a live Help Center id |
| 48 `ALL-FILTERS-PANEL` | `15`, `16` | 2R | `_census/jobs.md:146`, `:147` | no -- Help Center id each |
| 68 `PICKER-SURFACES` | `M16`, `M17` | 2W | `_census/messaging-and-content.md:347`, `:348` | no -- Help Center id only |
| 54 `RESUME-TOOLS-SURFACE` | `M11`, `M12` | 1R/1RW | `_census/profile.md:434`, `:435` | no -- **not even a Help Center id** |

    ROWS NAMING AN IN-PRODUCT ADDRESS: 0 of 9.

**A Help Center article id is a documentation citation, not a navigable page.**
This is the ninth instance of a finding this project has now made eight times
before, and it reproduces cleanly over a set nobody had checked. The standing
rule holds and this wave obeyed it: **an unnamed `+1` can only be discharged by
a family pattern, which is the boundary trap in a costume. No pattern was
written.**

### 3.1 Three of the six are individually more interesting than the shared finding

**`NO-URL-AT-ALL` (31) is correctly named, and that is unusual.** Row `N25`'s
own text says the capability is reached by an in-page nav step and *"no URL, so
no address to rule on"*. Its boundary is charged "none" rather than "allowlist
+1" -- so unlike its five neighbours this row is costed honestly. **The blocker
is not a missing measurement; it is a statement that the thing has no address to
measure.** It should be re-filed as a nav-path capability, not queued MEASURE.

**`AUDIO-EVENTS-EXISTENCE` (29) rests on a SEARCH SNIPPET, and this is a fourth
evidence class.** The census footnote at `_census/profile.md:946` records that
three candidate Help Center URLs 404 -- including the hub article. So the row's
evidence is not a page anybody opened; it is a search result describing a page
that does not resolve.

Today's three existence classes were:

    "the platform has no such surface"      permanent, universal
    "the page reads zero for this account"  reversible tomorrow
    "the data model ships, no surface drawn" 146 hashtag hits, no surface

**This is a fourth and it is weaker than all three: NOBODY HAS LOOKED, and the
citation that appears to be a look is a 404.** It must not be retired as an
absence and must not be queued as a measurement of a surface -- the first unit
of work is establishing whether the feature exists at all, and the row's own
citations cannot do that.

**`RESUME-TOOLS-SURFACE` (54) is filed BLOCKED with NO NAMED UPSTREAM BLOCKER.**
Its stated reason is "entitlement unverified". Five places were searched -- the
ranked doc full-text, the settings-tail predecessor doc, both derived TSVs,
`_premium-reader-slice.md`, and all three mentions of `PREMIUM-READER-NOT-BUILT`
-- and no upstream blocker is named anywhere. Reported **UNFOUND**, with the
search trail recorded, rather than guessed at.
`PREMIUM-READER-NOT-BUILT` is a different and already-scoped blocker
(`/premium/my-premium/`, InMail balance) and is **not** this row's upstream.

**A row filed BLOCKED against nothing is worse than a row filed GAP**, because
BLOCKED reads as "somebody established a dependency" and nobody did. It is the
same shape as the `allowlist +1` placeholder: a state word standing in for an
unknown.

---

## 4. THE BOUNDARY TRAP -- what this wave did about it

**Nothing, deliberately, and that was the assignment.** No settings-family
pattern was written; no narrow anchored pattern was written either, because
**not one of the six rows names an address to anchor one to.** The finding IS
the deliverable for those rows.

The standing invariant was re-run rather than trusted:
`tests/test_the_settings_boundary_refuses_account_deletion.py` passes at this
tree. It was written against a 29-pattern allowlist and still refuses at **31**,
so it has been exercised across two unannounced widenings by other waves --
which is the right shape for a boundary test.

Allowlist re-derived by importing the module and counting, not read from a
handoff document: **31**.

---

## 5. WHAT I DID NOT REACH, stated as a list rather than buried

**No page was opened by this wave. Not one live read was taken.** Six of my
eight blockers are queued MEASURE and I measured their ROWS, not their
SURFACES. That distinction is load-bearing and I am not going to blur it:

| # | blocker | what was established | what was NOT |
|---|---|---|---|
| 83 | `REPORTING-FLOWS` | row names no address | nothing about the surface |
| 31 | `NO-URL-AT-ALL` | the row says it has no url | whether the nav path exists |
| 29 | `AUDIO-EVENTS-EXISTENCE` | its evidence is a 404'd citation | **whether audio events exist** |
| 48 | `ALL-FILTERS-PANEL` | both rows name no address | whether the panel draws |
| 68 | `PICKER-SURFACES` | both rows name no address | whether pickers draw |
| 54 | `RESUME-TOOLS-SURFACE` | no upstream blocker is named | the entitlement |

Also not reached: a LIVE feed read, which would have converted `feed.py`'s
remaining asserted claim (two-entity paths occur ON THE FEED) into a
measurement. The corpus sweep is a weaker instrument aimed at the same claim and
it says so on its own output.

**Rows moved: 2 of 12** (49 built, 58's second half settled), **plus 6 blockers
re-costed on a measured row census and 3 of those individually characterised.**

---

## 6. PROVENANCE

* No browser attached, no page opened, no badge read, no navigation, and
  therefore no boundary consulted at run time by any instrument here.
* No write fired. No boundary list edited. No denylist touched. **No settings
  pattern written.** Nothing pushed.
* Gate verdicts and counts taken at this working tree. **This is a reading
  dated by the TREE, not by a SHA** -- a dozen waves are writing.
* Two closed-form slices were delegated and both deliverables are files:
  `_audit/_scratch/_settings-rest-rows.md` and
  `_audit/_scratch/_settings-rest-download.md`. Both were reviewed before use,
  and the download census was independently re-taken -- see 2.5, where my
  re-take was the one that was wrong.
* No name, member id, slug, urn, phone or page text appears in this document,
  in `feed.py`, in either test file, or in the probe's output. The probe prints
  integers and words drawn from two closed module-level vocabularies.

---

## 7. FREEZE -- numbers RECOMPUTED at freeze, not re-read

    commits            4     812abc3  feed.py + tests (the ruling)
                             8c028d3  corpus probe + the measured correction
                             f86f27f  row-58 transport invariant
                             (this document)
    files added        4     1 module, 2 test files, 1 probe
    tests added       37     28 feed + 9 transport
    AI attribution     0     verified per commit
    sweep at gate      PASS  0 hits across 354 tracked files
    allowlist         31     re-derived by import, not read from a document
    pushed          NOTHING
