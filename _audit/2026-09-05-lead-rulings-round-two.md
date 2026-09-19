# Lead rulings, round two

The operator ruled that this server should reach 100% of the enumerated
capability set, having heard the argument against it and reaffirmed. These are
the DECIDE-queue rulings I made on his behalf so that engineering could start
rather than wait. **Every one is written to be argued with, and every one names
what would reopen it.**

## The line I did NOT cross, and will not without him

**No irreversible write is fired at a real target.** Not an application, not a
post, not an invitation, not a message, not a comment. A blanket "build
everything" is permission to BUILD a capability; it is not consent to perform a
specific act against a specific person. Those five actions have no inverse --
and for `apply_job` specifically, nobody has established that LinkedIn offers a
withdraw at all, which is a stronger statement than this server lacking one.

Every write below may be designed, gated, tested against fixtures and left
ready. None may be fired.

## 1. `MENTION-COMPOSITION-RULING` -- BUILD THE MECHANISM, FORBID THE SOURCE

A mention names a real third party inside content he publishes. **A mention is
a name by construction, and this server does not publish names.**

Ruled: the mechanism may be built and gated, and the caller must supply the
target explicitly. **The composed mention may NEVER be assembled from a name
this server READ off a page.** Reading a name in order to mention it is exactly
the disclosure the entire boundary exists to prevent, and it would launder that
disclosure through a feature.

If that makes the capability useless in practice, the right answer is to file it
EXCLUDED-RULED with that reason rather than to relax the source rule.

REOPENS: never on convenience. Only if LinkedIn exposes a mention target as an
opaque identifier the caller already holds, with no name read to obtain it.

## 2. `INVITE-NOTE-PARAM` -- NO

An invitation note is free text sent to a real stranger, attached to an act that
is already irreversible and already gated.

Ruled EXCLUDED-RULED. Two reasons, both about blast radius rather than
mechanism: it **multiplies the consequence of a single mistaken confirm** from
"an unwanted connection request" to "an unwanted message that cannot be
unsent"; and the note has to be composed from something, which reopens the
source problem ruled in 1.

REOPENS: he asks for it explicitly, with a target named, at the time of sending.

## 3. `RECOMMENDATIONS-SURFACE` -- READS YES, STRUCTURALLY NAME-FREE; WRITES GATED, UNFIRED

A recommendation is written BY a named third party ABOUT him. The surface is
other people's words under their names.

Ruled: **reads are permitted and must publish counts and relations, never names
or text.** The pattern is `groups.py`, shipped today, which is name-free
**structurally** -- no name is a parameter of any function in the module,
asserted on `inspect.signature`, and a slug refused *because a slug is a name*.
A rule enforced by a signature cannot be forgotten by the next caller; a rule
enforced by discipline can.

Requesting or giving a recommendation is an outward-facing act naming a real
person: design and gate, fire nothing.

REOPENS: the read half does not need reopening. The write half reopens when he
names a person and asks.

## 4. `SERVICES-PAGE-SURFACE` -- READS YES; TEN WRITES GATED, UNFIRED

It is his own services page, so the read is his own data and there is no third
party in it. Build the reads.

The ten writes change how he presents professionally to everyone who visits.
Reversible in principle, outward-facing in practice. Gated, not fired.

## 5. `FEED-CONTENT-READ-RULING` -- COUNTS AND RELATIONS ONLY

Reading the feed means reading other people's posts. Ruled: counts and relations
only, never text or names, built structurally as in 3.

**The specific trap, measured today:** `census_substitute` returns a person's
name **UNCHANGED** -- it carries no urn, no `/in/` path, no possessive and no
six-digit run, so every marker that predicate looks for is absent. **No
shape-based guard will catch a name.** That is why the remedy has to be
structural rather than a filter.

## 6. `PROFILE-PDF-DOWNLOAD` -- YES IN PRINCIPLE, PENDING ONE MEASUREMENT

It is his own profile as a file: a read of his own data. Permitted if the
surface supports it. The open question is mechanical rather than ethical --
whether the download lands as a file this server can name without opening
anyone else's page.

## 7. `SCROLL` -- STILL NO, and this is a reaffirmation not a new ruling

Ruled earlier today in `_audit/2026-09-05-the-scroll-ruling.md`: not sanctioned,
because correct paging already reaches what it would buy. **The objection is
sufficiency, not safety.** Three named conditions reopen it; none has occurred.

## 8. The standing shape of every write ruling here

Design, WriteSpec, gate, consent text, tests against fixtures and synthetic
targets. **Two calls behind a single-use, action-bound, target-bound token with
a 120s TTL** -- the model the twelve shipped writes already meet.

**Do not invent a bar stricter than that for a new capability.** That mistake
has its own record in this project: safety is a property of the code, not of the
permission matrix, and a per-capability bar higher than the shipped one is
theatre that costs coverage. Equally, do not weaken it.
