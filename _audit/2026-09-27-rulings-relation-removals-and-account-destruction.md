# Rulings, 2026-09-27: removing a relation, and destroying the account

Lane L8 retired three `PERMANENTLY_FORBIDDEN` entries, applying
`OUTWARD-CLASSES-BUILT-BEHIND-GRANTS` (`_audit/2026-09-24-rulings-names-at-runtime.md`).
It found five rows that fall outside the three classes that ruling builds:
`N 29`, `N 141`, `N A14`, `P N27` and `P P2`
(`_audit/2026-09-24-lane-l8-outward-classes.md`). These are the orchestrator's
calls on them. They apply the operator's 2026-09-24 08:11 principle:
deliver the functionality, and mitigate the risk by best practice. The
operator can override either.

## Removing a relation with a person he names

RULED: (orchestrator, 2026-09-27, applying the operator's 08:11 principle) REMOVING A RELATION
WITH A MEMBER HE NAMES IS BUILT behind the single-use grant, off by default.
The removals are:
- removing a 1st-degree connection (`N 29`);
- blocking a member (`N 141`);
- removing an attendee from an event he organises (`N A14`).

Each fires only at the one member he names in that call, by profile link or
id, never by a name read off a page. It reports whom it resolved before it
acts, and it states its irreversibility in its own `reversible_by`: LinkedIn
documents that blocking removes the connection, endorsements and
recommendations.

Basis: each is a capability he has on LinkedIn directly, and each acts on
one person. `OUTWARD-ACTS-NEED-THE-OPERATOR` needs him for the target, not
for the build. The risk is acting on the wrong member. It is mitigated by
the same controls every outward act here carries: the grant, a target he
names, and a resolved identity shown before the act.

## Destroying the account or its data

RULED: (orchestrator, 2026-09-27, applying the operator's 08:11 principle) ACCOUNT-LEVEL
DESTRUCTION STAYS MANUAL. These are not built, and their rows are
EXCLUDED-RULED:
- merging or closing duplicate accounts (`P N27`);
- closing and deleting his account (`P N28`, already EXCLUDED-RULED on its
  forbidden-tuple entry; this ruling adds the capability-level ground);
- deleting the data LinkedIn holds about him (`P P2`).

REOPENER: he asks for one of them by name, naming the account or the data,
in the call that would make it.

Basis: the act is irreversible and catastrophic for the asset this whole
package protects, his professional identity, and automating it serves no
workflow. The best practice for destructive account operations is to leave
them in the platform's own interface, behind its own confirmations and
waiting periods. Here the mitigation is to keep the act manual, not to gate
it.
