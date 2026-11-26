# Orchestrator rulings of 2026-11-26 (01:20 IST): the job search's route, registered at integration 3

**Every ruling below is the orchestrator's.** It recorded them in its own merge
notes, which are kept outside this repository's tracked files, in the entry
headed "2026-11-26 01:20 IST". That entry reports that session 11's live part
is done and records a research finding: LinkedIn is retiring its classic job
search ("starting in September", with no end date given), and the classic
reader keys zero cards on the AI search page, so a redirect would return an
empty shortlist silently rather than an error. The entry counts 21 proven jobs
rows, plus `J 31`, that depend on the classic page.

Integration 3 (`_audit/2026-11-26-integration-3.md`) registers the entry's
three rulings here, in the register's format: a canonical id on a `RULED:`
line, the orchestrator's own words quoted, and the reopener. Where the words
name no reopener, this page says "none stated". The rulings of 2026-11-25 are
registered in `_audit/2026-11-25-rulings-end-of-wave.md`. This page is
separate because a ruling takes its date from its document's name, and these
three were made on 2026-11-26. The integrator adds no ruling of its own.

None of the three moves a census row today. The first two govern code that a
search lane is building and the budget of each live session. The third is
conditional: it moves rows only when a capture shows that the classic search
no longer serves, and no such capture has been taken. The entry queues that
check (`C-SRCH-1`, one load) for the next live session.

## 1. The route

RULED: (orchestrator, 2026-11-26) SEARCH-ROUTE-CLASSIC-PRIMARY --
"Q-SEARCH-ROUTE-POLICY: classic PRIMARY while it serves; the AI route is the
FALLBACK and REFUSES every filter not measured on it." REOPENER: none stated.
While the classic search serves, it is the route. A fallback that cannot honour
a filter refuses, rather than returning a broader result than the caller asked
for.

## 2. The search budget

RULED: (orchestrator, 2026-11-26) FILTER-REQUERY-COUNTS-AS-A-SEARCH --
"Q-FILTER-FIRES-SEARCH-CAP: a filter-driven re-query counts as a search against
the 5-per-session cap." REOPENER: none stated. The cap is `D1-SEARCH-AS-READS`'s
"at most 5 test searches per session". A re-query that a filter press triggers
spends from that cap, the same as a new search.

## 3. The rows proven on the classic route

RULED: (orchestrator, 2026-11-26) RETIRED-ROUTE-ROWS-RETURN-ON-CAPTURE --
"Q-RETIRED-ROUTE-ROWS: rows proven on classic stay COVERED-PROVEN while classic
serves; when a capture shows classic no longer serves, each returns to GAP with
its next step on the AI route and a reopener." REOPENER: none stated. The
reopener the words name is each returning row's own, not the ruling's. The
trigger is a capture showing that the classic search no longer serves. Until
that capture exists, every row proven on the classic page keeps its state.
