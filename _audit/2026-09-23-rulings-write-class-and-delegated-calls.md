# Rulings, 2026-09-23: the write class, the live budget, and the calls delegated to the orchestrator

This document records the rulings made on 2026-09-23 in one place, one
section per ruling, so the register claims each exactly. Each ruling names
WHO decided it. The operator's own words are quoted verbatim. Rulings the
orchestrator made under the operator's delegation are marked as such; the
operator can override any of them.

## The operator's rulings

### The live-session budget

RULED: (operator, 2026-09-23 17:43, verbatim "go, 40 loads is fine") A live
session against the attached browser may use up to 40 LinkedIn page loads,
serially, spaced at least 20 seconds apart. It is a ceiling, not a target.
Only one agent drives the browser at a time.

### What needs the operator

RULED: (operator, 2026-09-23 18:13) Only actions that act as the operator
toward other people, or that cannot be undone, need the operator. The
orchestrator decides every other call on evidence and records it here,
where the operator can override it. That covers search keywords, presses
that affect only his own view, his own notification state, and the
allowlist and press-gate defaults. The harness running in bypass-permissions
mode has no bearing on this line.

### The write class (b)

RULED: (operator, 2026-09-23 18:15, verbatim "b") The package may CONNECT,
MESSAGE, APPLY, POST and OPEN MESSAGING on the operator's account. This
lifts the read-only rule, the apply/connect/InMail cut and
DO-NOT-OPEN-MESSAGING. Writes stay behind the single-use grant model:
bound to one action and one target, consumed once, and off by default.

### The operator names each live target

RULED: (operator, 2026-09-23 18:15, same ruling) A live proof of an outward
action is fired ONLY at a target the operator names: whom to connect with or
message, which job to apply to, what to post. Neither the package nor its
agents ever choose a real person or a real job as a test target.

## The orchestrator's calls under that delegation (overridable)

### View-switch presses

RULED: (orchestrator, 2026-09-23, delegated) VIEW-SWITCH PRESSES are
permitted: a press that changes which rows a view shows, such as a sort or
filter control. The view must be RESTORED afterwards, with readings taken
before and after the press to prove it. Basis: the effect is confined to the
operator's own view, and restoration is measured rather than assumed.

### D1: search keywords and facets

RULED: (orchestrator, 2026-09-23, delegated) D1, SEARCH KEYWORDS AND
LinkedIn-WRITTEN FACETS, are permitted as READS, on three conditions:
- Values come from the tool's arguments, never from page content. The
  navigation-derivation guard still applies.
- No test search uses a value that identifies the operator (his name,
  employer, campus or city).
- A live session makes at most 5 test searches, because people searches
  count against the account's monthly limit.

### Notifications: the unread-spend question

RULED: (orchestrator, 2026-09-23, delegated) Loading /notifications/ is
permitted. Its only effect is to clear the operator's own unread badge,
which nobody else sees. This answers the open question that N 20 and N 45
were held on.

### Reading his own inbox

RULED: (orchestrator, 2026-09-23, applying (b)) Reading the operator's own
inbox, including opening message threads, is covered by ruling (b) and
needs no go-ahead per fire. Opening a thread can show its sender "seen", so
the live lane prefers threads whose last message is already read. That
makes a proof send no new read receipt.

### Edits to his own profile fields

RULED: (orchestrator, 2026-09-23, delegated) EDITS TO THE OPERATOR'S OWN
profile fields are not outward acts in the sense of
OPERATOR-NAMES-THE-TARGET. No other person is targeted, the operator allowed
the profile editors on 2026-08-31, and each edit is reversible. A live proof
is permitted on four conditions:
- "notify network" is confirmed off in the edit dialog;
- the field is restored in the same session;
- a before/after reading proves the restoration;
- no field that broadcasts by its nature (for example, adding a new position)
  is touched.

### Other members' ids as search facets

RULED: (orchestrator, 2026-09-23, delegated) OTHER MEMBERS' IDS IN SEARCH
facets (for example `connectionOf`) are permitted as reads when the id comes
from the tool's arguments, never from page content, and is never stored in
a tracked file. This answers the open other-members question that N 172 was
held on.

### D4: the package's own browser context

RULED: (orchestrator, 2026-09-24, delegated) D4 IS ANSWERED NO: the package
does not create its own browser context. It attaches to the operator's
signed-in browser, and that session model stands. `P C8` (saving the profile
as a PDF) gets its download transport through the Chrome DevTools download
behaviour on the ATTACHED browser, which creates no context. Basis: a new
context would change the model the whole server is built on, and it would
lack his session unless the session were copied into it.

### D6: a capability delivered without the named affordance

RULED: (orchestrator, 2026-09-24, delegated) D6 IS ANSWERED YES. A row named
for an affordance (a control or a surface) is discharged when the package
delivers the same capability payload by its own sanctioned routes. The row
names those routes and rests on THEIR proofs: COVERED-PROVEN if they are
live-proven, otherwise COVERED-UNFIRED. The affordance itself is not
reproduced. It governs `N 132` and `J 107`, and every row named for an
affordance this package replaces rather than reproduces.

### A button that only reveals

RULED: (orchestrator, 2026-09-24, delegated) A PLAIN BUTTON THAT ONLY
REVEALS content, such as "Show more analytics", is pressed as a disclosure.
Readings taken before and after the press must show that it revealed content
and changed no state.

### Share and poll proofs

RULED: (orchestrator, 2026-09-24, delegated) SHARE-LINK PROOFS USE THE
OPERATOR'S OWN posts only (`M C72`), so no other author's share figures are
touched. A poll post's address (`M C85`) comes from the tool's arguments only.
A proof uses one of his own posts that carries a poll, or it records
NEEDS-TARGET.

### Credential and session settings

RULED: (orchestrator, 2026-09-24, delegated) CREDENTIAL, RECOVERY AND SESSION
settings are never live-proven unless the operator names them. That covers
the seven credential and recovery controls among the returned settings rows,
and `P N10` (sign out of sessions), which would end this server's own
session. They fall on the cannot-be-undone arm of
OUTWARD-ACTS-NEED-THE-OPERATOR.

### Presses on /in/me/

RULED: (orchestrator, 2026-09-23, delegated) /in/me/ presses get NO blanket
sensitivity-basis bar. Each control is judged on evidence, disclosure versus
action, like any other press. Safety is a property of the code, not of a
permission matrix.
