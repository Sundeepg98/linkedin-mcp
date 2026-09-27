# Ruling, 2026-09-27: a preview names whom the tool resolved

Lane G's cold verification (`_audit/2026-09-24-lane-g-guards.md`, its notes
for other owners) found that the previews of `send_invitation` and
`send_reply` print a third party's name. It asked whether a preview counts as
a receipt, in the terms of `PEOPLE-DATA-MITIGATIONS`. Two of those mitigations
point in opposite directions:
- mitigation 6 requires the tool to say whom it resolved;
- mitigation 3 says people data is never stored.

This is the orchestrator's call. The operator can override it.

## A preview is the identity check, not a receipt

RULED: (orchestrator, 2026-09-27, applying NAMES-AT-RUNTIME) A PREVIEW NAMES WHOM
THE TOOL RESOLVED, AND A PREVIEW IS NOT A RECEIPT.

A preview is the identity check that every outward act here carries. Before
the grant is spent, it shows the operator the member the tool resolved: the
name and headline read off the page, sanitised, marked as another member's
words, and carried inside a people record. It is returned to the caller at
runtime and never written anywhere.

A receipt is anything that persists. What a write records on disk after it
fires carries only the target the caller supplied, never a name or headline
read off the page.

Basis: the risk an outward act carries is acting on the wrong member. The
mitigation is that he sees whom the tool found before anything fires. A
preview that withholds the name removes that check. A stored name is exactly
the storage that mitigation 3 forbids. Separating the two answers both.
