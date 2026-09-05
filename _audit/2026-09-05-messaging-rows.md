# Messaging rows wave, 2026-09-05 evening

**Owner: the `messaging-rows` wave. Scope: the same 7 blockers / 24 rows the
`messaging` wave left, plus the authorised live load it declined to take.**

**Page loads taken: FOUR, of which exactly ONE was `/messaging/`.
Messages sent: ZERO. Controls pressed: ZERO. Rows I retire myself: ZERO --
I hand up measurements, not retirements.
Commits: 9. Tests added: 9, in one new file. Boundary changes: 0.**

**HEADLINE, and it is not the load.** The load answered row 66 outright and
refuted the relayed zero behind rows 17 and 67. But the most reusable thing
found today was found without a browser: `known_side_effects` -- the field a
caller reads to decide which tool is safe -- makes CLOSED ENUMERATION CLAIMS
that nothing checks, and the messaging one is wrong in both directions at
once. Section 6. `a86c849` repaired the neighbouring bullet 51 minutes before
I looked at this one.

---

## 1. WHAT THE LOAD COST. First-class, as instructed.

**VERIFIED-BY-INSTRUMENT.** `scripts/_probe_messaging_surface_census.py`,
commits `697b609` + `a373547`, run 22:20:49 -> 22:21:19 by the box.

    reading            messaging badge          invitation badge
    BEFORE (on /feed/) new_since_last_visit=0   pending=0
                       state='read'             state='read'
    AFTER  (on /feed/) new_since_last_visit=0   pending=0
                       state='read'             state='read'
    moved              False                    False

**Both badges read at both ends, so the reading is reportable.** That was a
refusal condition, not a hope: the probe returns before the navigation if
either badge fails to read at the BEFORE, and prints UNREPORTABLE rather than
a delta if either fails at the AFTER.

**A CONVERSATION DID OPEN.** `redirected into a conversation: True` -- the
landed url carried `/messaging/thread/`. That is the documented redirect
confirmed a third time, and it is the cost that is actually observable here.

**AND THE BADGE DELTA IS NOT EVIDENCE OF ZERO COST, which is why it is stated
this way rather than as a clean pair of zeroes.** The probe refuses unless the
messaging badge reads 0 BEFORE, so a badge that was already 0 cannot show the
load consuming anything. **The zero delta is the precondition doing its job,
not a measurement that the load was free.** Reporting it as "cost: none" would
be the sibling of the trap this repository already wrote down -- *a badge at
zero cannot distinguish "the page consumed nothing" from "there was nothing to
consume."*

    navigations       3   ( /feed/ -> /messaging/ -> /feed/ )
    of which /messaging/  1
    page closed       True, in a finally. The PAGE, never the context.

**WHY THE AFTER READ COSTS A SECOND `/feed/`.** The messaging badge RESETS
while you are sitting in messaging -- that is the mechanism being measured --
so a post-read taken on the messaging page is uninterpretable by construction.
Both ends are read off `/feed/`, the same page with the same readers, which is
what makes them comparable at all.

---

## 2. THE ROWS THE LOAD ANSWERED

### 2.1 Row 66 `THREAD-REPLY-BOX` -- ANSWERED, both rows

    elements on the page   1351
    settle verdict         'rendered_no_baseline'      <- the page arrived
    recipient_boxes        0     <- the REFUTATION reading, did not fire
    editors                1     contenteditable, any
    editable_true          1
    textboxes              1     div[role=textbox]
    textareas              1
    text_inputs            1
    send_controls          1
    send_disabled          True

**A reply box exists, a Send control exists, and it is DISABLED on an empty
box** -- the exact transition signal `publish_post` and `send_message` both
gate on, which means a fill that lands is observable without reading what was
typed. The addressless-reply route the census called the most job-hunt-relevant
messaging action in all 761 rows is VIABLE.

**The refutation reading did not fire.** `recipient_boxes` is 0, and my own
independent selector for the composer's recipient box (section 2.5) also reads
0. Two readers, two mechanisms, same answer: **a thread has nobody to choose,
so a reply needs no address.**

**WHAT THIS DOES NOT SETTLE.** `editors`, `textboxes`, `textareas` and
`text_inputs` all read 1. A count cannot say whether that is ONE element seen
by four mechanisms or four distinct elements. `ac7003b`'s own commit subject --
*"the textarea is not the reply box"* -- says at least two are distinct. Not
resolved here, and resolving it needs element identity rather than counts.

### 2.2 Rows 17 + 67 `CONVERSATION-OVERFLOW-MENU` / `PER-MESSAGE-OVERFLOW-MENU` -- THE RELAYED ZERO IS REFUTED

The predecessor relayed, explicitly as unverified: *"0 triggers and 0 menu
items in 1.28 MB of DOM"*, with section A13 proposing all 10 rows move to
DECIDE on the strength of it.

    aria-haspopup, any value        0
    aria-haspopup=true              0
    aria-haspopup=menu              0
    role=menu                       4
    role=menuitem                  12
    button[aria-expanded]          31
    button[aria-expanded=false]    31

**`aria-haspopup` reads 0 on a page that draws 4 menus and 12 menu items.**
The trigger on this surface is marked with `aria-expanded` -- 31 of them, every
one collapsed -- and not with `aria-haspopup` at all.

**AND THE ITEMS ARE ALREADY IN THE DOM WITH NOTHING PRESSED.** Twelve
`role=menuitem` elements, on a page where no control was activated. That
changes the shape of these 12 rows: the stated blocker was that enumerating
the items needs a press, and **the items do not need a press to be counted.**

**WHAT I AM AND AM NOT CLAIMING.** I am refuting a CONCLUSION -- "0 menu
items" -- with a direct count on a live page. **I am NOT diagnosing the prior
instrument**: I never saw it and do not know what it aimed at. The `aria-haspopup`
zero sitting beside a `role=menuitem` twelve is *a hypothesis about how a
correct-looking reader reaches zero*, offered as one. Route the artifact:
`_audit/_scratch/_progress-measure-surfaces.md` and blockers A13, not this
paragraph.

**I did not read the twelve labels.** Deliberately -- see section 4.

### 2.3 Row 76 `MESSAGE-REACTION` -- the affordance is drawn

    label contains React        12
    label contains Emoji         5
    label contains reaction      0     <- case-sensitive; "React" is the spelling
    label contains Delete        0
    label contains Archive       0
    label contains Report        0
    label contains More          1
    label contains Options       8
    label contains Write a message  1
    label contains Compose       0
    label contains New message   0

Twelve controls carry `React` in their accessible name. The reaction
affordance exists on this surface.

**THE DOUBLE-COUNTING TRAP, AND I AM NAMING IT RATHER THAN BANKING BOTH
NUMBERS.** `role=menuitem` is 12. `React`-labelled controls are 12. **These may
be the same twelve elements** -- a reaction picker IS a menu of items. If they
are, then counting 12 as evidence for rows 17/67 AND 12 as evidence for row 76
is one observation spent twice.

Resolving it needs the menu items' labels, which I did not read. **An equal
count is a correlation, not an identity**, and this repository has already
recorded two corroborating readings being wrong together because they shared a
defect. I decline to spend this one twice.

### 2.4 Row 50 `MESSAGE-REQUESTS-SURFACE` -- the `allowlist +1` is CONFIRMED a placeholder

    CONTROL /feed/          2      <- the href reader FIRED
    CONTROL /messaging/     1      <- the href reader FIRED
    /messaging/thread/      0
    /messaging/requests     0
    message-requests        0
    messageRequest          0
    filter=requests         0
    /messaging/compose      0
    filter=other            0
    filter=focused          0
    filter=unread           0
    filter=inmail           0
    /messaging/?            1

**Both firing controls are non-zero, so the zeros above are about LinkedIn and
not about a dead reader.** That is the whole reason they are in the list.

**No message-requests address is drawn anywhere in this page's own nav.** The
standing rule is that an `allowlist +1` naming no address is a placeholder for
an unknown until somebody names it. **This is the first time that has been
MEASURED on this surface rather than inferred from the ledger** -- the obvious
place for the address to be named is the surface it belongs to, and it is not
there. Row 50 is not cheaper than the ledger says; it is a genuine unknown.

**`/messaging/thread/` reads 0 while we are ON a thread.** So the conversation
list is not made of anchors -- consistent with the `role=menuitem`/`button`
picture and with the filter finding below.

**ONE query-bearing messaging anchor exists and I did not resolve it.**
`/messaging/?` = 1. What that query says is the single cheapest thing a second
load would settle, and it is a plausible home for the requests or Other view.
It is unresolved because of the no-strings rule in section 4, and that is the
price of that rule stated plainly rather than hidden.

> ### RESOLVED 22:34, WITHOUT A SECOND SPEND -- see section 2.9
>
> **It is the same anchor as the CONTROL, and it is the nav's own link.**
> `a[href*="/messaging/"]` read 1 and `a[href*="/messaging/?"]` read 1 on that
> page. **The second selector is a subset of the first**, so at 1 and 1 they
> match THE SAME ELEMENT -- arithmetic over two counts I had already taken,
> not a new reading and not a guess. It is the global nav's messaging link
> wearing a query LinkedIn appends when you are already there, and it is not a
> second destination.
>
> **The answer was inside the numbers already printed.** I wrote it up as an
> open item because I read the two rows as two findings instead of asking what
> relation the two SELECTORS have. Section 2.9 then confirmed the same shape
> from `/feed/` at zero cost. *Recompute over your own readings before
> declaring something unreached.*

### 2.5 Row 57 `MESSAGE-ADDRESSING` -- STILL UNOBSERVED, and now for a STATED reason

    composer recipient box      0
    chip selector 1 of 4        0
    chip selector 2 of 4        0
    chip selector 3 of 4        0
    chip selector 4 of 4        0

**THIS READING RETIRES NOTHING AND ITS CONTROL DID NOT FIRE.** The four chip
selectors read zero -- but so does the rail's own anchor, the composer's
recipient box. So the reading cannot separate *the selectors are wrong* from
*there is no rail on this page at all*, and the second is obviously true: a
thread page has no composer. **Row 57 is exactly where the predecessor left
it.**

**THE STRUCTURAL POINT, WHICH IS NEW AND WHICH I THINK OUTRANKS THE READING.**
Row 57's stated blocker is *"the chip rail has never been observed."* A chip
does not exist until a recipient is COMMITTED to a composer. **Committing a
recipient is not a read** -- it is the second-to-last step of an irreversible
send, and it is the step `_recipient_gate` exists to adjudicate.

> **So "observe the chip rail" is not a measurement any read can take. Row
> 57's blocker is unreachable by the class of action that was going to
> discharge it.**

That is not a reason to relax anything. It is the argument for the identifier
route in `2026-09-05-messaging.md` section 6 -- already admitted at the
boundary -- rather than for further tuning of a string comparison against a DOM
nobody can legitimately produce.

**THE DIGIT-ADJACENCY RULING IS NOT SETTLED BY THIS LOAD AND I AM NOT
SETTLING IT.** No chip was observed, so there is no evidence about whether a
real chip runs a connection degree onto a name the way a suggestion row does.
The red in `tests/test_click_is_not_its_own_evidence.py` stands where the
predecessor left it, with its reasons intact. **I looked for the evidence that
would move it and did not find it; that is a result, not a deferral.**

### 2.6 Row 45 `GROUP-CHAT-SURFACE` -- still BLOCKED, and the reading is a sample of one

    label contains participants   0
    label contains group          0
    role=listitem                 0
    role=tablist                  0
    role=tab                      0
    role=dialog                   0
    CONTROL button               58     <- the role reader FIRED
    role=button                   5
    li                           59
    form                          1

No group-chat vocabulary is drawn on this conversation. **But LinkedIn CHOSE
this conversation.** This is a sample of one thread out of an inbox nobody has
enumerated, so it says nothing about whether he is in group conversations. Row
45 stays BLOCKED.

### 2.7 A question `server.py` said either answer would settle -- and I am NOT banking it

`linkedin_open_messaging` carries this, verbatim: *"if a pill is an anchor its
href names the filter parameter, and if it is a button with no href then
filtering is client-side state and InMails are unreachable by navigation at
all. Either answer is a finding."*

    filter=focused / other / unread / inmail hrefs    0, 0, 0, 0
    role=tablist                                      0
    role=tab                                          0

That points at client-side filtering. **I am not claiming it.** LinkedIn
redirected into a THREAD, and the filter pills may simply not be drawn on that
view -- in which case this is a reading about which view I landed on, not about
how filtering works. **A zero taken from a surface that may not draw the
control is the render-gate trap**, which this repository has already paid for
once on a tabbed profile category. Recorded as evidence toward, not as an
answer.

### 2.9 THE SAME QUESTION FROM `/feed/`, AT ZERO MESSAGING COST -- row 50 answered twice

**VERIFIED-BY-INSTRUMENT.** `scripts/_probe_messaging_family_off_the_feed.py`,
commit `e4a7947`, run 22:34:13. **Zero `/messaging/` loads.**

`/feed/` is loaded by `linkedin_new_messages`, by every badge read in this
package, and by the messaging probe at both of its own ends. It does not
redirect into a conversation and does not clear the messaging badge -- that is
precisely why it is the surface both badges are read off. **A global nav is
drawn on every page**, so if LinkedIn advertises a message-requests
destination anywhere, the feed carries it.

**AND IT ADDS THE THING SECTION 2.4 LACKED: A DENOMINATOR.** Per-literal counts
alone cannot separate *LinkedIn draws no requests link* from *my literals do
not spell what LinkedIn draws.* So this counts the whole family, then the
subset matching any of twenty declared spellings, and prints the difference.

    total anchors under /messaging       1
    matching at least one spelling       1
    UNACCOUNTED                          0
    the one that matched                 /messaging/   (the bare root)

    messaging badge  new_since_last_visit=0  state='read'
    invitation badge pending=0               state='read'

**UNACCOUNTED = 0 is what makes the zeros mean something.** The messaging
family, as drawn in the global nav, is fully spelled by the declared list --
so the sixteen requests/filter zeros are readings about LinkedIn and not about
my vocabulary. **A non-zero here would have proven an address this repository
cannot name, and said how many.**

> **ROW 50, STATED AS A RESULT:** the message-requests address is not
> advertised in the global nav on ANY page this server loads -- measured from
> two independent surfaces, the messaging page and the feed, with a firing
> control on each. **The `allowlist +1` is a placeholder for an unknown, and
> that is now measured rather than inferred from a ledger.** Nobody should
> spend it by writing a pattern broad enough to cover the unknown.

**What this does NOT establish:** that no such surface exists. LinkedIn may
draw the entry inside the messaging page as a button rather than an anchor --
which is consistent with `/messaging/thread/` reading 0 on a thread page, and
with `role=menuitem` reading 12. **A destination that is not an anchor cannot
be found by an href census**, and that is the honest limit of both readings.

---

## 3. WHAT THE LOAD DID **NOT** REACH

Stated plainly, because a wave's omissions are the part a successor cannot
recover.

* ~~The query on the one `/messaging/?` anchor.~~ **RESOLVED at 22:34** by
  arithmetic over readings I already had, and confirmed from `/feed/` at zero
  cost. Sections 2.4 and 2.9.
* **The labels of the 12 `role=menuitem` elements.** Deliberate, section 4.
* **Whether the 12 menu items and the 12 `React` controls are the same
  elements.** An equal count is not an identity.
* **Any chip, and therefore row 57.** Structurally unreachable by a read.
* **Any group conversation, and therefore row 45.**
* **What a second conversation looks like.** One thread, chosen by LinkedIn.
* **Whether the reply box and the textarea are distinct elements.**
* **No WriteSpec written**, for any of the six blockers that need one. Same
  as the predecessor.
* **No write fired**, gated or otherwise, at anyone.
* **No boundary change.** No allowlist entry, no denylist entry, no digest
  recomputed. Row 50's `+1` is untouched and is now measured to be a
  placeholder rather than a unit of work.
* **The full suite was not run.** I ran my own file (7), both taint guards
  (279 with mine), and the exact-value sweep after staging.
* **I retire no row.** Rows 17, 66, 67 and 76 have moved substantially and the
  retirement decision belongs to whoever owns the ledger, with these numbers.

---

## 3a. NOBODY CAN SAY WHICH ROWS THESE ARE, AND THAT LIMITS EVERY NUMBER ABOVE

**DERIVED, from a delegated census I did NOT re-take, and then CORROBORATED
from a tracked document I did read.** Flagged this way deliberately: a number
one agent hands another is a reading with a timestamp the receiver cannot see.

A slice sent to enumerate the row IDs behind my seven blockers found that
**only one of the seven has an explicit row-id list anywhere** in the tracked
or scratch corpus (`GROUP-CHAT-SURFACE`, and even there two independent
reconstructions disagree about which row fills the fourth slot). For the other
six -- including all 10 rows of `CONVERSATION-OVERFLOW-MENU` and all 4 of
`MESSAGE-REQUESTS-SURFACE` -- there is no list.

**THE CORROBORATION IS BETTER THAN THE DELEGATION**, and it is independent of
it: `_audit/2026-09-05-decide-retire-rulings.md` section 1 says so in its own
words, about its own work -- *"The ledger assigned all 409 rows to blockers and
then published only the COUNTS... the classifier that produced the mapping is
not on disk."* That wave had to reconstruct eleven of twelve blockers' row sets
by reading each blocker NAME as a capability family.

**WHAT THIS MEANS FOR EVERYTHING ABOVE.** The totals reconcile -- 10+4+2+2+1+1+4
= 24, and the R/W split matches the predecessor's independently-stated
2R/21W/1RW. **But a total that sums correctly is not a set that has been
checked**, and this repository has already recorded the exact arithmetic that
hides a pair of errors: profile +1 and messaging -1, cancelling in the total.

So when section 2 says row 66's two rows are answered, that is a claim about a
BLOCKER whose two rows nobody can name. **My measurements are about surfaces
and they are sound; the mapping from surface to ledger row is the part that
rests on a reconstruction.** Whoever retires rows on the strength of this
document should retire them by BLOCKER, or reconstruct the row sets first and
say which method they used -- not quote my section numbers against row ids
nobody has.

---

## 4. WHY THIS PROBE READS NO STRINGS AT ALL, AND WHAT THAT COST

Every reading in section 2 is `locator(<a selector written in the probe>).count()`.
**No label, no href, no inner text, no page string of any kind entered the
process** -- not redacted, not shaped.

That is stricter than every sibling probe on this surface, and the reason is
the surface. A conversation page is a third party's correspondence, in full,
sent to him privately. `_probe_thread_reply_surface.py` measured the shipped
redactor letting a name survive `Reply to <a name>` and `Open <a name> profile`,
and this repository has measured `census_substitute` returning a person's name
UNCHANGED. **A relation cannot carry an identity; a redacted string can
whenever the redactor has a hole.** Reading nothing removes the question
instead of answering it.

**THE COST IS REAL AND IT IS VISIBLE IN THIS DOCUMENT.** Section 2.4's
unresolved query and section 2.3's unresolved 12-versus-12 are both directly
caused by this rule. **Every zero in section 2 is a reading about a selector I
wrote**, which is why three firing controls -- arrival, a must-match href, a
must-match role -- are read first and reported first. They all fired.

### And it presses nothing, which is a ruling rather than nerves

Rows 17 and 67 ask what an overflow menu CONTAINS, and the obvious move is to
press a trigger. Every click in this package is gated through
`readonly.SANCTIONED_MUTATIONS`, and **the only sanctioned click on this entire
surface is a named filter pill.** An overflow menu on a conversation is a
plausible home for `Delete`. A probe that presses an unsanctioned control on a
real person's conversation has routed around the exact mechanism that exists to
stop it -- and this repository's standing scar is that routing around a blocked
supported path under friction is how a capability silently loses its guarantees.

**As it turned out the press was unnecessary**, because the items are in the
DOM already. That is luck, not vindication, and the ruling would have been the
same either way.

---

## 5. TWO SELF-INFLICTED FAILURES, BOTH INSTRUCTIVE

### 5.1 A SCRIPTED REWRITE DELETED HALF THE PROBE AND EVERY CHECK PASSED

A `python - <<PY` rewrite step sliced from `_read_both_badges` to `main()` to
swap two helpers. **That span also contained `_SPENT` and the whole of `_run`
-- every section of the census.** The file still compiled. Both taint guards
still passed on it. The commit reported 320 insertions and I committed it.

**THE CHECK I RAN WAS NOT A CHECK.** I verified by comparing the reported 320
insertions against 320 lines in `git show HEAD:<path>`. **Those agree by
construction -- both count the same truncated object.** The file had been 435
lines minutes earlier, and 320-against-435 is the comparison that had the
answer in it.

    RULE: an insertion count is a check ONLY against a figure derived
          INDEPENDENTLY of the commit. A number compared to itself is
          arithmetic, not verification.

That is the sharper form of the standing rule the predecessor wrote at 19:18
after losing section 7 the same way. **I had read that rule, in this wave, and
performed the ritual instead of the check.** Reading a documented near-miss
does not prevent it -- second receipt in two days.

**What caught it: running the thing.** `NameError: name '_run' is not defined`.
**What would have caught it earlier, and now does: an AST enumeration of
top-level definitions**, which a syntax check and a taint guard structurally
cannot perform -- nothing referenced `_run` except `main()`, at runtime.

**NOTHING WAS SPENT.** It raised before any navigation and its own cost line
printed `loads taken this run: 0`, because `_SPENT` is appended to AT the
navigation and not before. A counter placed at the act rather than at the
intent is why a crash could not inflate it.

### 5.2 THE NEW INSTRUMENT REFUTED ITS OWN AUTHOR ON FIRST RUN

I wrote `test_two_tools_load_a_messaging_address_and_the_sentence_names_neither`
asserting two unnamed tools. **It failed, naming one.** The second,
`linkedin_surface_census`, navigates to `CENSUS_SURFACES[key]` where `key` is a
CALLER'S ARGUMENT -- a destination that does not exist until a caller picks
one, and which no static reader can attribute.

**That refutation is worth more than the claim I was making** (section 6.3).
The test was renamed to what it measures and the third shape got its own test.

---

## 6. `known_side_effects` MAKES ENUMERATION CLAIMS AND NOTHING CHECKED THEM

**VERIFIED-BY-INSTRUMENT.** Commit `d1b1a62`,
`tests/test_a_named_cost_names_a_tool_that_can_incur_it.py`, 7 tests, measured
by AST over `server.py` rather than by grep.

The brief warned that one sentence in this field had been measured false. It
had been repaired at `a86c849`, 21:33, **51 minutes before I read the
neighbouring bullet.** The messaging bullet is wrong in BOTH directions.

### 6.1 TOO LARGE -- it names a tool that structurally cannot incur the cost

The sentence says *"Only `linkedin_open_messaging` and `linkedin_new_messages`
can incur this"*. Measured:

    linkedin_new_messages   -> FEED_URL, and nothing else
    linkedin_open_messaging -> MESSAGING_URL

`linkedin_new_messages` returns `opened_a_conversation: False` and its own
docstring says it *"never loads the messaging surface at all"*.

**THIS DIRECTION IS THE QUIET ONE AND IT HAS A REAL PRICE.** That tool exists
PRECISELY to answer the messaging question without paying for it. Naming it
beside the expensive tool tells a caller the cheap route is expensive -- **so
the field steers a caller away from the one route built to protect the counter
it is warning about.**

### 6.2 TOO SMALL -- the `/mynetwork/` failure, unrepaired one bullet away

`linkedin_compose_fields` navigates to `CENSUS_SURFACES['messaging_compose']`
= `<base>/messaging/compose/`. The sentence names it nowhere.

**This is NOT a claim that it costs what the root costs.** The composer was
measured on 2026-09-01 with the badge at 0 either side and no redirect, and
`dom` records that. **The defect is the SCOPE of the word "messaging" in a
closed claim**: read as the root it is defensible, read as the surface it is
false. That exact ambiguity is what the `/mynetwork/` correction says let its
own bullet stand wrong for two days -- *"read charitably the sentence meant the
root while a caller would read it as the whole surface."*

### 6.3 THE THIRD SHAPE, WHICH OUTRANKS BOTH -- a closed claim cannot be checked

`linkedin_surface_census` navigates to a CALLER-CHOSEN key, and
`messaging_compose` is one it accepts.

> **A closed enumeration cannot be checked against an open navigator.** A
> sentence of the form *"only tools X and Y can incur this"* is UNVERIFIABLE in
> this package while a parameterised navigator exists.

**The `/mynetwork/` fix repaired one sentence's TEXT. The field's FORM is what
keeps producing these.** Either the claim is scoped to statically-addressed
tools and says so, or the parameterised tool is named as able to reach the
family, or the field stops making closed claims.

### 6.4 WHAT I DID NOT DO, AND WHY

**I did not edit the sentence.** Two independent reasons, both this
repository's own rules:

* `linkedin_server/server.py` was DIRTY with another wave's uncommitted lines
  when I looked (22:24), and there is no git-level protection for a
  neighbour's lines inside a file you legitimately name.
* The block has a measured owner by `git log --oneline -3 -- <path>`:
  `a86c849`, 21:33, the wave that repaired the adjacent bullet. **Route the
  artifact, not the verdict.**

So the tests **assert TODAY'S DEFECT**. Green means present-and-recorded;
repairing the sentence turns them RED, which is the point -- *a known defect
must not be fixable in silence, and the record of a defect may not outlive the
defect.* Each test's docstring says what a red means and what to delete.

### 6.4a THE CLAIM HAS A SECOND HOME, AND IT IS THE WORSE ONE

**Found at 22:40, after section 6 was written.** `README.md` line 493 restates
the messaging bullet including its closed clause, with the same two tool names:

    Only `linkedin_open_messaging` and `linkedin_new_messages` can incur
    this, and only when called

**So the defect exists TWICE, and a repair applied to one copy leaves the other
standing.** A README is worse than the field it copies: `known_side_effects` is
read by a caller weighing one call, but a README is a STANDING INSTRUCTION read
as current truth by whoever opens the repository next, and it carries no
`CORRECTED BY:` mechanism at all -- the correction machinery governs
`_audit/*.md` only.

**AND THE README CONTRADICTS ITSELF FOUR LINES LATER.** Its next bullet says
*"the message composer is on the surface point 3 describes"* -- which is
`linkedin_compose_fields`' destination, and point 3 does not name it. **The
premise and its own counterexample sit in the same document, a few lines
apart.** Nobody needed a browser, an AST walk or a live load to catch that;
they needed to read two adjacent bullets as one claim.

**NOT EDITED, same ruling as 6.4.** `README.md` was committed at 22:33 --
six minutes before I read it -- by a wave actively working that file
(`e1a81e9`). Route the artifact.

**What landed instead is a DIVERGENCE DETECTOR**: a test asserting the two
copies name the SAME tool set. Today they agree, both wrong identically; it
fires the moment they stop agreeing, which is exactly what a one-sided repair
looks like. Shown failing by a third mutation that simulates precisely that --
the README copy repaired, `server.py` left alone: 1 failed, 8 passed.

### 6.5 SHOWN FAILING BEFORE IT ENTERED

Per the register's second law. Two mutations, on a copy, each asserted to have
actually changed the source -- **a mutation that does not apply prints PASS**:

    blind the family classifier   4 failed, 3 passed
    blind the goto detector       4 failed, 3 passed

The second is the exact guaranteed failure mode the control exists for: **both
defect tests are of the form "this tool does NOT navigate to messaging", and a
reader that finds no navigation anywhere satisfies both.**
`test_the_reader_finds_a_true_positive` is the detector factored out of the
assertion, and both defect tests were shown sensitive to the reader dying.

---

## 7. HAND-OFFS, BY ARTIFACT

| to | what | artifact |
|---|---|---|
| owner of `known_side_effects` (`a86c849`) | the messaging bullet is wrong in both directions; and the field's FORM cannot express a checkable closed claim | `tests/test_a_named_cost_names_a_tool_that_can_incur_it.py`, 7 tests, `d1b1a62` |
| whoever owns the blockers ledger | rows 17/67 relayed zero is refuted by a direct count; 12 menu items need no press; rows 66's two rows are answered; row 50's `+1` is a measured unknown | section 2, and `scripts/_probe_messaging_surface_census.py` re-runs it |
| owner of `tests/test_click_is_not_its_own_evidence.py` | the digit-adjacency ruling is UNCHANGED. No chip was observed, so this load produced no evidence either way | section 2.5 |
| whoever re-costs this family | row 57's blocker is unreachable by any read, because a chip requires a committed recipient | section 2.5 |

**The cheapest single open item is now the 12-versus-12 question** in section
2.3 -- whether the 12 `role=menuitem` elements and the 12 `React`-labelled
controls are the same twelve. It needs the menu items' labels on a live
conversation, so it needs a `/messaging/` load AND a ruling about reading
labels on that surface. It is the only thing standing between rows 17/67/76
and a clean retirement recommendation.

**The next cheapest is NOT an href census.** Both of this wave's address
readings are blind to a destination drawn as a button rather than an anchor,
and section 2.9 says so. If row 50's surface exists, that is where it is.

---

## 8. PROVENANCE

Recomputed at freeze, not re-read from the sections above. The two counts most
worth recomputing are the ones that flatter, and both moved: page loads 3 -> 4
(the feed-side probe added one), commits 3 -> 6.

    commits            697b609  the census probe, planned before spent  320 ins
                       a373547  restore the body a rewrite ate          152 ins
                       d1b1a62  the enumeration-claim instrument        457 ins
                       38ea9dc  this document, first form               510 ins
                       e4a7947  the feed-side family probe              206 ins
                       f6a4fd1  section 2.9 and the freeze recount    119 ins
                       fdc063c  section 3a, the row-mapping limit       37 ins
                       + the commit carrying this line, which is the 8th.
                       A count that names its own commit has to include it:
                       the earlier "6" was correct when written and stale by
                       the time the file was saved, which is the same defect
                       this document records twice elsewhere.
    files              scripts/_probe_messaging_surface_census.py    472 lines
                       scripts/_probe_messaging_family_off_the_feed.py 206 lines
                       tests/test_a_named_cost_names_a_tool_that_can_incur_it.py
                                                                     457 lines
                       _audit/2026-09-05-messaging-rows.md           682 lines
    tests added        9, all passing. 3 mutations shown KILLING a test,
                       each asserted to have changed the source first --
                       a mutation that does not apply prints PASS.
                       The third simulates a ONE-SIDED repair of the claim
                       (README fixed, server.py not) and the divergence
                       detector caught it: 1 failed, 8 passed.
    taint guards       279 passed with the census probe;
                       274 passed with the feed probe, green on first run
    exact-value sweep  run AFTER staging every time, per the gate-time rule.
                       Four readings, and the ORDERING is what they say:
                         0 hits / 361 files    before the first commit
                         0 hits / 366 files    after staging the instrument
                         0 hits / 367 files    after staging this document
                         0 hits / 368 files    after staging the feed probe
                       The corpus grew by 7 files across them. Only the last
                       says anything about the tree this wave closed on.
    /messaging/ loads  1
    other page loads   3, all /feed/, an address every badge read uses
    total navigations  4
    controls pressed   0
    writes fired       0
    boundary changes   0
    rows retired       0
    AI attribution     0 across all commits (grep over each body, recomputed
                       at freeze rather than asserted from the first check)
    pushed             nothing

**Every count in section 2 is reproducible**: re-run the probes. The census
refuses on a non-zero messaging badge, refuses on an unreadable badge at either
end, and reports what it spent in its own finally. The feed probe spends
nothing on the messaging counter at all.

**No real person's name, no member id, no slug, no urn, no thread id and no
href appears in anything this wave wrote.** Neither probe can emit one: they
read no page strings.

### One number in this document is NOT mine and is marked as such

*"0 triggers and 0 menu items in 1.28 MB of DOM"* (section 2.2) is relayed from
`_audit/_scratch/_progress-measure-surfaces.md` via the predecessor's own
document, which relayed rather than confirmed it. **I refute the conclusion
with a direct count and I do not vouch for the reading.** Route the artifact.
