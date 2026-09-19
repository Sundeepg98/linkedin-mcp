# network-tail -- 22 rows across five blockers, and the overreach is filed on the wrong one

Wave `network-tail`, 2026-09-05. Blockers 21, 52, 63, 11, 60 from
`_audit/2026-09-03-linkedin-gap-blockers.md` section 3.

**Everything below was measured offline against the working tree by
`scripts/_probe_network_tail_boundary.py`. No page was loaded. No browser was
opened. `linkedin_server/readonly.py` is BYTE-UNCHANGED by this wave** -- see
"What I did not do", which is the longer half of this document.

    tree measured    working tree at 6456701, readonly.py clean (git status empty)
    allowlist        29 anchored patterns    (recomputed, not read off a note)
    denylist         33 forbidden substrings (recomputed)
    probed           18 candidate addresses + 3 controls

The freeze file records the allowlist at 27 -> 28 as of the newsletter wave's
close. It is 29. A number quoted from a note is a reading with a timestamp; this
one is taken at freeze time, which is the standing rule.

---

## 1. THE HEADLINE: `ENDORSE-SUBSTRING-OVERREACH` DOES NOT REPRODUCE

I was briefed that row 63 is the same defect fixed for `linkedin_connections`
on 2026-09-03 -- a forbidden substring over-matching and catching a READ
address it was never meant to catch. **It is not. Measured:**

    [R] /in/me/details/skills/                    ALLOWED   clean
    [R] /in/me/details/skills/?detailScreenTabIndex=0
                                                  ALLOWED   clean

`/in/me/details/skills/` is the address the census itself names for the read
row -- row `N 114` reads *"Lives on HIS OWN skills page, which IS readable
(`/in/me/details/skills/`)"*. **The boundary already allows it, cleanly, and
the substring `/endorse` never touches it.** The read row is not blocked by
the denylist and never was.

What `/endorse` does refuse is the write side, and refusing it is the entry
working as designed:

    [W] /in/me/details/skills/endorsements/       REFUSED-FORBIDDEN  matched '/endorse'
    [W] /in/me/endorse/                           REFUSED-FORBIDDEN  matched '/endorse'
    [W] /profile/endorse                          REFUSED-FORBIDDEN  matched '/endorse'

**RULING: `/endorse` is not narrowed, and no narrowing is owed.** The blocker's
1R needs no boundary change (it is already allowed); its 2W are write acts and
a write guard refusing a write is not overreach. **The most dangerous edit in
this repository turned out not to be needed** -- which is the result I wanted
and not the one I was sent to produce.

**HONESTY MARKER ON THE THREE WRITE ADDRESSES.** I did not observe those three
addresses on LinkedIn. They are route SHAPES I constructed to exercise the
substring, and the finding they support is about the GATE, not about
LinkedIn's URL space. `/in/me/details/skills/`, by contrast, is the census's
own recorded address. The two claims have different evidence and the document
says which is which rather than letting the table imply they are alike.

**The row is RE-FILED, not retired.** Its real blocker is that no reader
exists for the endorsements-received surface, which is a BUILD on an already-
admitted address -- the cheapest class of row there is, and the same shape as
the company wave's five rows off an already-loaded posting. It should not sit
in a DECIDE queue behind a denylist question that has now been answered.

---

## 2. THE OVERREACH IS REAL AND IT IS ON ROW 52, `PEOPLE-FOLLOW-LISTS`

The defect I was briefed to find exists. It is one blocker away.

    [R] /mynetwork/network-manager/people-follow/following/
                                                  REFUSED-FORBIDDEN  matched '/follow'
    [R] /mynetwork/network-manager/people-follow/followers/
                                                  REFUSED-FORBIDDEN  matched '/follow'
    [R] /mynetwork/network-manager/company/       ALLOWED            clean

**Two READ addresses refused by `/follow`, a substring that exists to stop this
server FOLLOWING somebody.** That is exactly the `linkedin_connections` shape:
a write guard matching a read address. And the third line is the corroborator
-- a SIBLING under the identical parent path is already admitted and read
today, so the family is not in question, only these two leaves.

The rows: `N 38` (view the list of people you follow), `N 44` / `P L2b` (own
follower list -- `P L2b` records *"NOBODY HAS LOOKED"*).

**A third instance, found in passing:** `/feed/follows/` is also
REFUSED-FORBIDDEN on `/follow`. It is a read. It is not worth admitting -- see
section 4 -- but it means `/follow` over-matches at least three read addresses,
not one.

### The remedy is an EXEMPTION, not a narrowing, and that distinction is the ruling

**DO NOT shorten `/follow`.** This repo already has the right mechanism and has
used it twice: `_FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS`, an ANCHORED-pattern
table that lets one named url carry one named substring while the substring
keeps its full bite on everything else. It is how `/messaging/compose` with a
recipient was admitted, and how the connections list was admitted on
2026-09-03.

A narrowing subtracts reach from a guard globally and forever. An exemption
adds one anchored address and leaves the guard's reach untouched -- and the
address then needs BOTH gates, the exemption saying which substring it may
carry and the allowlist saying it is a permitted read. Neither alone admits it.

### SPEC, ready to apply -- allowlist +2, exemptions +2, denylist UNCHANGED

I am handing this over rather than applying it. The reason is in section 6.

    _ALLOWED_URL_PATTERNS  (+2, anchored, no query string)
      ^https://www\.linkedin\.com/mynetwork/network-manager/people-follow/followers/?$
      ^https://www\.linkedin\.com/mynetwork/network-manager/people-follow/following/?$

    _FORBIDDEN_SUBSTRING_PATTERN_EXEMPTIONS  (+2, each exempting exactly {"/follow"})
      the same two anchored patterns

    _FORBIDDEN_URL_SUBSTRINGS  UNCHANGED. 33 entries before and after.
                               "/follow" and "/unfollow" both keep full reach.

**No query string, deliberately.** A query is where a filter naming a person
would arrive, and nothing in this package builds one. Same reasoning the
connections-list entry records for itself.

**THE PROOF THE NEXT WAVE OWES BEFORE COMMITTING, and it is not optional:**
plant the acts the entry exists to stop and show each still refused with the
exemption in place --

    /in/me/follow/             must stay REFUSED-FORBIDDEN on '/follow'
    /company/<slug>/follow/    must stay REFUSED-FORBIDDEN on '/follow'
    /company/<slug>/unfollow/  must stay REFUSED-FORBIDDEN on '/unfollow'
    /feed/follows/             must stay refused (NOT admitted by this change)
    either admitted url + "?"  must stay refused (the anchor is load-bearing)

All five are already in `scripts/_probe_network_tail_boundary.py`'s candidate
set or its controls, so this is a re-run, not new work.

**AND A PAYLOAD WARNING THAT IS NOT A BOUNDARY QUESTION.** Per the lead's own
13:00 split -- *the boundary decides what may be OPENED, the shaper decides
what may be SAID* -- opening these two pages settles nothing about publishing
them. **Both pages are lists of PEOPLE.** `census_substitute` returns a
person's NAME UNCHANGED, measured by the newsletter wave, so no shape guard
saves a reader here. A follower-list reader must emit COUNTS and RELATIONS
only. Copy `groups.py`, which is structural rather than filtered: no name is a
parameter of any function in it, asserted on `inspect.signature`.

---

## 3. `SERVICES-PAGE-SURFACE` -- the lead's ruling holds, and the write split was wrong

Ruling as briefed: it is his own services page, reads are fine; the ten writes
are outward-facing changes to how he presents professionally -- design and gate
them, fire none. I did not fire any. I did not design them either (section 6).

**The ledger costs this at `allowlist +1`. Measured, that is right for the read
and incomplete for the writes:**

    [R] /services/page/           REFUSED-NO-PATTERN  no forbidden substring; no allowlist pattern
    [W] /services/page/create/    REFUSED-FORBIDDEN   matched '/create'
    [W] /services/page/edit/      REFUSED-FORBIDDEN   matched '/edit/'
    [W] /services/page/reviews/   REFUSED-NO-PATTERN  no forbidden substring; no allowlist pattern

### CORRECTED, SAME SESSION, ONE COMMIT LATER: `allowlist +1` IS NOT OWED EITHER

The paragraph that stood here read the `+1` off `/services/page/` and called it
correct. **It is not, and the error is the same one section 1 catches: costing
a row by its SURFACE when the boundary gates an ADDRESS.**

Row `P H11`, the 1R of this blocker, is *"the `Providing services` section AS
RENDERED ON THE PROFILE"*. That is not `/services/page/`. It is his own
profile, and:

    [R] /in/me/                        ALLOWED             clean
    [R] /in/me/details/services/       REFUSED-NO-PATTERN
    [R] /services/page/                REFUSED-NO-PATTERN

**`/in/me/` is already admitted and this server already loads it today.** The
read row costs ZERO allowlist entries. `/services/page/` is a different surface
serving the ten WRITES, and admitting it buys no read row at all.

**THE RENDER GATE IS UNMEASURED AND I AM NOT CLAIMING THE READ WORKS.** This
repo has already been bitten: a tabbed category's rows are not in the document
until its tab is pressed, and the Companies category rendered ZERO on a live
396909-character profile read while holding at least 20 rows in fixtures. I do
not know whether the services section renders on a passive profile load, and a
zero taken without pressing would be a fact about the instrument. **What is
settled is the boundary; what is open is the render**, and those are different
claims.

**THIS IS NOW A PATTERN ACROSS TWO OF MY FIVE BLOCKERS AND IT GENERALISES.**
Row 63's read was already allowed. Row 21's read is already allowed. Both were
filed with a boundary cost derived from the surface's NAME. The company wave hit
the same thing from the other side and shipped three rows off an About-card
inside a posting it was already loading -- *no page load added, no allowlist
pattern*. **Anyone re-costing this ledger should probe the ADDRESS of every 1R
row before trusting its `allowlist +N` cell.** On the two I probed, the cell was
wrong both times, and both times in the direction that makes the work look more
expensive than it is.

**But two of the ten writes are refused TWICE and eight only once**,
and that is a real distinction the ledger's single "WriteSpec" cell cannot
carry: a row refused by an anchored allowlist alone is one loose pattern away
from reachable, where a row also carrying `/create` or `/edit/` has a second,
independent gate behind it. The groups/events entry recorded exactly this
asymmetry for the member roster and called the count the point. It is the point
here too.

Enumerated at close. The ten writes are `P H1`-`P H10`; probing their plausible
addresses returns REFUSED-NO-PATTERN for every one except the two carrying
`/create` and `/edit/`. So the split is **2 refused twice, 8 refused once** --
and the eight are the ones a single loose anchored pattern would reach.

### AND ONE OF THE TEN IS NOT LIKE THE OTHER NINE. `P H9` IS EXCLUDED-RULED.

    P H9  Request service reviews (up to 20 invitations)

The census row flags it in its own note -- *"reaches real people"* -- and
nobody had joined that to the invitation ruling. **It is the same act as
`INVITE-NOTE-PARAM` at twenty times the scale**: an outward-facing, irreversible
request delivered to up to twenty named human beings, composed from something,
and unrecallable once sent. Every argument in section 5 applies and each one
applies harder.

The other nine writes change how he presents himself on a page. `P H9` puts a
message in twenty other people's notifications. **"Design and gate them, fire
none" is right for nine and is the wrong frame for this one** -- a gate is a
mechanism for an act somebody intends to perform, and nothing in the record says
he intends this one.

**RULING: `P H9` is EXCLUDED-RULED, not GAP, on the section 5 ground.**
`SERVICES-PAGE-SURFACE` costs 11 rows as filed and 10 as ruled: 1R + 9W.
REOPENER, identical in shape to the invite-note one: he asks for it explicitly,
with the recipients named. Not "he wants reviews" -- named recipients.

### A THIRD WAVE REACHED THE SAME VERDICT ON A DIFFERENT DENYLIST, INDEPENDENTLY

Observed at close, in this tree, in a sibling wave's commit message on the
profile-modal blockers: *"THE DENYLIST WAS NOT NARROWED, and declining it is the
finding"* -- its two candidate entries matched zero of 237 urls across five
profile captures, so removing them would have traded a live guard for no reach.

**Two waves, two unrelated blockers, both costed for a denylist change, both
measured it and both declined.** That is not agreement between instruments
sharing a defect -- the two measurements have nothing in common except the
ledger column that predicted them. **The `denylist x1` cell has now been wrong
in every case anyone has actually probed**, which is a claim about the ledger
rather than about either blocker, and it is worth one pass over that column
before another wave is dispatched to shorten something.

---

## 4. `HASHTAG-EXISTENCE` -- MEASURE, and it was already largely measured

The gap document had already done most of this work and I did not re-take it.
It re-files the blocker's three rows to ONE (`C 52`): `N 194`'s own census note
names a different blocker (*"no people search"*), and `C 11` is EXCLUDED-RULED
because a shipped AST-asserted invariant already forbids the server composing
anything into his text -- the hashtag is that defect's worked example, not the
subject of the assertion.

My boundary reading adds the gate half:

    [R] /feed/hashtag/hiring/     REFUSED-NO-PATTERN
    [R] /feed/follows/            REFUSED-FORBIDDEN  matched '/follow'

**WHICH CLASS OF CLAIM THE EVIDENCE SUPPORTS, since the events wave's
distinction is the thing I was asked to be precise about:**

* *"the platform has no such surface"* -- permanent and universal. Supported by
  LinkedIn's own help index (source article returns HTTP 404; two independent
  index queries return no hashtag-following article) and by a live settled
  `/feed/` of 405872 characters drawing `hashtag` ZERO times in html as well as
  in visible text. **The second is the stronger of the two and it is nearly a
  platform claim rather than an account claim**, because a feed rendering posts
  that carried hashtags would draw `/feed/hashtag/` links regardless of whose
  feed it is. It is not quite universal: it is one account's feed on one day.
* *"the page reads zero for this account"* -- reversible. Nothing here is only
  this.

**RULING: `C 52` carries forward as a ONE-ROW MEASURE blocker, not retired.**
I decline to retire it on evidence I did not take, and the strongest instrument
(the 405872-character feed) is one reading from one session. Retiring a row on
a universal claim requires a universal instrument, and a re-run of that feed
read is the cheapest way to get a second one. **I did not take it** -- it is a
live page load and I judged the reproduction of the two live-read obligations
already queued in the freeze file to be a higher call on a shared browser.

A fixture-wide offline census of hashtag needles was commissioned as a second,
independent instrument. **It landed and it CHANGES the ruling above** -- see
section 7. The evidence supports neither of the events wave's two classes but a
third and narrower one: **LinkedIn still ships the hashtag data model and draws
no hashtag surface.** So `C 52` carries forward MEASURE for a sharper reason
than "I did not take the reading": a live type behind a withdrawn surface is
precisely the thing that returns, and retiring the row on "the platform has no
such surface" would retire it on a claim the evidence does not reach.

---

## 5. `INVITE-NOTE-PARAM` -- EXCLUDED-RULED

**RULING: NO. One row, `1W`, filed EXCLUDED-RULED rather than GAP.**

An invitation note is a free-text message to a real stranger, attached to an
irreversible act. `send_invitation` is already irreversible and already gated.
Adding a note multiplies the blast radius of a single mistaken confirm: today
the worst outcome of a wrong confirm is that a stranger receives a blank
connection request, which is socially cheap and silently ignorable; with a note
the same wrong confirm delivers composed prose over his name, to a named
person, permanently. **And the note would be composed from something** -- this
server has an AST-asserted invariant that the typed text is a slice of the
grant's canonical target precisely so it never composes what it types, and a
note parameter is the natural place for that invariant to be argued away.

The address side is not the blocker and the record should say so:

    [W] /mynetwork/invite-connect/connections/    ALLOWED   clean

That is the connections LIST, admitted 2026-09-03 as a read. The note is a
write PARAMETER, not an address, so no boundary change is implicated in either
direction. A future reader who reaches for the allowlist here has misread the
row.

**REOPENER, and it is the whole point of filing rather than deleting:** he asks
for it explicitly, with a target named. Not "he asks for invitations", not "he
asks for outreach" -- this row reopens on a named person and an explicit
request, and on nothing else.

---

## 6. WHAT I DID NOT DO, AND WHY -- the longer half

**I did not touch `linkedin_server/readonly.py`. Not one byte.** The
follow-list build in section 2 is specified and not applied. The reasons, in
order of weight:

1. **The boundary freeze chain is hand-narrated and contested.** It has been
   re-frozen five times on 2026-09-04 and at least twice on 2026-09-05, by
   different waves, and the file itself records that *"re-pinning a frozen
   digest to whatever the tree currently hashes to is the one edit this
   instrument cannot survive"* -- it turns a freeze into a mirror. Landing two
   allowlist patterns and two exemption patterns means moving two digests,
   appending a narrative leg without overwriting anyone's, and verifying that
   the tree minus my own line hashes to the prior pin. That is a careful
   half-hour on a quiet tree.
2. **I had 39 minutes by the box and a live child out.** A re-freeze abandoned
   two thirds through leaves a red belonging to nobody who ran it -- which this
   tree already has one of, and the freeze file has a whole section on how
   expensive those are to triage.
3. **Five staging incidents happened in this tree today**, and the sharpest
   statement of the rule is that staging a precise hunk does not narrow the
   window at all: the window is between the staging and the commit, and only
   ownership closes it. `readonly.py` is the single most contended file here.

**The trade I made, stated so it can be disagreed with:** a correct RE-FILING
of the overreach is worth more than a rushed application of it, because the
re-filing changes what the next wave does and the application does not depend
on me. **The finding travels with the artifact that produced it** -- the probe
is committed, so the receiver can RE-TAKE the reading rather than trust it.

**Also not done, and each is cheap:**

* The `SERVICES-PAGE-SURFACE` writes are not designed. Their addresses are now
  all probed (2 refused twice, 8 once) and `P H9` is ruled out, but no
  WriteSpec was written for the remaining nine and none was fired.
* **The services render gate is unmeasured.** I know the boundary admits
  `/in/me/`; I do not know whether the `Providing services` section is in the
  document on a passive load. That is one live read and it is the single
  cheapest thing left in this cluster.
* No live page was loaded, so **no invitation badge reading was taken** -- there
  was nothing to take one around. I loaded nothing, so nothing moved. That is a
  statement about my actions, not a measurement of the badge, and the
  difference matters: I am not reporting the badge as unchanged, I am reporting
  that I never approached it.
* The endorsements-received reader (row `N 114` / `P E7`) is not built,
  although its address is already admitted and it is now the cheapest row in
  this cluster.
* `C 52`'s second instrument is the fixture census in section 7, not a second
  live feed read.

---

## 7. THE FIXTURE CENSUS -- second instrument for section 4

Commissioned as an offline, independent check on whether any captured LinkedIn
html in this repo draws a hashtag surface, with a must-fire control so that a
zero could be distinguished from a broken scanner. Full working at
`_audit/_scratch/_network-tail-hashtag-census.md` (gitignored -- the numbers
that matter are reproduced here, because that path does not survive a clone).

    37 files (22 tracked, 15 untracked), 6955444 bytes

    /feed/hashtag        0
    Followed hashtags    0
    feed/follows         0
    #hiring              1
    hashtag            146
    CONTROL "<div"    4860, non-zero in EVERY one of the 37 files

**Every zero carries its denominator**, which is the whole reason this was
commissioned: a zero with no denominator is not a measurement. The three
structural zeros are taken over all 37 files and all 6955444 bytes, and each was
confirmed twice -- once by an occurrence counter, once by an independent tool.

**AND THE NON-ZERO IS THE INTERESTING RESULT, NOT THE ZEROS.** `hashtag` occurs
146 times, in exactly 4 of the 37 files, and **zero times in any of the 22
tracked fixtures**. All 146 were inspected in context and fall into two buckets,
neither of which is a rendered control:

1. **icon-manifest asset filenames** -- a page-agnostic sprite manifest that
   ships whatever the page shows, carrying a `hashtag` icon family alongside
   many other generic entity-type families;
2. **REST.li schema type definitions** -- a `Hashtag` record type, a urn type
   reference, a `hashtagUrns` array field. The client's data model telling
   itself the type exists.

The two blobs are byte-identical across three of the four files, consistent with
one shared inlined bundle rather than three independent occurrences of hashtag
UI.

### THIS SHARPENS THE CLAIM PAST BOTH OF THE EVENTS WAVE'S TWO CLASSES

The events wave gave two classes -- *"the platform has no such surface"*
(permanent, universal) and *"the page reads zero for this account"* (reversible).
**The honest reading here is neither, and it is more useful than both:**

> **LinkedIn still ships the hashtag DATA MODEL and draws no hashtag SURFACE.**

A bare zero would have been consistent with LinkedIn having deleted the concept.
It has not: the type is right there in the bundle. What is absent is every
rendered affordance -- no `/feed/hashtag` link, no `Followed hashtags` heading,
no follow control -- across 6955444 bytes in which the control needle fires
4860 times.

**That matters for the ROW rather than for LinkedIn.** A retired concept stays
retired; a live type behind a withdrawn surface is exactly the thing that comes
back, and a row retired on "the platform has no such surface" would be retired
on a claim this evidence does not support. It supports the narrower one.

**LIMITS, stated rather than left for a reader to find.** These are captures
this repo happens to hold, taken for other purposes -- feed, groups, events,
profile. **None was taken while looking for a hashtag surface**, so this is
evidence of absence exactly to the degree those pages would have drawn one, and
that degree is unquantified. The 22 tracked fixtures are sanitised, and a
sanitiser that stripped hashtag markup would produce this same zero; the 15
untracked raw captures are what carry the weight, and they are the ones that do
not survive a clone.

---

## 8. INSTRUMENT ADMITTED, SHOWN FAILING

`scripts/_probe_network_tail_boundary.py` -- offline boundary reproduction over
18 candidate addresses plus 3 controls. It distinguishes THREE outcomes, and
the distinction is its entire value: `ALLOWED`, `REFUSED-FORBIDDEN` (naming the
matching substring), `REFUSED-NO-PATTERN`. A row blocked by NO-PATTERN needs an
additive allowlist entry; a row blocked by FORBIDDEN needs a denylist change,
which is a different and far more dangerous edit. A probe that printed
"refused" for both would have sent this wave to narrow `/endorse` for a row
that is already allowed.

**Its substring detector is computed independently of `assert_read_url`**, so
the two can disagree and the disagreement is visible. An instrument whose
detector is the thing it measures cannot fail.

**SHOWN FAILING, not asserted to work.** With `_FORBIDDEN_URL_SUBSTRINGS`
monkeypatched to the empty tuple:

    HELD    /feed/                    expected ALLOWED            read ALLOWED
    BROKEN  /company/<slug>/follow/   expected REFUSED-FORBIDDEN  read REFUSED-NO-PATTERN
    HELD    /nothing/here/            expected REFUSED-NO-PATTERN read REFUSED-NO-PATTERN
    controls hold? False

**One control broke and two held.** That is the load-bearing half: the mutation
was specific, so the control is sensitive to the branch it is named for rather
than merely to the probe being alive. This is the 14:05 law applied forward --
the input was chosen so that the neutered denylist is the ONLY thing that could
change the answer, instead of being chosen from a model of the risk.

It is DISPOSABLE for the boundary register in the sense that it hard-codes this
wave's candidate set; the reusable part is `verdict()`, three lines, which any
future blocker triage should copy rather than re-derive. Registering it as a
candidate for `INSTRUMENTS.md` under that caveat rather than claiming it is
general.

---

## 9. LEDGER EFFECT

Recomputed at close from the rows above, not carried forward from the brief.

| blocker | as briefed | at close |
|---|---|---|
| 63 `ENDORSE-SUBSTRING-OVERREACH` | 3 rows, DECIDE, denylist x1 | **denylist x1 NOT OWED.** 1R already ALLOWED -> re-files to BUILD on an admitted address. 2W correctly refused. |
| 52 `PEOPLE-FOLLOW-LISTS` | 4 rows, BUILD, allowlist +2 denylist x1 | **this is where the overreach lives.** allowlist +2 and exemptions +2 CONFIRMED; **denylist x1 REFUSED** -- exempt, never narrow. Spec written, not applied. |
| 21 `SERVICES-PAGE-SURFACE` | 11 rows, DECIDE, allowlist +1 | reads-are-fine ruling holds. **`allowlist +1` NOT OWED** -- the 1R renders on `/in/me/`, already admitted. **`P H9` EXCLUDED-RULED** (reaches up to 20 real people). 11 rows as filed -> 10 as ruled. Write split: 2 refused twice, 8 once. Render gate UNMEASURED. |
| 11 `HASHTAG-EXISTENCE` | 3 rows, MEASURE | already re-filed to 1 row by the gap doc. Carries forward MEASURE. Not retired -- see section 4 on which class of claim the evidence reaches. |
| 60 `INVITE-NOTE-PARAM` | 1 row, DECIDE | **EXCLUDED-RULED.** Reopener: he asks explicitly, with a target named. |

**Net boundary movement from this wave: ZERO.** Allowlist 29 before and after,
denylist 33 before and after. No digest moved and no re-freeze was attempted.

---

## 10. CLOSE -- every number here RECOMPUTED, not re-read

Taken at freeze by running the code, per the standing rule that proofreading
cannot reach a number that is wrong and only recomputation can.

    allowlist patterns        29     (unchanged by this wave)
    forbidden substrings      33     (unchanged)
    pattern exemptions         2     (unchanged)
    exact-url exemptions       2     (unchanged)
    files this wave committed  2     _audit/2026-09-05-network-tail.md
                                     scripts/_probe_network_tail_boundary.py
    commits                    3     ffc57c7, 6315915, 1bf0981
    linkedin_server/readonly.py      NOT TOUCHED, byte-unchanged

**Zero AI attribution across all three commit bodies, with the check SHOWN
FIRING.** A planted `Co-Authored-By` trailer returns 1 from the same needle that
returns 0 on all three commits. A check that cannot fail certifies nothing, and
this one is now known to be able to.

**AND THAT CHECK FALSE-ALARMED ON ITS FIRST RUN, which is worth recording
because it is the day's own law pointed at me.** My first needle included
`noreply` and matched all three commits -- on the operator's own GitHub
`users.noreply.github.com` author address. **A red guard means MATCHED, not
REAL.** I measured what it saw before concluding anything, and what it saw was a
needle I had chosen too broadly. Had I escalated instead, I would have reported
AI attribution on three clean commits, which is the exact error already recorded
against the lead twice today over four synthetic member ids.

### Suite reds in this checkout, none of them mine

Named by file, because "the text-taint guard" is not an address:

    test_page_text_is_never_printed::test_no_file_prints_page_text_beyond_its_pinned_inventory
        scripts/_probe_comment_identifier.py, scripts/_probe_contact_info_panel.py
    test_a_sanitiser_earns_its_entry::test_every_claimant_of_a_sanitiser_name_is_enrolled
        scripts/_probe_profile_modal_presence.py  (its owner's commit says it is fixed there)
    test_a_correction_is_findable_from_the_claim  (3 tests)
        2026-09-05-census-recounted.md, 2026-09-05-jobs-tail.md, 2026-09-05-profile-modals.md

**The correction guard went from 1 failure to 3 in eight minutes while I worked,
and it is not the same 1.** Different documents, different lines -- other waves
committing audit docs. *Compare the SETS, never the totals*: a count that moves
under a change that should not move it is a number about the tree, not about the
guard. My document is named in NONE of the three, checked by extracting the
document names the failures print rather than by reading the summary line.

### One thing raised OUT of this wave and routed

The shipped exact-value identity sweep went RED at my commit gate on a file that
is not mine and is already COMMITTED: `_audit/2026-09-05-jobs-tail.md:403`,
class `operator_own_denied_terms`, blob at `7edbd0a`. The file is clean in the
working tree, so tree and blob are the same object and the hit is in history.
Push freeze is on, so nothing is published.

Handed off on disk at `_TEAM_LEAD_IDENTITY_HIT_JOBS_TAIL.md` (untracked, so it
surfaces in every wave's own `git status`) rather than by message, because the
owning wave is not in my roster and a send to a guessed idle name forks that
agent. **I did not read the matched line, did not unmask it, and am not ruling
on it.**

**The ordering is the finding.** Two readings, both mine, both by the shipped
sweep, about two minutes apart: PASS 0 hits over 314 files, then FAIL 1 hit over
332. Eighteen files entered the index in between and this one was committed
inside that window. That is the ~16:57 entry in the freeze file replaying about
two hours after it was written, and it is a second receipt for the pre-commit
hook that entry recommends -- a hook would have refused the commit at the moment
it was made, instead of leaving it to a neighbour committing two minutes later.

### AND THEN THE DISK WENT GREEN, WHICH IS NOT THE SAME AS RESOLVED

    ~18:59  sweep FAIL: 1 hit  across 332 tracked files
    ~19:09  sweep PASS: 0 hits across 333 tracked files

Somebody fixed the working-tree copy in that window. **That is the correct
remedy in a shared tree -- a follow-up commit, not a rewrite -- and it settles
nothing about what a push would publish.** The file has six commits and grew
from 22483 to 29800 bytes across them, so the fix is later than `7edbd0a` and
the earlier blobs are untouched. This repo's own rule: *a clean working tree
says nothing about history; to make a claim about what a push would publish,
sweep the BLOBS.*

**I TRIED, MY INSTRUMENT WAS BROKEN, AND I AM CLAIMING NO READING.** I wrote an
ad-hoc blob sweeper that imported the shipped `load_wordlist()` and then
extracted the values from it myself. It printed:

    sweeping blobs with 0 spellings
      556d6e0 ... classes hit: NONE      (and five more, all NONE)

**Zero spellings. An empty needle set matches nothing, and its `NONE` is not a
result.** I am recording the broken output rather than deleting it, because six
`NONE` lines read as an all-clear to anyone who did not read the first line --
which is the precise shape this repo keeps catching.

**This is the THIRD recorded instance of one specific error, and the remedy was
already written down before I made it.** The lead built its own exact-value
check twice on this date and both were broken; only the attempt that used the
shipped code found the real hits, and the rule extracted from that was: *when a
repo ships an instrument, IMPORT IT -- do not reimplement it to point at a
different corpus.* I reimplemented it anyway, from the same motive (wanting the
sweep aimed at blobs rather than at disk) and with the same outcome. **A rule
that has now failed to prevent its own violation three times is a missing TOOL,
not a missing reminder**: the shipped sweep has no blob mode, so everyone who
needs one writes their own badly. That is the fix worth making.

Honest state at the time that was written: **DISK GREEN, HISTORY UNREAD.**

### THE HISTORY IS NOW READ, AND THE MISSING TOOL IS BUILT

The lead took the blob reading independently and it came back **3 blobs of one
path**, `_audit/2026-09-05-jobs-tail.md`, class `operator_own_denied_terms`, all
unpushed. Purge scoped, push blocked. **My caution was answered, not
vindicated** -- the reading existed and I simply did not have it, which is the
correct outcome of refusing to report a mute instrument rather than the reward
for it.

Then I built the thing whose absence caused the failure:
**`scripts/sweep_blobs_for_identity.py`.**

    needles: 218 spellings across 16 classes
    range  : @{upstream}..HEAD -> 51 commit(s)
    swept  : 388 distinct blob(s)
    FAIL: 3 hit(s) in 1 distinct path(s).     exit 1

**It agrees with the lead's independent pass: same count, same path, same
class.** The two address the same objects by different names -- that pass
reported COMMIT shas, this one dedupes by BLOB sha and adds the line number
(403, which is also where the on-disk sweep found it, so three routes converge
on one line).

**AND THEY ARE NOT FULLY INDEPENDENT, WHICH MATTERS MORE THAN THE AGREEMENT.**
Both import `load_wordlist()`, so a defect in the key would move both together
-- and this repo has already recorded two corroborating readings being wrong
together, an events selector reading 54 rows where there are 18 with two
selectors agreeing because both were the same multiple of the truth. What IS
independent here is the enumeration and the dedupe. Stating the shared
component is the difference between corroboration and the appearance of it.

**THE DESIGN IS ONE IDEA AND IT IS MY OWN SCAR ENCODED AS A GUARD.** The
instrument REFUSES to report a green it cannot back: if the needle set is empty
it exits 2 saying it cannot speak, **before sweeping anything**, so no
reassuring output can precede the refusal, and it prints the needle count on
every run so a reading arrives with its own denominator.

SHOWN FAILING, both directions, because a mute instrument and a clean corpus are
indistinguishable without both:

    wordlist monkeypatched empty  ->  "REFUSING TO SWEEP: the needle set is
                                       EMPTY."  exit 2
    real range                    ->  218 needles, 3 hits, exit 1

**The general lesson is the one worth keeping, and it is not about sweeping.**
The rule *"when the repo ships an instrument, IMPORT IT"* was written down
before any of the three violations and prevented none of them. Every violation
had the same motive: wanting the instrument aimed somewhere its enumeration does
not reach. **A rule that keeps being broken from an identical motive is a
missing TOOL, not a missing reminder** -- the same discipline-to-mechanism
conversion as the pre-commit hook the lead installed today, which now refuses at
the index what three people were catching by hand.

### The single sentence, if only one survives

**Two of my five blockers were costed for a boundary change that measurement
says is not owed, and both were costed from the surface's NAME rather than its
ADDRESS.** The denylist narrowing I was sent to make is not needed where I was
sent; the overreach it describes is real and sits one blocker away; and the
remedy there is an anchored exemption, which leaves the guard's reach intact,
rather than a narrowing, which does not.
