# Rulings, 2026-09-24: the search verticals, member rosters, refusals nobody registered, and passive costs

This document records the orchestrator's calls on three open decisions:
D2, D3 and D5 in `_audit/2026-09-21-the-read-triage.md` section 4.
Each ruling has its own section so the register claims it exactly. All four
rulings below are the orchestrator's, made under the operator's delegation of
2026-09-23 18:13 (`OUTWARD-ACTS-NEED-THE-OPERATOR`). None of them acts on
another person, and the operator can override any of them.

These rulings change what is decided, not what is built. The census cells,
`scripts/census_completion.py`'s `RULING_BLOCKED_NAMED`, the address table
and `readonly.py`'s allowlist move when the lanes that build the admissions
land. Until then the census still prints the old reasons, and each lane cites
the ruling here when it moves a row.

## The search verticals

### D2: widen the search admission beyond people

RULED: (orchestrator, 2026-09-24, delegated) D2 IS ANSWERED YES. The search
admission widens from the people vertical to four CLOSED path segments,
`/search/results/(people|companies|groups|events)/`. It is spelled as a
closed enumeration of literal words, never as a `/search/` prefix, and it
carries `D1-SEARCH-AS-READS`'s three conditions to every vertical:
- values come from the tool's arguments, never from page content;
- no test search uses a value that identifies the operator;
- a live session makes at most 5 test searches.

It serves `N 104` (companies), `N 161` and `M C70` (groups) and `N 179`
(events). Each then needs a reader.

Basis:
- All three addresses were refused by the allowlist's silence alone, with
  zero forbidden substrings (measured through the shipped gate on
  2026-09-21).
- `_audit/2026-09-19-search-admission-preconditions.md` measured this exact
  spelling (S2). `SEARCH-CONDITION-2-CLOSED` is what keeps the
  account-ending traversal refused, and a closed alternation of literal
  words satisfies it.
- The one reason that document preferred dropping `companies` (S2b) was that
  no row needed it. `N 104` needs it.

## A refusal written only into the allowlist

### D3: is a reasoned allowlist refusal a ruling?

RULED: (orchestrator, 2026-09-24, delegated) D3 IS ANSWERED NO. A refusal
written only into an allowlist comment is not a ruling. It does not make a row
EXCLUDED-RULED or COVERED-CANNOT-DELIVER. It is a question with its argument
recorded. A row resting on one is GAP, blocked on the decision the refusal
asks for, until that decision is registered here.

Basis: this register is the record of what was decided. Each entry is a claim
with an anchor that has to resolve. A refusal that exists only as a comment
beside an allowlist entry is exactly the invariant nobody ruled: true,
load-bearing, never decided, and invisible to every instrument that reads
rulings.

It governs the three rows `census_completion.py` names under D3 (`N 99`,
`N 177`, `N 178`), and every future row that rests on a comment instead of a
registered ruling. The roster decision those rows wait on is made in the next
section.

`N 178` has a second question, and this ruling does not answer it. Its read
may need another member's profile to load, and that load shows the member
that the operator looked. If it does, it is an act toward that person, and
`OUTWARD-ACTS-NEED-THE-OPERATOR` governs its live proof: he names the member.

## Member rosters

### Rosters he can open himself

RULED: (orchestrator, 2026-09-24, delegated) MEMBER ROSTERS ARE ADMITTED AS
BOUNDED READS. This decides the question a 2026-09-05 refusal recorded but
never registered. That refusal put a group's member list out of scope by name
("a list of people who did not choose to be enumerated by him"). It was
written only in `readonly.py` and in census cells, and was carried from there
to event attendee lists and to the People tab of a company or school. Under
D3 it was an argument, not a ruling. This ruling weighs that argument and
comes down the other way. The rows it held are `N 165`, `N 188`, `N 189`,
`J 108`, `N 102`, `N 99` and `N 177`.

A roster the operator can open himself is read under five conditions:
- one page per call, with no automatic pagination;
- the group, event, company or school id comes from the tool's arguments
  only;
- no member's name or id is stored in a tracked file;
- the read stays inside the live-session budget;
- the rows it held become GAP, blocked on an admission and a reader.

Basis:
- The census asks what he can do on LinkedIn directly, and he can open each
  of these lists himself.
- `D1-SEARCH-AS-READS` already lets a facet search list the people at a
  company or school, so the old refusal no longer draws a line anywhere else
  in the package.
- What keeps a roster read at the scale of one person browsing is carried by
  the code: one page, a caller-supplied id, and the budget. It is not carried
  by refusing the address.

REOPENER: a live read that shows LinkedIn restricting, warning or
rate-limiting the account after a roster load. That reading would reinstate
the refusal for that roster family, and any live lane can observe it.

## Passive costs

### D5: is a passive cost a capability row?

RULED: (orchestrator, 2026-09-24, delegated) D5 IS ANSWERED: A PASSIVE COST IS
NOT A CAPABILITY ROW. A consequence of an act that has no control of its own
is recorded on the row of the act that incurs it. Its own row is
EXCLUDED-RULED as NOT-AN-ACT. It governs `N 171`: exposing his profile to
every member of a group he joins is a cost of joining, not something he does.

It does NOT govern `N 183`. A preference he sets about who may send him event
invitations is an act: it is a setting. That row stays GAP, as a write row
that is admitted by name like any other setting.

REOPENER: LinkedIn draws a control that turns the consequence on or off. The
row then returns as that control's write, and any lane that captures the
group settings can observe it.
