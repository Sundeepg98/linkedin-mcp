# The DECIDE-RETIRE queue, ruled

**CORRECTS:** `_audit/2026-09-03-linkedin-gap-blockers.md` -- its section 3 files
`MESSAGING-SETTINGS` as a blocker awaiting a ruling, and its section 7 leaves open
whether those five rows "were already ruled"; they were, by a capability-level
settings ruling shipped in `linkedin_server/server.py` and quoted below, so the
five are a RE-FILE and not a decision anybody still owes.

**CORRECTS:** `_audit/2026-09-03-linkedin-gap-blockers.md` -- its section 4 says the
twelve DECIDE-RETIRE rulings convert 39 rows, and that the answer "is almost
certainly no" for all of them. Three rows of `AI-INTERVIEW-PRODUCT` and two of
`OFF-PLATFORM-WIDGET` are not retired by any reason this pass could find, so the
queue converts 37 rows and hands 5 back as gaps rather than 39 and none.

**THE NUMBER: 37 rows leave GAP, not 39.** Twelve blockers plus
`PANEL-NOT-OBSERVED` -- 42 rows after Amendment A13 -- were walked one row at a
time. **32 rows are retired by a ruling written here. 5 more are re-filed against
a ruling that already existed. 5 are handed back as genuine gaps**, under two new
blocker names, because the reason the queue offered does not reach them.

**BE CLEAR ABOUT WHAT THIS BUYS, BECAUSE IT IS NOT COVERAGE.** It does not move
the proven capability count by one. Nothing here makes the server able to do
anything it could not do this morning. What it moves is 37 rows out of a number
that has been read all day as an indictment, into a column that says somebody
looked and wrote down why not. The denominator does not change either: 761
capabilities before, 761 after. GAP falls and EXCLUDED-RULED rises by the same
amount, inside a total that is still a floor.

**And it is worth doing only because the reasons are real.** A live audio session
in a separate product with its own camera-and-microphone permission article. A
mobile-only recording LinkedIn's own help page says cannot be made on desktop. A
broadcast that needs an external encoder. A Help Center form filed by somebody
else after his death. A promotion that spends his money. **A retirement you cannot
justify is worse than an open row, because it stops anyone looking again** -- which
is why five rows are handed back rather than counted.

---

## 0. WHAT A RETIREMENT IS HERE, AND WHAT IT IS NOT

A retirement moves a row from GAP to EXCLUDED-RULED. It is a statement about
THIS SERVER, never about LinkedIn and never about the operator:

* **It does not say the capability is worthless.** It says this server is not the
  thing that should hold it.
* **It does not say he cannot do it.** Every capability retired below, he can
  perform himself in the browser this server attaches to, today.
* **It is REVERSIBLE, and every ruling below names the fact that reopens it.** A
  ruling nobody can reopen is a wall, not a decision. Where the reopener is
  "the operator asks", that is said plainly rather than dressed up as a
  measurement.
* **It is scoped to an ACT, not to a surface.** Retiring "broadcast a Live" does
  not retire "read a Live event's page". Retiring "boost a post" does not retire
  "read a post's analytics". Each ruling states what it does NOT reach, because
  a retirement that quietly walls off its neighbours is the failure mode.

**THE EVIDENCE CLASS IS STATED PER RULING.** VERIFIED-BY-INSTRUMENT means a
grep, an import, a machine-checked refusal or a quotation from shipped code.
DERIVED means it follows from something verified. UNTESTED means I am telling
you what I assumed and what would settle it -- section 7 of the ledger this
appends to is the model, and three rulings below carry an UNTESTED line.

---

## 1. THE ROW SETS BELOW ARE A RECONSTRUCTION, AND THAT IS THE WEAKEST THING HERE

**The ledger assigned all 409 rows to blockers and then published only the
COUNTS.** Section 3 names the rows for seven blockers and for no others; the
classifier that produced the mapping is not on disk -- `AI-INTERVIEW-PRODUCT`
appears in exactly two files in this repository, both prose. So for eleven of
the twelve blockers I had to work out which rows they are.

Method: read the blocker NAME as a capability family, find every GAP row in the
four census slices belonging to that family, then check the set against the
stated row count AND the stated R/W split. Both have to match, and where they
did not I say so.

| blocker | rows I reconstructed | count | R/W | class |
|---|---|---|---|---|
| `AI-INTERVIEW-PRODUCT` | `J 132`-`J 145` | 14/14 | 4R/10W matches | **VERIFIED** -- two contiguous census sections (J and K), and the only four read-shaped rows in them are `J 136 137 138 144` |
| `CONTACT-IMPORT` | `N 105`-`N 109` | 5/5 | 5W matches | **VERIFIED** -- census section I is exactly this family; its sixth row `N 110` is already EXCLUDED-RULED |
| `HELP-CENTER-FORM` | `P N30`, `P N31`, `N 152` | 3/3 | 3W matches | **VERIFIED** -- the only three GAP rows in the corpus whose route is a `/help/linkedin/ask/` form |
| `LIVE-BROADCAST` | `P L5`, `M C59` | 2/2 | 2W matches | **VERIFIED** -- the only two go-live rows |
| `DEVICE-GEOLOCATION` | `J 17` | 1/1 | 1R matches | **VERIFIED** -- sole row naming device location |
| `MOBILE-APP-ONLY` | `P A23` | 1/1 | 1W matches | **VERIFIED** -- sole row a help article calls app-only |
| `SIGNIN-INTERSTITIAL` | `P N13` | 1/1 | 1R matches | **VERIFIED** -- sole row naming an interstitial |
| `VOICE-CAPTURE` | `M M19` | 1/1 | 1W matches | **VERIFIED** -- sole row needing microphone capture |
| `PAID-BOOST` | `M C71` | 1/1 | 1W matches | **VERIFIED** -- its census cell says "the only capability in this slice that costs currency" |
| `MESSAGING-SETTINGS` | `M M37 M41 M42 M46 M50` | 5/5 | 5W matches | **DERIVED-STRONG** -- the messaging census's own family cell lists SEVEN; `M 24` is claimed by `GROUP-CHAT-SURFACE` (4 rows, 4W, exactly `M 21`-`M 24`) and `M 38` by `REPORTING-FLOWS` (1 row, 1W), leaving these five |
| `AI-ASSIST-MESSAGING` | `M M40`, `M M51` | 2/2 | 2W matches | **DERIVED** -- three rows share the family (`J 150` is the third); see the ruling |
| `OFF-PLATFORM-WIDGET` | `N 50`, `N 76`, `M C72` | 3/3 | 2R/1W matches | **DERIVED-WEAK** -- the only 2R/1W set I could build; see the ruling, which does not depend on it |
| `PANEL-NOT-OBSERVED` | `J 25 29 30` | 3/3 | 2R/1W matches | **VERIFIED** -- named explicitly in Amendment A13 |

**WHY THIS MATTERS AND HOW IT IS CONTAINED.** A wrong row id retires the wrong
capability, silently, and a retirement is exactly the state nobody re-opens to
check. So **every ruling below is written against the CAPABILITY FAMILY, not
against the id list.** The reason has to reach the capability as the census
describes it; the ids are the best available mapping and are marked as such.
Where the ruling and my reconstruction could disagree -- `AI-ASSIST-MESSAGING`
and `OFF-PLATFORM-WIDGET` -- the ruling says what happens under both readings
and the arithmetic is shown to be the same either way.

**A BLIND SECOND RECONSTRUCTION WAS COMMISSIONED AND IT AGREES ON ALL TWELVE.**
It was given the counts and the R/W splits and not my answer, and it records that
it read no sibling product, so it is uncontaminated. Filed at
`_audit/_scratch/_retire-rows-blind-check.md`.

**Read what that is and is not worth.** Two independent readers reaching the same
sets is real corroboration against idiosyncrasy; it is not corroboration against
a shared misreading of the census, because both read the same census. And the
second reader states the honest deflation itself: **on a one-row blocker the R/W
split is a two-bit check**, so the six singletons rest on their capability text
being unique in the corpus rather than on arithmetic.

It puts a live substitution risk on three blockers, each exactly one row wide,
and its list is the same three mine flags:

| blocker | row at risk | what would displace it |
|---|---|---|
| `MESSAGING-SETTINGS` | `M M42` | `M M24`, if the classifier put `M 42` rather than `M 24` in `GROUP-CHAT-SURFACE` |
| `AI-ASSIST-MESSAGING` | either row | `J 150`, if Writing Assistant was read as AI-assist rather than as an addressing failure |
| `OFF-PLATFORM-WIDGET` | `M C72` | nothing that preserves 2R/1W -- so the risk is that all three are wrong together and the blocker means something else by "widget" |

**None of the three changes a count, and each for its own reason.** Exactly one
of `M 24` / `M 42` sits in `MESSAGING-SETTINGS` under either reading and the
other sits in `GROUP-CHAT-SURFACE`, so five rows re-file either way and only the
identity of one of them is uncertain -- and both are settings-family writes that
the ruling in 3.10 reaches identically. `J 150` and whichever messaging row it
would displace fail for the identical reason in 3.6, so two rows retire either
way. And 3.4 is written as a shape rule precisely because the third case cannot
be resolved by arithmetic at all.

---

## 2. THE BOUNDARY IS NOT A REASON, AND ELEVEN OF THESE TWELVE CANNOT BORROW IT

Every address these capabilities live at is refused today. That is nearly
worthless as evidence, and the ledger's own rule says why: *"Everything a
general mechanism merely happens to block is a GAP with a NAMED BLOCKER --
recorded so nobody reads GAP as cheap, but not laundered into a decision."*

So the boundary was measured with the two gates reported SEPARATELY, because
`assert_read_url` runs the forbidden-substring loop first and stops -- and
`readonly.py` records that this has already misled three readers into taking a
substring for the wall when the allowlist was the wall.

Receipt: `scripts/_probe_retire_ruling_boundary.py`, output at
`_audit/_scratch/_retire-boundary-evidence.txt`. Four must-allow controls
passed, one must-refuse control fired, zero control failures. 28 allowlist
patterns, 33 forbidden substrings at HEAD.

| family | forbidden substring? | allowlist? | what that is worth |
|---|---|---|---|
| messaging settings | **YES** -- `/psettings/`, `/settings/`, `/mypreferences/d/categories/` | no pattern | a written entry with an argument behind it |
| Help Center form | no | no pattern | **nothing.** Default-closed |
| off-domain page | no | no pattern | **nothing** |
| live video, campaign manager, Learning, contact import, checkpoint | no | no pattern | **nothing** |

**Read the second column, not the verdict.** Exactly one of these families meets
a rule somebody wrote; the other eleven meet the default-closed allowlist, which
decided nothing about them in particular. **No ruling below cites a NO-PATTERN
refusal as its reason.** Each stands on the capability.

**A caveat on the one that does.** The five messaging-settings addresses in that
probe are ASSUMED -- no census row names a url, and the ledger declined to
invent one for exactly this reason. What the probe proves is that the ADDRESS
SPACE is refused by a written substring. That LinkedIn serves these five
controls inside that space is DERIVED from the settings-family pattern. It does
not matter to the ruling, which rests on the capability-level ruling in section
3.10 rather than on any address.

---

## 3. THE RULINGS

### 3.1 `AI-INTERVIEW-PRODUCT` -- 14 rows, RETIRE 11, HAND BACK 3

**Rows:** `J 132`-`J 145`. Two products: LinkedIn's Premium AI interview practice
(`a8336402`, rows 132-138) and hirer-invited AI interviews as a hiring stage
(`a10376002`, rows 139-145, not Premium-gated).

**What the capability would be:** the server generates practice questions from a
job description, conducts or completes a spoken interview with a real-time AI
interviewer, ends or declines one in progress, and messages the hirer about it.

**RETIRED -- rows 132, 133, 134, 135, 139 (the session).** The surface is not a
page to read or a control to click. It is a live audio or video session with a
conversational agent, opened in a separate product in a new tab.

* VERIFIED-BY-INSTRUMENT: LinkedIn publishes a help article whose entire subject
  is granting **camera and microphone permission** for this product
  (`a10133010`, browser-settings troubleshooting for four browsers). The jobs
  census read it, ruled it documents no capability of its own, and cited it as
  evidence the product exists. A product with a permissions-troubleshooting page
  for camera and microphone is a media session, and this server has no audio or
  video to give one.
* VERIFIED-BY-INSTRUMENT: the census's own shape cell for 132-138 reads *"a whole
  separate product that opens in LinkedIn Learning in a new tab. Voice capture, a
  real-time conversational agent, and a scored transcript. Structurally out of
  shape for this server."*

**RETIRED -- rows 140, 141, 142 (decisions on a live application).** These are
acts inside a real hiring process with a real employer at the other end.
Row 140 is not reversible: a completed screening interview is submitted. Row 142
is the one the census flagged and it is the sharpest of the three -- LinkedIn
documents declining as safe, *"you will not be automatically disqualified"*, which
means an automated participation decision would be **making a career call, not a
mechanical one**. This repository has fired exactly one irreversible write ever
(`apply_job`, which did not submit), and the ruling that governs it is that a
gate must be able to say what it costs him. Nothing here can price a declined
interview.

**RETIRED -- rows 143, 144, 145 (messages to a human hirer).** All three routes
are, in LinkedIn's own words, contacting the hirer: replying with feedback on the
interview experience (143), requesting your rating, summaries, transcript or
recording (144), requesting an accommodation (145). The content is a personal
statement about his own experience or his own needs. That is the same class the
shipped `auto_accept_or_auto_reply` prohibition names -- *"a reply in his name
that he did not read is a message from a stranger wearing his face"* -- and an
accommodation request is the least automatable message on this census.

  **Row 144 disagrees with itself and I am recording that rather than smoothing
  it.** The ledger's R/W split makes it one of the four reads; its own source
  sentence makes it a message. I retire it as a message. If it turns out
  LinkedIn draws a self-serve results page rather than "contact the hirer", it
  reopens with rows 136-138 below.

  **The blind reconstruction reached the same ambiguity independently, and
  sharpened it: TWO different read-assignments both produce 4R/10W.** Reading
  (a) is `J 136 137 138` plus `J 144`; reading (b) is `J 132 136 137 138`, with
  `J 144` read as the act of contacting a hirer. **The ledger publishes only the
  aggregate, so the split cannot distinguish them** -- which means the R/W column
  is not evidence about `J 144` in either direction, and the source sentence is
  the only evidence there is. That is what the retirement rests on.

**HANDED BACK -- rows 136, 137, 138. The reason above does not reach them.**
These are the READ side: the readiness score, the summary of strengths and areas
to improve, the transcript with worked improvements. They are the RESULTS of a
session. If the operator takes a practice interview himself in his own browser --
which he can, he holds Premium Career -- then reading his own results back is a
page load and a parser, which is precisely this server's shape and one of its
cheapest builds.

The census said so first and nobody acted on it: *"The realistic reachable slice
is the READ side -- a past session's readiness score, summary and transcript, if
they are addressed by a url."* Retiring these three would have retired the one
part of this product the server could plausibly hold.

  **New blocker: `AI-INTERVIEW-RESULTS-NO-ADDRESS` -- 3 rows, 3R, queue MEASURE,
  cost 4** (allowlist +1, capture +1, parser +1, tool +1; ratio 0.75). Nobody has
  looked for the address. **PRECONDITION, and it is his to answer in one
  sentence: has he ever taken one?** If he has not, there are no results to read
  and the rows are unreachable for a reason that has nothing to do with this
  server -- which is a fact about USE and not about REACHABILITY, and the census
  counts reachability. That is why they are handed back rather than retired.

**WHAT REOPENS THE 11:** LinkedIn ships a text-only interview mode with no audio
or video, **or** the practice product exposes its questions and scoring at an
address that renders without a session. Either turns rows 132-135 and 139 from a
media session into a document. Rows 140-142 reopen only on the operator's own
ruling that an automated participation decision is his to delegate; nothing
measurable changes that.

**WHAT THIS RULING DOES NOT REACH:** rows 146-149 (resume tips) are a different
product and are already filed under `FILE-UPLOAD-UNSANCTIONED`, rank 1, DECIDE.
Nothing here touches them.

---

### 3.2 `CONTACT-IMPORT` -- 5 rows, RETIRE 5

**Rows:** `N 105`-`N 109`, census section I. Import contacts from the mobile
address book; import Gmail contacts; choose which device contacts to upload;
select or deselect the connection recommendations an import produces; send
connection requests to the imported contacts you selected.

**What the capability would be:** the server pulls his address book or his Gmail
contacts into LinkedIn's graph and turns the result into connection requests.

**RETIRED, and the five rows retire for three different reasons rather than one:**

* **`N 105` -- LinkedIn documents this as a mobile address-book flow.** A browser
  driver has no address book to offer. Same shape as section 3.9 and it fails for
  the same structural reason. VERIFIED against the census cell; the underlying
  help article was not re-fetched this pass.
* **`N 106` -- a Gmail import is an OAuth consent screen on Google's domain.**
  Reached by a ruling already shipped in this server, verbatim at
  `linkedin_server/server.py:5706-5711`: *"Driving a form on somebody else's
  domain, under their terms, is not this server's to do at any capture quality."*
  That sentence was written about applicant-tracking systems; it is a rule about
  domains, and a Google consent screen is somebody else's domain.
* **`N 107`, `N 108` -- sub-steps inside an import that cannot start.** They are
  retired WITH the flow and not on their own merits, and that is worth saying
  plainly: if either import route ever reopens, these two reopen with it
  automatically and need no separate argument.
* **`N 109` -- reached by a PERMANENTLY_FORBIDDEN entry.**
  `writes.PERMANENTLY_FORBIDDEN["any_loop_sweep_or_scheduled_write"]` reads *"one
  write per invocation, always. The grant TTL makes an unattended write
  structurally impossible and that is the intended consequence."* A bulk invite
  is a sweep by construction -- the census calls this row *"the
  highest-blast-radius row in the census -- one confirmation sends many
  invitations"* -- so it meets a forbidden key rather than a missing surface.
  VERIFIED-BY-INSTRUMENT: the key and its text were read out of the imported
  module at HEAD.

**The family was already half-ruled.** `N 110`, delete all imported contacts, is
EXCLUDED-RULED in the census under R5. This pass finishes a decision the network
slice had started.

**WHAT REOPENS THEM:** `N 106` reopens if LinkedIn ships an import that completes
inside `linkedin.com` with no third-party consent screen. `N 105` reopens if
desktop gains address-book import. **`N 109` does not reopen while
`any_loop_sweep_or_scheduled_write` stands, and that entry is the operator's --
only he moves it.**

**WHAT THIS RULING DOES NOT REACH:** it retires importing a contact graph INTO
LinkedIn. It says nothing about reading his mail, which the `linkedin-jobs` skill
already does from Gmail with no LinkedIn session at all, and nothing about
`linkedin_send_invitation`, which is built, per-person, and gated.

---

### 3.3 `HELP-CENTER-FORM` -- 3 rows, RETIRE 3

**Rows:** `P N30` (deceased member -- request account closure), `P N31` (deceased
member -- request memorialization), `N 152` (report harassment or a safety
concern).

**What the capability would be:** the server files a Help Center support ticket
on his behalf.

**RETIRED. Two of the three are not his acts at all.** `P N30` and `P N31` are
what somebody ELSE files about HIM, after he dies. The profile census included
them honestly -- they are account-lifecycle capabilities LinkedIn's product
offers -- and marked the shape: *"Not his own act."* A server acting for him
cannot perform an act defined as being performed by another person after his
death. This is the cleanest retirement in the document and it needs no
measurement.

**`N 152` is different and deserves its own sentence.** A harassment or safety
report is an accusation with a consequence for the person named, carried by a
free-text narrative only he can write, filed to a human review queue off the
product surface.

  **Why the obvious counter-argument fails, and it is worth walking because this
  repository already litigated it.** `writes.PERMANENTLY_FORBIDDEN` records that
  `endorse_or_recommend` USED to be refused on the ground *"a statement ABOUT
  ANOTHER PERSON, which is not his to automate"* -- and that reason was
  **retired**, on the operator's own 2026-08-25 ruling that an endorsement is a
  gift to the person receiving it rather than an extraction from them. So "it is
  about another person" is not, by itself, a reason in this repository any more.
  **A safety report is the exact inverse of a gift**, and that is the distinction
  that makes the refusal principled rather than convenient: the person named
  bears the cost, they never consented, and the server cannot read the situation
  that produced the report.

**WHAT REOPENS THEM:** `P N30`/`P N31` reopen only if LinkedIn makes them
self-service acts a living member performs for his own account, which would make
them different capabilities. `N 152` reopens if LinkedIn moves safety reporting
onto an in-product structured surface -- and even then the ruling narrows rather
than lifts: a structured report might be previewable and confirmable; a free-text
accusation is not.

**WHAT THIS RULING DOES NOT REACH:** it retires FILING. It does not retire any
read that would support him -- and nothing here says the server should decline to
help him find the form, draft nothing, and hand him the address.

---

### 3.4 `OFF-PLATFORM-WIDGET` -- 3 rows, RETIRE 1, HAND BACK 2

**This is the ruling my row reconstruction is weakest on, so it is written as a
SHAPE rule that survives being wrong about which rows they are.**

**THE RULE: an act performed on a domain that is not LinkedIn's is retired. A
READ that produces a link, performed ON a LinkedIn page, is not.**

**RETIRED -- pressing a Follow button embedded on a third party's website
(`N 50`).** Reached by the shipped ruling quoted in 3.2 --
`server.py:5706-5711`, *"Driving a form on somebody else's domain, under their
terms, is not this server's to do at any capture quality."* And the capability
is not even lost: the same follow is available on LinkedIn through
`linkedin_follow_company`, which is built and COVERED-UNFIRED. **Only the route
is retired, not the outcome**, which is the least costly retirement here.

**HANDED BACK -- the two read rows.** My reconstruction puts `N 76` (copy your
personal Follow link for use off LinkedIn) and `M C72` (share a post off
LinkedIn) here. Both are filed R by their own census slices, and **the
off-domain ruling does not reach either**: the copy control and the share control
are drawn on a LinkedIn page, and what they produce is a link. Reading a control
on a LinkedIn page is the single thing this server does most.

The blocker's NAME describes the one write. Its 2R are a different capability
wearing the same label -- and retiring them would have walled off two cheap reads
on the strength of a name.

  **New blocker: `LINK-FOR-OFF-PLATFORM-USE` -- 2 rows, 2R, queue BUILD, cost 2**
  (parser +1, tool +1; ratio 1.00). No boundary change asserted, because I have
  not established which page draws either control. **UNTESTED:** if either
  control lives on a page not currently admitted, the cost is 3 and the queue
  is MEASURE. One capture settles it.

**IF MY RECONSTRUCTION IS WRONG,** the shape rule still decides: whichever rows
sit here, the off-domain acts retire and the on-LinkedIn reads do not. **The
arithmetic is unchanged only if the split is 1W/2R, which is what the ledger's
own R/W column says it is.**

**WHAT REOPENS IT:** nothing plausible for `N 50` -- LinkedIn would have to make
a third-party widget drivable without leaving `linkedin.com`, which is a
contradiction. The handed-back reads need no reopener; they are open.

---

### 3.5 `LIVE-BROADCAST` -- 2 rows, RETIRE 2

**Rows:** `P L5` (host a LinkedIn Live), `M C59` (create or broadcast a LinkedIn
Live).

**What the capability would be:** the server starts a live video broadcast under
his name to his network.

**RETIRED.** Going live requires an external encoder or a partner integration --
the messaging census's own recovery pass names `a548518` (broadcasting FAQ),
`a569473` (broadcaster features) and `a523091` (go live via Zoom) -- and the
census cell states the consequence: *"needs a third-party streaming tool, so it
is outside a browser driver regardless."* A browser driver cannot supply a video
stream. DERIVED from LinkedIn's own documentation as read by the census; the
articles were not re-fetched this pass.

**The profile slice recorded no reason at all** -- `P L5` reads *"he clears the
>150-follower gate at 275; no tool, no reason."* That is the honest state this
ruling replaces: a row that had been checked for ELIGIBILITY and never for
FEASIBILITY.

**THE RULING IS ON THE FAMILY, AND THAT IS WHERE ITS VALUE IS.** `M C59`'s own
census section 10 records that the messaging slice **undercounted Live 5:1** and
that its single row *"should be at least five."* Those four-or-more rows are not
in the 409 and this document does not claim them. But because the ruling is
written against the act of broadcasting rather than against two ids, **a future
pass that expands the family inherits the reason and needs no new decision.**

**WHAT REOPENS IT:** LinkedIn ships browser-native go-live with no external
encoder.

**WHAT THIS RULING DOES NOT REACH:** attending, watching, commenting on or
reading a Live event. Those are the events family and remain open.

---

### 3.6 `AI-ASSIST-MESSAGING` -- 2 rows, RETIRE 2

**Rows:** `M M40` (use smart replies / reply suggestions) and `M M51` (use
LinkedIn AI-powered conversation in messaging). `J 150` (send an enhanced message
to a recruiter using Writing Assistant) is the third member of the same family
and my reconstruction could have any two of the three here.

**What the capability would be:** LinkedIn composes a message and the server
sends it under his name.

**RETIRED, by the consent architecture rather than by a missing surface.**

The messaging census was careful to say the existing prohibition does NOT cover
these -- `M 40` is *"never named; the away-message ruling does not cover a
suggestion the operator picks"* and `M 51` is *"adjacent to the
`auto_accept_or_auto_reply` prohibition without being covered by it."* That is
correct, and it is why this needed a ruling rather than a citation. The reason is
one layer down.

VERIFIED-BY-INSTRUMENT, read out of the imported module and its test at HEAD:

* `writes.TYPING_ACTIONS` is `comment_on_item`, `publish_post`, `send_message`.
* `mint` binds a confirm token to a canonical TARGET; for `send_message` that
  target is composite and CARRIES THE MESSAGE TEXT.
* `_render` prints the target; `consume` refuses a token whose rebuilt target
  does not match.
* `tests/test_typed_bytes.py` asserts by AST that the one `page.fill` site in the
  package takes its text from `_text_component_of(spec, grant.target)` and from
  nowhere else -- so *"a future edit that interpolates, truncates, strips or
  decorates the string fails here rather than typing something he never read."*

**The whole gate rests on one claim: the bytes sent are the bytes he read.** An
AI-assisted send has no bytes at mint time -- LinkedIn composes them after the
control is pressed. He would be confirming a message whose content nobody has
read, which is the one thing this design was built to make impossible.

**And notice what is left over, because it is the reason the retirement costs
nothing.** If he presses LinkedIn's assist himself, reads the draft, and hands
the text to `send_message`, that is a built path with his own bytes in it. The
only part of the capability that is missing is the part the architecture exists
to refuse.

**UNTESTED, and named because it is the one route that could reopen this:** I
have not opened the assist control. If LinkedIn's flow fills the composer and
lets you EDIT before sending, then a two-step shape exists -- press assist, read
the composer back, mint a grant on what it actually says, then send. That is not
a small build; `send_message` already reads its composer back and that read-back
is the hardest-won part of it. **WHAT WOULD SETTLE IT: one capture of the
messaging composer with the assist control pressed.**

**WHATEVER THE MEMBERSHIP IS, TWO ROWS LEAVE.** All three candidates fail for the
identical reason, and whichever one my reconstruction displaced lands under a
blocker this ruling does not retire, so the count is 2 either way.

---

### 3.7 `DEVICE-GEOLOCATION` -- 1 row, RETIRE 1

**Row:** `J 17`, search from device current location.

**What the capability would be:** `linkedin_search_jobs` asks the browser where
he is and searches there.

**RETIRED, and NOT on the ground the census gave.** The census says *"needs
browser geolocation permission. Out of shape for this design."* **The
impossibility half of that is false and should not be inherited:** this server
drives a real Chrome over CDP, and CDP can grant and override geolocation. If
anyone retires this as impossible, the next person to check will find it is not,
and will reopen the wrong question.

The two reasons that hold:

* **The capability is already served by a parameter.** `linkedin_search_jobs`
  takes a `location` string, and the jobs census establishes -- across two
  independent help pages, `a507441` and `a523131`, which it calls *"the second
  page to agree"* -- that LinkedIn's job search documents adding locations BY
  NAME and carries **no distance or radius control**. So "current location" is a
  convenience for a human who does not want to type a city; there is no result
  set behind it that a named location cannot reach. An agent always knows the
  city it means.
* **The cost is a durable permission on his real profile.** Granting a page
  geolocation writes a permission into the profile store of the browser he uses
  himself, and it outlives the read. This server's design is about not leaving
  marks; spending a persistent permission grant to save typing a city name is the
  worst trade in this document.

**WHAT REOPENS IT:** the operator wants a search whose location he cannot name --
and the `location` string cannot express it. Both halves are needed.

---

### 3.8 `SIGNIN-INTERSTITIAL` -- 1 row, RETIRE 1

**Row:** `P N13`, sign-in security prompt / email code / CAPTCHA.

**What the capability would be:** the server reads, and by implication answers, an
authentication challenge.

**RETIRED, and this one is retired because holding it would be a defect.** An
authentication challenge exists to test that the actor is the human. A server
that reads and answers one defeats exactly the thing it is for. This package
already names the class: `writes.PERMANENTLY_FORBIDDEN` carries
`any_anti_detection_technique`.

**And the designed response is already built.** VERIFIED-BY-INSTRUMENT, imported
at HEAD: `config.AUTHWALL_MARKERS` is `('/login', '/authwall', '/uas/login',
'/checkpoint/')`, and a landing on any of them is turned into a REPORTED FAILURE.
The census cell says the same and calls it *"adjacent but not this"*. It is
adjacent because the row asks for a READ and the server implements a STOP. **The
ruling is that the stop is the correct behaviour and the read is not a capability
this server should acquire.**

**WHAT REOPENS IT:** nothing that keeps the shape. If the operator wants the
server to report WHICH challenge it hit in more detail, that is a diagnostic
improvement on a path that already exists, not this row.

---

### 3.9 `MOBILE-APP-ONLY` -- 1 row, RETIRE 1

**Row:** `P A23`, name pronunciation audio.

**What the capability would be:** the server records or edits the 10-second audio
clip of his name on his profile.

**RETIRED, refused twice from two independent directions, and neither is the
allowlist.**

* **LinkedIn's own article says desktop cannot do it.** `a550527`, as read by the
  profile census: max 10 seconds, **mobile iOS/Android app only**, cannot be
  recorded or edited on desktop, only deleted. A browser-driven server
  structurally cannot record it.
* **The one verb desktop does offer is already forbidden.** Deleting it meets
  `writes.PERMANENTLY_FORBIDDEN["delete_or_withdraw_anything"]` -- *"destruction
  is not a write this design covers, at any confirm level"* -- an entry whose own
  text records that **five WriteSpecs now cite it in `reversible_by`**, so it is
  the least movable line in the package.

**WHAT REOPENS IT:** LinkedIn ships desktop recording for name pronunciation.

**WHAT THIS RULING DOES NOT REACH:** reading whether his profile carries a
pronunciation clip at all. That is a read, it is not this row, and it is not
retired.

---

### 3.10 `MESSAGING-SETTINGS` -- 5 rows, RE-FILED, NOT RETIRED

**Rows:** `M M37` (read receipts and typing indicators), `M M41` (smart features
in Messaging), `M M42` (allow or prevent messages from group members), `M M46`
(opt out of receiving InMail), `M M50` (message nudges).

**THIS IS NOT A NEW DECISION. THE OPERATOR ALREADY MADE IT, AND TWO CENSUS
SLICES APPLIED IT DIFFERENTLY.** The ledger's section 7 flagged this as one of
four things it could not settle. It is settled, and the settling artifact is
shipped code rather than an inference.

**The ruling, VERIFIED-BY-INSTRUMENT in three places at HEAD:**

* `linkedin_server/server.py:6476-6484`, in the live `linkedin_update_setting`
  docstring: *"The read allowlist admits exactly one page below the settings
  index, admitted BY NAME on the operator's ruling... a setting is admitted by
  name or not at all -- and it is why this tool shipping does NOT mean the next
  setting is a small step."*
* The same tool's refusal message for any other setting name repeats it and
  loads nothing.
* `writes.PERMANENTLY_FORBIDDEN` is not where it lives; the `update_setting`
  WriteSpec's own residue is: *"TWO OF THE THIRTY-THREE ADDRESSES ARE ACCOUNT
  DESTRUCTION -- 'Close and delete account' and 'Hibernate account' -- and they
  sit in the same url family as 'Dark mode'... a permission written for the
  family would carry those two with it, so a setting has to be admitted BY NAME
  or not at all."*

**The profile census applied this ruling to 93 settings rows and filed every one
EXCLUDED-RULED**, stating it exactly: *"The settings-family ruling is
capability-level, not path-level. It says a setting is admitted BY NAME or not
at all. That excludes every page below the settings index whatever its URL
spelling."* The messaging census filed its five as GAP. **Same ruling, two
slices, opposite states.** The ruling says "a setting", not "a profile setting",
and these five are settings.

**So the five are RE-FILED to EXCLUDED-RULED under an existing ruling, not
retired under a new one.** The distinction is not pedantry: a re-file says the
number was wrong, a retirement says somebody has now decided. Only one of those
is true here, and reporting the wrong one would credit this pass with a decision
the operator made weeks ago.

**WHAT REOPENS ANY ONE OF THEM: the operator names it.** That is not a
consolation, it is the mechanism -- it is exactly how `/mypreferences/d/dark-mode`
got in, by name, with a WriteSpec and a reversibility story. The family is closed
by default and opens one leaf at a time, and the cost is roughly one allowlist
entry, one WriteSpec, one consent line and one reversibility argument per leaf.

**A NOTE ON `M M46` THAT SHOULD SURVIVE THIS RULING.** Opting out of receiving
InMail is the one setting on this list a job seeker might touch by accident and
regret: he WANTS recruiter InMail. It is closed by the ruling above like the
others -- but if it is ever named and opened, it should be opened with the
direction constrained, not just the setting.

---

### 3.11 `VOICE-CAPTURE` -- 1 row, RETIRE 1

**Row:** `M M19`, send a voice message.

**What the capability would be:** the server records and sends an audio message
in his voice.

**RETIRED, and the two reasons are of unequal strength, so both are stated with
their class.**

* **DERIVED (strong):** the composer's control records live audio from a
  microphone. This server drives a browser attached to his profile and has no
  audio input to give one. There is no path in this package that has ever
  supplied media to a page -- `set_input_files` is on the mutation-pattern list
  and in no sanction, which is `FILE-UPLOAD-UNSANCTIONED`, rank 1, still a DECIDE
  row.
* **UNTESTED, and this is the honest limit:** I have not opened the message
  composer. Whether LinkedIn offers a voice note as an ATTACHMENT as well as a
  recording is unknown. **WHAT WOULD SETTLE IT: one capture of the message
  composer with the attachment controls enumerated.**
* **The reason that does not depend on the capture:** a recording that sounds
  like him saying words he did not speak is an identity forgery. That is the
  `auto_accept_or_auto_reply` class -- *"a message from a stranger wearing his
  face"* -- with the face made audible. This is a policy reason, and this
  repository has already had one policy reason overturned by a measurement
  (`endorse_or_recommend`), so it is offered as the weaker of the two and not the
  load-bearing one.

**WHAT REOPENS IT, AND IT REOPENS AS A DIFFERENT ROW:** if the composer turns out
to accept an audio FILE, and the operator supplies a recording he made himself,
then the server is transmitting his own bytes and the blocker is
`FILE-UPLOAD-UNSANCTIONED`, not this one. **The retirement is scoped to
RECORDING, not to sending.**

---

### 3.12 `PAID-BOOST` -- 1 row, RETIRE 1

**Row:** `M C71`, boost a post (paid promotion).

**What the capability would be:** the server spends his money to promote a post.

**RETIRED. This is the only capability in the census that costs currency**, in
the messaging census's own words, and it is the cleanest retirement here.

* **This server has no payment authority and must never acquire one.** There is
  no confirm-token shape for an amount: the gate architecture binds a token to a
  canonical target, and a boost's target is a budget, a duration and an audience
  chosen across a multi-screen wizard, not a control with a value.
* **Every WriteSpec's consent line has to say WHAT IT COSTS HIM.** For every
  other write in this package that is attention or reputation -- costs the design
  can describe. Here it is money, and the amount is not knowable before the flow
  is entered.
* **There is no undo.** `delete_or_withdraw_anything` is permanently forbidden,
  and spend is not refundable regardless.

**WHAT REOPENS IT:** nothing that keeps the shape.

**WHAT THIS RULING DOES NOT REACH, and it matters because the neighbour is one of
the best-value rows on the census:** reading a post's analytics, including the
performance of a boost he ran himself, is a READ. The messaging census's
analytics family -- four addresses, none on the allowlist -- is called *"still
the best value-per-risk in the whole slice"* and is untouched by this ruling.

---

### 3.13 `PANEL-NOT-OBSERVED` -- 3 rows, RETIRE 3, on the measurement already taken

**Rows:** `J 25` ("Why am I seeing this job?"), `J 29` (Skills Match insight),
`J 30` (add a missing skill from the insight; depends on `J 29`).

**Queue move: MEASURE to DECIDE-RETIRE, then retired here.** Amendment A13 argued
the move on evidence and left it, noting that section 3's `ruling` column still
reads `no` for this blocker and disagrees with A13 until someone edits it. **This
document is that edit, made as an append rather than in the table**, for the
reason A7 gives.

**No new measurement was taken. The one already on the record is sufficient and
is restated so the ruling can be audited without opening A13:**

* A CONTROL with a known value -- the needles `Show match details` /
  `Show Premium Insights` / `How you match` must read **1/1/0** on a settled
  posting -- reproduced 1/1/0 on **four committed captures**, all confirmed
  present on disk that pass.
* The same control reads **0/0/0 on exactly the two captures the fixture table
  independently marks un-hydrated**, so it discriminates settled from
  half-rendered rather than merely firing.
* It reproduced **1/1/0 LIVE, twice**, across a full browser stop and restart.
* On all four settled captures and both live reads, **every target needle reads 0
  in visible text and 0 in html**: `Why am I seeing this job`, `Why am I seeing
  this`, `why am i`, `seeing this`, `Skills Match`, `skills match your profile`,
  `of 10 skills match`, `Add skill`. The loosest probe, the bare token `skill`,
  reads 1, and that occurrence sits inside `<strong>` with `<br>` siblings --
  job-description prose, not a panel.
* The page carries `aria-expanded="false"` x10 and `aria-expanded="true"` x0, and
  no aria-label on it mentions matching or skills.

**THE PANELS ARE ABSENT, NOT COLLAPSED.** A capability row naming a panel
LinkedIn does not draw is not a gap in this server; it is a row about LinkedIn's
product. There is nothing to parse. `J 30` has no host control once `J 29` is
absent, and the census already records that dependency.

**THE STATED LIMIT, and it is the right one:** this was measured on HIS account,
on postings he opened, in one locale. Whether LinkedIn draws these panels for
other accounts is unknown -- **and irrelevant, because this server only ever
reads his.** The scope of the measurement matches the scope of the server
exactly, which is the strongest form this evidence can take.

**WHAT REOPENS IT, and it is cheap and already scripted:** the control reads
1/1/0 -- proving the page is settled and the reader can see -- AND any target
needle reads non-zero. That is one probe run against one capture. **A zero
without the control firing reopens nothing**, per the render gate: a read of zero
from a surface whose control did not fire is a fact about the instrument.

**ONE THING OWED THAT THIS PASS DID NOT DO.** A13 records that `/jobs/view/<id>`
earned a settled-control baseline of **193** -- two readings, identical on every
structural count, across a browser restart -- and belongs in
`server.CENSUS_SETTLED_CONTROLS` under a `job_posting` key. That edit is still not
made. **`linkedin_server/server.py` is a contended file with other waves writing
it, so this pass did not touch it.** It is owed and it is routed by artifact: the
baseline is A13's, and whoever next holds `CENSUS_SETTLED_CONTROLS` should carry
it.

---

## 4. THE FIVE ROWS I DID NOT RETIRE

Collected in one place, because they are the part of this document most likely to
be skipped and they are the reason the rest can be trusted.

| rows | why the queue's reason does not reach them | new blocker | queue |
|---|---|---|---|
| `J 136 137 138` | they are the RESULTS of a session, not the session. Reading his own readiness score, summary and transcript is a page load and a parser | `AI-INTERVIEW-RESULTS-NO-ADDRESS` (3R, cost 4) | MEASURE |
| `N 76`, `M C72` | both are READS drawn on a LinkedIn page whose product is a link. The off-domain ruling reaches the act, not the read | `LINK-FOR-OFF-PLATFORM-USE` (2R, cost 2) | BUILD |

**Both new blockers are READS, and reads are where this census's cheap work has
been all along** -- the ledger's section 8 measured 43 of the 88 costed blockers
as needing no WriteSpec at all, carrying 141 rows between them. Handing these
five back adds two more.

**Neither is a large build and neither needs a ruling.** That is precisely why
retiring them would have been the expensive mistake: a retired row is not
re-examined, and these two families are cheaper than most of what the BUILD queue
already holds.

---

## 5. THE ARITHMETIC, CLOSED RATHER THAN ASSERTED

**The base.** Section 4's queue table as amended by A13, re-summed here rather
than trusted. A13 moved `PANEL-NOT-OBSERVED` (3 rows) to DECIDE-RETIRE,
`CONVERSATION-OVERFLOW-MENU` (10 rows) to DECIDE, `N 194` from MEASURE into
`SEARCH-RESULTS-SURFACE` (DECIDE), and `C 11` out of the row set entirely.

    queue           blockers   rows
    MEASURE              23     105
    BUILD                34     113
    DECIDE               13      84
    DECIDE-RETIRE        13      42
    RE-FILE               7      29
    NOT-OURS              2      21
    BLOCKED               5      14
    -------------------------------
                         97     408

**408 and not 409, and the one-row difference is A13's `C 11`** leaving the row
set for EXCLUDED-RULED. A13 states that subtraction inside its MEASURE
arithmetic and does not restate the queue total; this is that consequence, not a
new claim.

**This pass.**

    RETIRED BY A RULING WRITTEN HERE
      AI-INTERVIEW-PRODUCT      11 of 14   (3 handed back)
      CONTACT-IMPORT             5 of 5
      HELP-CENTER-FORM           3 of 3
      OFF-PLATFORM-WIDGET        1 of 3    (2 handed back)
      LIVE-BROADCAST             2 of 2
      AI-ASSIST-MESSAGING        2 of 2
      DEVICE-GEOLOCATION         1 of 1
      MOBILE-APP-ONLY            1 of 1
      SIGNIN-INTERSTITIAL        1 of 1
      VOICE-CAPTURE              1 of 1
      PAID-BOOST                 1 of 1
      PANEL-NOT-OBSERVED         3 of 3
      ------------------------------------
                                32 rows

    RE-FILED UNDER A RULING THAT ALREADY EXISTED
      MESSAGING-SETTINGS         5 of 5
      ------------------------------------
                                 5 rows

    TOTAL LEAVING GAP           37 rows

    HANDED BACK, STILL GAP
      AI-INTERVIEW-RESULTS-NO-ADDRESS   3   MEASURE
      LINK-FOR-OFF-PLATFORM-USE         2   BUILD
      ------------------------------------
                                        5 rows

    42 - 37 = 5.  DECIDE-RETIRE ends EMPTY.

**The queue table after this pass.**

    queue           blockers   rows
    MEASURE              24     108      (+1 blocker, +3 rows)
    BUILD                35     115      (+1 blocker, +2 rows)
    DECIDE               13      84
    DECIDE-RETIRE         0       0      (-13 blockers, -42 rows)
    RE-FILE               7      29
    NOT-OURS              2      21
    BLOCKED               5      14
    -------------------------------
                         86     371

    408 - 37 = 371.   97 - 13 + 2 = 86.

**THE DENOMINATOR DOES NOT MOVE.** 761 capabilities before, 761 after. This pass
moved rows between STATES inside it -- GAP falls by 37 and EXCLUDED-RULED rises
by 37. Anyone reporting this as coverage is reporting it wrong.

**THE MASTER GAP TOTAL, with its caveat stated rather than buried.** Against the
ledger's own frozen 409-row set, GAP goes **409 to 372**. Against A1's HEAD
figure of **390** -- the frozen 409 less nineteen rows A1 subtracted as already
refused, closed or double-counted, none of which overlap with the DECIDE-RETIRE
queue -- GAP goes **390 to 353**.

**353 is DERIVED and was not re-verified this pass.** Re-confirming 390 against a
live HEAD in a tree a dozen waves are writing was out of scope, which is the same
caveat A13 gave for the same arithmetic and for the same reason. **A11 already
demonstrates how fast that number goes stale.** A13's flagged-but-not-taken
`C 11` subtraction would make it 352; that subtraction is A13's to take and this
pass does not take another wave's.

---

## 6. EVERY REOPENER, IN ONE TABLE

A retirement that cannot be reopened is a wall. These are the facts that reopen
each one, and they are deliberately concrete enough to be checked.

| ruling | rows | what reopens it | who can establish it |
|---|---|---|---|
| `AI-INTERVIEW-PRODUCT` session | `J 132`-`135`, `139` | a text-only interview mode, or an address that renders the practice product without a session | a capture |
| `AI-INTERVIEW-PRODUCT` live application | `J 140 141 142` | nothing measurable -- only the operator ruling that an automated participation decision is his to delegate | the operator |
| `AI-INTERVIEW-PRODUCT` hirer messages | `J 143 144 145` | `J 144` alone reopens if the rating and transcript prove self-serve rather than "contact the hirer" | a capture |
| `CONTACT-IMPORT` | `N 105`-`109` | 106: an import completing inside `linkedin.com`. 105: desktop address-book import. 107/108 follow either. **109: only the operator moving `any_loop_sweep_or_scheduled_write`** | mixed |
| `HELP-CENTER-FORM` | `P N30 N31`, `N 152` | N30/N31: LinkedIn makes them self-service for a living member. N 152: an in-product STRUCTURED report, and even then the narrative stays his | LinkedIn |
| `OFF-PLATFORM-WIDGET` | `N 50` | nothing plausible -- a third-party widget drivable without leaving `linkedin.com` is a contradiction | -- |
| `LIVE-BROADCAST` | `P L5`, `M C59` | browser-native go-live with no external encoder | LinkedIn |
| `AI-ASSIST-MESSAGING` | `M M40 M51` | the assist control fills an EDITABLE composer, making a read-back-then-mint shape possible | **one capture of the composer with assist pressed** |
| `DEVICE-GEOLOCATION` | `J 17` | he wants a search whose location he cannot name AND the `location` string cannot express it -- both halves | the operator |
| `SIGNIN-INTERSTITIAL` | `P N13` | nothing that keeps the shape | -- |
| `MOBILE-APP-ONLY` | `P A23` | desktop recording for name pronunciation | LinkedIn |
| `MESSAGING-SETTINGS` | `M M37 M41 M42 M46 M50` | **the operator names one.** That is the mechanism, not a consolation -- it is how dark mode got in | the operator |
| `VOICE-CAPTURE` | `M M19` | the composer accepts an audio FILE -- and then it reopens as `FILE-UPLOAD-UNSANCTIONED`, not as this | **one capture of the composer** |
| `PAID-BOOST` | `M C71` | nothing that keeps the shape | -- |
| `PANEL-NOT-OBSERVED` | `J 25 29 30` | the control reads 1/1/0 AND a target needle reads non-zero. **A zero without the control firing reopens nothing** | one probe run |

**Three reopeners are one capture each and two of those are the same capture** --
the message composer settles both `AI-ASSIST-MESSAGING` and `VOICE-CAPTURE`. That
is the cheapest un-retirement available and it is worth knowing before anyone
argues either ruling.

---

## 7. THE STATED LIMIT

**What is soft here, named rather than left to be discovered:**

1. **The row sets for eleven of the twelve blockers are a reconstruction**, not
   the classifier's. A blind second reader reproduced all twelve, which rules out
   idiosyncrasy and **does not rule out a shared misreading, because both read the
   same census.** Section 1 grades each one and names the three rows that could
   substitute; two rulings are written to survive being wrong about membership.
2. **`M C72` and `N 76` may not be in `OFF-PLATFORM-WIDGET` at all.** If they are
   not, this document has handed back two rows that were never in the queue, and
   the count of rows leaving GAP rises toward 39 rather than falling to 37. The
   shape rule in 3.4 is what decides in either case.
3. **Three rulings carry an UNTESTED line** -- `AI-ASSIST-MESSAGING` (the assist
   control), `VOICE-CAPTURE` (the composer's attachment set) and
   `LINK-FOR-OFF-PLATFORM-USE`'s cost (which page draws the control). Each names
   the capture that settles it.
4. **No help article was re-fetched this pass.** Every citation to `a8336402`,
   `a10376002`, `a10133010`, `a550527`, `a548518`, `a569473`, `a523091`,
   `a507441`, `a523131`, `a7443434` is the census's reading of it, inherited. The
   census walked them; this pass did not re-walk them.
5. **No page was loaded and no browser was driven.** Everything measured here was
   measured by importing `linkedin_server` at HEAD and by reading committed
   markdown. `PANEL-NOT-OBSERVED` rests entirely on A13's measurement, restated
   and not re-taken, as instructed.
6. **353 is derived from a number this pass did not re-verify** -- see section 5.
7. **761 is still a floor.** Three passes grew it 661 to 721 to 761 and the
   covered count never moved once. Retiring 37 rows says nothing about the rows
   no pass has found, and `M C59`'s own 5:1 undercount is a live example inside
   this very document.

**What is NOT soft:** the shipped-code quotations in 3.2, 3.3, 3.6, 3.9, 3.10 and
3.12 were read out of the imported modules and their tests at HEAD, not off any
agent's report; the boundary table in section 2 has four passing must-allow
controls and one firing must-refuse control on the record; and the arithmetic in
section 5 closes in both directions.

---

## 8. PROVENANCE

* Rows parsed from `_audit/_census/{jobs,profile,messaging-and-content,network}.md`.
* Blocker counts and R/W splits from section 3 of
  `_audit/2026-09-03-linkedin-gap-blockers.md`; queue totals from its section 4
  as amended by A13.
* `PERMANENTLY_FORBIDDEN` keys and texts, `PERFORMABLE`, `TYPING_ACTIONS`,
  `_COMPOSITE_TARGET_KINDS` and `config.AUTHWALL_MARKERS` read by importing the
  modules under `venv/Scripts/python.exe` at HEAD.
* Boundary refusals machine-checked by `scripts/_probe_retire_ruling_boundary.py`,
  which reports the substring gate and the pattern gate separately; output at
  `_audit/_scratch/_retire-boundary-evidence.txt`. 5 controls, 0 failures.
* Blind second reconstruction of the row sets:
  `_audit/_scratch/_retire-rows-blind-check.md`.
* Working log: `_audit/_scratch/_progress-retire-rulings.md`.
* No browser, no LinkedIn session, no page load, no `mcp__linkedin__*` call. No
  identifier of any person appears in this document; capabilities and relations
  only.
