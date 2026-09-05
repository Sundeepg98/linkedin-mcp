# People search: the one ruling, and the one thing nobody has measured

Date: 2026-09-05. `SEARCH-RESULTS-SURFACE`, ranked 3rd by rows-per-cost in the
blocker ledger. **This document decides nothing. It exists so one decision can
be made in two minutes, consistently with the two he has already made.**

---

**CORRECTED BY:** `_audit/2026-09-05-search-results-measured.md` -- the instrument this document says has never been read WAS read at 14:24 the same day (LOAD A, headline 108, twice, stable), and taking it did not produce the evidence the fork below promised: the counter's caption came back redacted, which class of search feeds it is open, and the AFTER half needs the very act this ruling gates

## 0. THE SENTENCE THAT GOES FIRST

**I could not establish that opening a people-search results page leaves the
people it lists untouched, and nobody in this repository ever has.** The claim
that a search is cheaper than a profile view is not measured here in either
direction -- not confirmed, not refuted.

What makes that a finding rather than a shrug: **the instrument that would
settle it exists, sits on his own account, costs no third party anything, and
has never been read.** LinkedIn shows a member their own *Search appearances*
-- how often they turned up in other people's searches. That is the receiving
end of exactly the signal a people search emits, and it is the same class of
instrument that MEASURED the profile-view question and closed it. It is already
in the ledger as `SEARCH-APPEARANCES-SURFACE`: 2 rows, both reads, both on his
own data, `allowlist +1`, cost 4, queue BUILD, **ruling: none needed**.

So the honest shape of the decision is not "rule on 21 rows". It is:

> **Rule now on 19 reads with the emission unmeasured, or spend one page load
> on his own analytics page first and rule on evidence.**

---

## 1. WHAT WAS DONE AND NOT DONE

No browser was launched, no LinkedIn session opened, no page fetched, no
`mcp__linkedin__*` tool called, no write performed, no boundary widened by one
character, and the profile lock was not touched. Two measurements below were
taken in-process, importing the package on disk under `venv/Scripts/python.exe`
with no network: the read boundary was asked about candidate addresses, and the
two person-card parsers were fed a synthetic record. Every string fed in was
invented; no real member's name, headline, slug or id appears in this document
or in the probe that produced it
(`_audit/_scratch/_probe_search_surface_desk.py`, untracked).

---

## 2. THE PRECEDENTS. There are THREE, and the third is two days old

### R1 -- what `linkedin_who_viewed_me` may EMIT

`writes.PERMANENTLY_FORBIDDEN["deanonymise_a_viewer"]`, verbatim:

> "six of ten profile viewers chose anonymity; the row LinkedIn renders him is
> the whole of what he is entitled to"

and the tool's own docstring holds the same line: *"This server makes no
attempt to work out who they are, and there is no code here that could...
What you get is the row LinkedIn already put on your screen."*

**THE PRINCIPLE: THE RENDERED ROW IS THE CEILING.** Where LinkedIn has already
put a person in front of him, reading that row back is his to have. Adding
anything to it -- joining, resolving, de-anonymising -- is not.

### R2 -- what this server may DO to a third party to learn something

`writes.PERMANENTLY_FORBIDDEN["load_a_third_partys_profile_to_measure_a_control"]`,
verbatim and in full:

> "ADDED 2026-08-30, and it is the rule the endorsement ruling above rests on
> rather than a restatement of it. A profile view is an EMISSION, and this
> server can read the receiving end of that signal: linkedin_who_viewed_me
> returns rows, reaching 365 days back on his Premium Career account, and every
> row is somebody who loaded a profile and left a record its owner can still
> read most of a year later. So loading a stranger's profile in order to find
> out what controls it carries spends THEIR privacy on OUR measurement, and the
> cost lands entirely on somebody who is not him. Whether HE chooses to open a
> profile is his own affair; this server may not do it for a measurement"

**THE PRINCIPLE: AN ACT THAT EMITS SPENDS SOMEBODY ELSE'S PRIVACY, AND THE
EMISSION IS A MEASUREMENT RATHER THAN A WORRY.** Two halves, and the second is
what gives the first its force -- the refusal is not caution, it is a reading
taken from the far end of the signal by an instrument this server already ships.

### R3 -- the operator's own ruling, 2026-09-04

`linkedin_server/readonly.py` removed the third-party profile pattern from the
read allowlist. Its replacement comment says what decided it:

> "THE ALLOWLIST ADMITTED WHAT THIS SERVER'S OWN DOCUMENTATION SAYS IT NEVER
> DOES... **NOT 'NOTHING USES IT, SO CLOSE IT' -- that is the weaker argument
> and it was rejected. The measurement is the second reason, not the first.**"

**THE PRINCIPLE: THE BOUNDARY MUST SAY WHAT THE SERVER CLAIMS, AND AN OPEN
ADDRESS NOBODY RULED ON IS A DEFECT EVEN WHEN NOTHING USES IT.** Verified in
this session: `https://www.linkedin.com/in/someone-else/` is REFUSED at HEAD,
`https://www.linkedin.com/in/me/` still ALLOWED.

---

## 3. WHERE A RESULTS PAGE FALLS, AND WHAT IS GENUINELY DIFFERENT

R1 does not reach it: R1 governs what may be added to a row LinkedIn drew, and
a search page draws rows nobody has yet decided may be drawn at all.

R2 is the one that reaches it, and **it reaches it by its PRINCIPLE and not by
its terms.** R2 forbids a specific act -- loading a profile -- on a specific
measurement. A results page is not a profile. So the question is whether the
principle survives the change of surface, and that turns on four claims. Three
of the four are the ones the surface's defenders would raise, and **only one of
them is established.**

| # | claim | evidence class | verdict |
|---|---|---|---|
| D1 | a results load leaves no durable record on the people listed | **UNMEASURED, both ends** | see below |
| D2 | it renders a summary, not a profile | **ASSUMPTION** -- no capture of this page exists anywhere in this repo | not established |
| D3 | he chose the query, not the person | TRUE of the tool that would be built | established, and it cuts both ways |
| D4 | it is the first people-set with no relationship to him | **VERIFIED from source** | established |

**D1 is the whole ruling and it is empty.** LinkedIn's *Search appearances*
panel is the reciprocal instrument, and this package has never read it -- census
rows `N 132` ("Search appearances are never read") and `P G7` ("no tool, no
reason"), plus `_audit/2026-08-22-parity-linkedin.md:17`, which named the
address `/analytics/search-appearances/` a fortnight ago and ranked it the top
unbuilt read. So the profile-view question was settled by a reading and the
search question has never been read from either side. **This is not the same
evidence R2 rests on; it is the absence of that evidence.**

**D2 is an assumption and it should be labelled as one.** `tests/fixtures/`
holds twenty captures. Not one is a search results page of any kind other than
jobs. Nobody in this repository has seen what a people-search card contains.

**D3 is true and it does not only help.** A query-driven tool means no
individual was targeted -- and it also means **he does not choose whose names
leave this process. LinkedIn's ranker does.** Every consent argument this repo
has written turns on the cost landing on somebody who did not agree; a ranker
picking the set is the same fact stated from the other side.

**D4 is the sharpest difference and it runs AGAINST the surface.** Every set of
people this server names today is defined by a relationship to him:
`who_viewed_me` (people who opened his profile), `linkedin_connections` (people
he is connected to), notifications and messages (people who acted toward him).
The nearest counter-example proves the rule -- `linkedin_send_invitation` reads
one label off a suggestion rail of strangers on his own profile, and that label
is deliberately confined to the confirm block: not into `grant.preview`, not
into `grant.target`, not into the `Observation`, not into a log line. **A search
result set would be the first people-set this server enumerates that has no
relationship to him at all.**

---

## 4. THE 21 ROWS, AND THEY ARE NOT ONE QUESTION

**THE LEDGER'S PER-ROW MAP FOR THIS BLOCKER WAS NEVER PUBLISHED.** The
classifier is recorded as `scratchpad/classify.py` and declared disposable; it
is not on disk, and the final document carries counts rather than ids for this
entry. What follows is reconstructed from the census tables. **19 of the 21 are
identifiable with confidence; 2 are not.**

| rows | what they are | R/W | the question |
|---|---|---|---|
| `N 79-95` | search for a person; narrow to People; the 13 filters; multi-location; re-run a recent search | 17 R | **the ruling** |
| 2 unattributed | almost certainly `N 104` (find an organization's Page by searching), `N 161` (search groups) or `N 179` (search events) | 2 R | same ruling if people; weaker if not |
| `N 96` | clear your search history | 1 W | **ALREADY RULED -- see below** |
| `N 4` | send an invitation from a people-search result | 1 W | **A DIFFERENT RULING. Not this one** |

`N 194` (find hiring managers through the #Hiring hashtag) was re-filed INTO
this blocker by amendment A13, taking the ledger's own figure to 22.

**`N 96` needs no answer from him.** Clearing search history is destruction, and
`PERMANENTLY_FORBIDDEN["delete_or_withdraw_anything"]` covers it -- *"destruction
is not a write this design covers, at any confirm level"*. The jobs slice
independently flags the same shape (`delete`/`remove` sit on the mutation-verb
denylist). It is a re-file, not a decision.

**`N 4` must not ride along with the reads.** It is irreversible, visible to a
stranger, and it would extend `linkedin_send_invitation` from the nine-control
suggestion rail on his own profile to any person a ranker returned. Two forbidden
substrings (`/invite`, `invitation`) already stand in its way. **A yes to the
reads is not a yes to this**, and this document says so here so that nobody
later reads one ruling as covering both.

**So the ruling is over 19 reads.** One is already answered; one is a separate
question he is not being asked today.

---

## 5. WHAT IS BUILT AND WHAT WOULD BE NEW

The ledger costs this at 5 with `allowlist +1` and says the parser half is done.
Measured today, that list is one item shorter than it looks and one item longer.

| piece | state |
|---|---|
| read allowlist pattern | **NEW.** VERIFIED: `/search/results/people/`, `/all/`, `/companies/` all refuse at HEAD as REFUSED-NO-PATTERN. **No forbidden substring bites any of them** -- so the cost is one anchored pattern, with no denylist surgery. Controls in the same run behaved: `/jobs/search/` and `/in/me/` ALLOWED, `/in/someone-else/` and `/mynetwork/` REFUSED. Boundary at HEAD: 33 forbidden substrings, 24 allowed patterns, exactly ONE mentioning search and it is `/jobs/search/` |
| query builder | **NEW table, PROVEN pattern.** `linkedin_search_jobs` already builds a filtered search url from validated enum dicts plus `params.append`, and rejects unknown values by naming what it saw |
| card harvest | **BUILT.** `dom.harvest_linked_cards` with `dom.PERSON_HREF` (`/in/([A-Za-z0-9\-_%]{2,})`) is what `who_viewed_me` already uses |
| **card parser** | **NEW -- see the correction below** |
| capture / fixture | **NEW, and it is a live load.** Zero captures of this surface exist |
| tool surface + docstring | NEW |
| refusal text | NEW, and cheap: the shape exists -- `linkedin_connections` shipped registered and refusing, naming the one measurement that would lift it |
| rate discipline, authwall guard | BUILT and automatic |

**CORRECTS:** `_audit/_census/network.md` -- the people-search family line states the parser half is done because parse_person_card exists; measured today, that parser returns nothing at all on a card carrying no Viewed timestamp, and whether the search card carries one has never been captured

**CORRECTS:** `_audit/2026-09-03-linkedin-gap-blockers.md` -- section 5 repeats the same parser-half claim as settled; it rests on an assumption about a page this repository has never opened, which moves it from a fact to an open cost

### The measurement, and the two evidence classes kept apart

Fed a synthetic person card with no relative timestamp -- name, degree badge,
headline, location, mutuals -- and run through both parsers in-process:

    parse_all(10 search-shaped cards, parse_person_card)     -> 0 rows, 10 dropped
    parse_all(10 search-shaped cards, parse_connection_card) -> 10 rows, 0 dropped
                                                                but headline = "3rd degree connection"

* **VERIFIED-BY-INSTRUMENT:** `shape.parse_person_card` REQUIRES a `Viewed
  <when>` line and returns `None` without one. That is a property of the parser.
* **ASSUMPTION:** that a people-search card carries no such line. Nobody has
  captured the page.

The repository already contains the argument, written one day after the census
claim. `shape.parse_connection_card` exists precisely because the same reuse was
attempted for the connections page, and its docstring says why it could not be:

> "That parser REQUIRES a `Viewed <when>` line, and says so as its own
> invariant: 'Every row LinkedIn draws here has one.' That is true of the
> profile-views page and there is no reason it would be true of this one.
> Pointing it at this surface would drop every row and report zero -- the 'zero
> matched' answer that has already cost this repository two wrong diagnoses,
> arriving from a page full of people."

The word *here* is doing the work. And `parse_connection_card` is not the
substitute either: on the same synthetic card it parses all ten rows and puts
the degree badge in the headline field. **A search-result shaper is new work.**

---

## 6. THE RESIDUE, in this repository's own vocabulary

The gate from `_audit/2026-08-30-linkedin-nine.md` -- Q1 consumption, Q2
emission, Q3 mutation, a YES to any one refuses the key, and the burden sits on
the addition rather than on the refusal.

| | reading | class |
|---|---|---|
| **Q1 consumption** | no badge is known on this surface, and none has been looked for | E4 STRUCTURAL ABSENCE -- the weakest class, and the one the settings ruling was careful to label |
| **Q2 emission** | **UNKNOWN.** The reciprocal instrument exists and has never been read | **no class. This is the hole** |
| **Q3 mutation** | it would add to his own recent-search history, on his own data | DERIVED from the documented sibling: `linkedin_search_jobs` already does exactly this, and `server_info.known_side_effects` says so |

**What cannot be taken back, if the answer is yes and D1 turns out false:** every
search run leaves a permanent mark in the search-appearance record of every
person it listed -- people who are, by D4, strangers, and by D3, chosen by
LinkedIn rather than by him. There is no undo for that anywhere in this design,
and `who_viewed_me` establishes the retention scale on the neighbouring signal:
365 days.

**And the gate's own rule forbids the obvious way out.** Its section 1.1 says
the obvious way to answer Q1-Q3 is to load the page, *"and that is precisely the
act the gate exists to authorise"*. So one people-search load cannot be the
evidence that authorises people search.

---

## 7. THE LOADS. Named, so they can be batched rather than reasoned around

**LOAD A -- `/analytics/search-appearances/`, on his own account. One page.**
Settles Q2: whether a search emits anything to the people listed, whether it
names the searcher or aggregates, and over what window. It is the E2 reciprocal
reading -- the same instrument class that closed the profile question -- and it
costs no third party anything, because the only person in it is him. It needs
one allowlist pattern and it delivers `SEARCH-APPEARANCES-SURFACE`'s own 2 rows
as a by-product. **This is the load that would let him rule on evidence.**

Its limit, stated rather than discovered later: it shows what LinkedIn chooses
to show a Premium Career member about people who found him. If it shows names,
a search emits an identifying record and D1 is dead. If it shows only counts, D1
is supported but not proven -- absence on his panel is not proof of absence in
LinkedIn's store.

**LOAD B -- one `/search/results/people/?keywords=...`.** Settles D2 (what the
card contains), the parser cost, and Q1 (whether any badge moves). **It is the
act under consideration, so it cannot precede the ruling** -- unless he
authorises it explicitly as a one-off measurement, which is his to do and not
this document's to assume.

**Order matters: A is available now and B is not.**

---

## 8. THE QUESTION

**Does the emission ruling that closed the profile question also close this
one -- given that for a search results page the same measurement has never been
taken?**

Concretely, one of three:

1. **NO, open it** -- 19 reads become reachable, on the argument that a
   rendered summary of people a ranker returned is not a profile view, accepting
   that D1 is unmeasured when the answer is given.
2. **YES, close it** -- the 19 rows become EXCLUDED-RULED with a written reason,
   which is worth more than a gap: nobody has ever ruled against people search
   in this repository, and silence is what got the `/in/<member>/` pattern
   admitted for months.
3. **MEASURE FIRST** -- authorise LOAD A only, on his own analytics page, and
   rule after. Costs one page load and one allowlist pattern, delivers 2 census
   rows either way, and lands the ruling on a reading instead of on D1's
   silence.

Neither `N 4` (invite a stranger from a search result) nor `N 96` (clear search
history) is inside any of the three. The first is a separate ruling; the second
is already forbidden.
