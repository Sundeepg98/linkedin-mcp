# Rulings, 2026-09-24 (second batch): the notify condition, a page's veto, a named person's profile, and WHO/WHICH

This batch records four calls the orchestrator made on the night of
2026-09-24 while merging lanes. Each call answers something a lane measured.
Each ruling has its own section so the register claims it exactly. All four
are the orchestrator's calls under the operator's delegation of 2026-09-23
18:13 (`OUTWARD-ACTS-NEED-THE-OPERATOR`), and he can override any of them.

## The notify condition on his own profile edits

### Where the dialog draws no notify control

RULED: (orchestrator, 2026-09-24, delegated) CONDITION 1 OF
SELF-PROFILE-EDITS-NOT-OUTWARD IS AMENDED. That condition required "notify
network" to be confirmed off in the edit dialog. Where the dialog draws a
notify control, that still holds. Where it draws NONE, the condition is met
by reading his account-level setting "Share profile updates with your network"
as OFF before the edit. That read is a read of his own settings page, and
nothing is toggled. If neither the dialog's control nor that setting can be
established, the row records NEEDS-OPERATOR and the edit is not made.

A switch the dialog draws but cannot NAME is not evidence either way. The
condition is not met while one is present, even with the account setting
read OFF, until a capture identifies that switch. Lane L7's save gate refuses
in exactly that case.

The other three conditions stand unchanged.

Basis: session 1 of the live lane measured the intro editor, and it draws no
notify control at all (`_audit/2026-09-23-live-lane-session-1.md`). The
original condition assumed a control that the dialog does not draw. The
account-level setting is what governs whether a profile change is announced,
so reading it answers the question the control was meant to answer.

## A page may veto a navigation, never supply one

### The address comes from the caller

RULED: (orchestrator, 2026-09-24, delegated) A PAGE MAY VETO A NAVIGATION,
NEVER SUPPLY ONE. Every navigation address is composed from the tool's
arguments. Page content may only REFUSE a navigation, for example by showing
that a caller-supplied id is not his own. It never provides the address.

The route lane G found (`linkedin_surface_census`'s `feed_item` surface) opens
a permalink built from an id read off his activity rail. It becomes:
- the caller supplies the id;
- the package verifies that id appears on his own activity rail;
- it refuses the id otherwise, with nothing loaded.

Basis: two standing rules met on that route. One is that navigation
addresses never come from page content, the rule behind the navigation
guard. The other is that the route never aims at somebody else's post. With
the page limited to a veto, both hold at once. A page that can only say no
cannot steer the browser.

## Reaching a person the operator names

### A third party's profile, inside his own outward act

RULED: (orchestrator, 2026-09-24, applying (b)) A THIRD PARTY'S PROFILE
(`/in/<slug>/`) MAY BE LOADED ONLY INSIDE AN OUTWARD ACT whose target the
operator names in that call, under three conditions:
- the slug comes from the tool's arguments only: never from page content,
  and never loaded for a measurement;
- the page's shaper stays name-free;
- the load is part of the act he ordered (connect, message, or the note on
  an invitation), not a read of its own.

Condition 5 of the search admission stands: nothing is fired from a search
results page. The route to a named person is his profile, not a search
result.

Basis:
- `WRITE-CLASS-B` permits connecting and messaging.
- `OPERATOR-NAMES-THE-TARGET` makes him the one who chooses the person.
- `load_a_third_partys_profile_to_measure_a_control` forbids loading a
  profile FOR A MEASUREMENT. Its own text says that whether HE chooses to open
  a profile is his own affair.
- The profile view this load emits is part of the act he ordered toward
  that same person, not a cost laid on a stranger.

It unblocks `N 1` (connect through the profile), `N 4`, `N 5` (the note), and
`M M1` / `M M6` (Message on the profile) as builds. Every live proof still
fires only at a person he names.

## Counts are not delivery when the row asks who or which

### A count-only reader does not deliver WHO or WHICH

RULED: (orchestrator, 2026-09-24, delegated) A ROW WHOSE PAYLOAD IS WHO (a
person or a set of people) OR WHICH (items of other people's content, such as
groups or events) IS NOT DELIVERED by a reader that publishes only counts
under the name-free shaper doctrine. Such a row is GAP. Its blocker is the
doctrine (`_audit/2026-09-05-lead-rulings-round-two.md`), pending the
operator's question on returning names and titles at runtime, and it carries a
REOPENER: he rules that such reads may return them.

A row whose payload is a FILTER, or an AGGREGATE (counts by title, school,
skill or location), IS delivered by a count or aggregate reader, and can be
COVERED once built.

Basis: `N 162` and `N 180` are COVERED-CANNOT-DELIVER for this exact reason:
the surface was read, and the shaper withheld which. A count proves that a
filter applies. It never tells the operator who or which.
