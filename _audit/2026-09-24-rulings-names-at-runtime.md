# Rulings, 2026-09-24 (third batch): names at runtime, their mitigations, and the classes built behind the grant

The operator answered the question the WHO/WHICH rows were held on. This
document records his ruling in his own words, then the orchestrator's calls
that apply it. Each ruling has its own section so the register claims it
exactly. The orchestrator's calls are overridable by the operator.

## The operator's ruling

### Names at runtime

RULED: (operator, 2026-09-24 08:11, verbatim) "It's not about returning or not returning. The functionality is to return people's names as the result. During runtime, if you want to be careful, then follow the best procedure and practice to mitigate the risk."

A read whose capability is people, or which items of other people's content
(groups, events), returns them as its result: people's names, and the titles
of groups and events.
- This answers the question `WHO-WHICH-COUNTS-ARE-NOT-DELIVERY` was pending
  on.
- It amends the name-free doctrine of 2026-09-05 for what a read RETURNS at
  runtime: `FEED-CONTENT-READ-RULING`'s "never text or names", and condition 1
  of `SEARCH-ADMISSION-APPROVED-FIVE-CONDITIONS`.
- It does not touch what is STORED. No third party's name is ever written to a
  tracked file, and that is unchanged.

## The orchestrator's calls applying it

### How people data is returned

RULED: (orchestrator, 2026-09-24, applying NAMES-AT-RUNTIME) PEOPLE DATA IS
RETURNED UNDER SIX MITIGATIONS. Each is enforced by code and by a test that is
shown failing without it.

1. DECLARED FIELDS ONLY. A person comes back as a closed record: name,
   headline, profile link or member id, and connection degree. A group or an
   event comes back as its title and its link. No other page text leaves
   through a people reader.
2. SANITISED AND MARKED. Every string is:
   - Unicode-normalised;
   - stripped of control, zero-width and bidirectional characters;
   - whitespace-collapsed and length-capped;
   - marked as untrusted third-party text that the client model treats as
     data, never as instructions.
3. NEVER STORED. No third party's name, headline or link is written to a
   tracked file, a log, an error field, a receipt, a cache or a fixture.
   Fixtures use synthetic people. Live evidence records counts and hashes.
4. BOUNDED. One page per call, no automatic pagination, and inside the live
   budget. No loop, sweep or schedule; `PERMANENTLY_FORBIDDEN` already holds
   that.
5. VISIBLE ONLY. Only what LinkedIn shows him is returned. A member LinkedIn
   shows as "LinkedIn Member" stays that. De-anonymising a viewer stays
   forbidden.
6. NOT A TARGET BY ITSELF. A name read off a page is never used on its own to
   compose outward content or to choose a target; `MENTION-COMPOSITION-RULING`
   stands. An outward act fires at the exact member the operator names, by
   link or id, and the tool reports whom it resolved before it acts.

Basis: this is the standard practice for a personal tool reading what its
user can already see. Return what the task needs and nothing more. Hold it
only for the session. Respect the platform's own visibility. Keep the volume
at the scale of one person browsing. Treat page text as untrusted input.

These are the risks it answers:
- **Leakage into persistent files.** The repository is public, and agents
  write evidence.
- **Prompt injection through a headline.**
- **Acting on the wrong person when two share a name.**
- **Account restriction from scraping-shaped volume.**
- **Exposing members who chose to be anonymous.**

### The outward classes ruling (b) did not name

RULED: (orchestrator, 2026-09-24, applying the operator's 08:11 principle)
THREE CLASSES ARE BUILT BEHIND THE SINGLE-USE GRANT:
- reposting or sharing;
- endorsing or recommending;
- deleting or withdrawing one of HIS OWN items.

Each is off by default, and each fires only at a target the operator names in
that call.

`PERMANENTLY_FORBIDDEN` keeps only the entries whose grounds are themselves
mitigations:
- any anti-detection technique;
- any loop, sweep or scheduled write;
- auto-accept or auto-reply;
- de-anonymising a viewer;
- loading a third party's profile for a measurement;
- marking notifications read.

Basis: the operator's principle of 08:11 is to deliver the functionality and
mitigate the risk. `OUTWARD-ACTS-NEED-THE-OPERATOR` needs him only for the
target: building an act acts on nobody, and firing it needs his named target.

When the delete path is built, the specs whose `reversible_by` cites
`delete_or_withdraw_anything` are re-read and restated. Endorsing reaches its
control through `THIRD-PARTY-PROFILE-FOR-A-NAMED-TARGET`.
