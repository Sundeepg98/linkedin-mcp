# Rulings, 2026-10-10: the ledger's questions

Lane K's ledger (`_audit/2026-09-28-lane-k-ledger.md`, section 7) asked 17 questions and listed 14
PURPOSE rows. Each question below is answered by the orchestrator under the ruling
OUTWARD-ACTS-NEED-THE-OPERATOR: it decides every call that targets no other person and is not
irreversible. One question is the operator's and is relayed to him, not ruled here. The operator may
override any ruling.

## 1. A capture may press, under the probe rule

RULED: (orchestrator, 2026-10-10) CAPTURE-PRESS-UNDER-PROBE-RULE: a live-lane CAPTURE may press a disclosure control or type into a SEARCH box on a surface the press gate refuses, when nothing is committed.

- **What may be pressed or typed:**
  - a disclosure control: a menu, a folder, a filter panel, or a list;
  - a SEARCH box, never a composer or an editor.
- **Nothing is committed:** no save, send, submit, apply or confirm. Escape closes what was opened.
- **What is recorded:** the before-and-after state, and a skeleton only.
- A shipped TOOL still needs its own per-surface `SENSITIVITY_BASES` entry before it may press. The capture is the evidence that entry is built from.

Rows: J 37, M C14, M C15, M C16, M C17, M M28, M M34, N 86, N 90, N 91, N 92.

## 2. One article-composer capture

RULED: (orchestrator, 2026-10-10) ARTICLE-COMPOSER-CAPTURE: one capture load of /article/new/ is permitted, with nothing typed and nothing published.

The page is closed without publishing. An empty draft it may leave is private to him and deletable. The capture records whether a draft appeared.

Rows: M C44, M C46, M C50, M C78, M C81, P L3.

## 3. No position-pinned judgements

RULED: (orchestrator, 2026-10-10) NO-INDEX-PINNED-JUDGEMENTS: a control is judged by its own accessible name and role, never by its position.

Live session 7 showed LinkedIn moving structure under a recorded position (P B9). The four rows therefore go to capture under ruling 1, which shows what each control opens. Label-based `SENSITIVITY_BASES` entries follow from that.

Rows: N 76, P C8, P B3, P S4.

## 4. Caller composition counts under D6

RULED: (orchestrator, 2026-10-10) CALLER-COMPOSITION-UNDER-D6: a row is discharged under D6-CAPABILITY-OVER-AFFORDANCE when the caller can compose SHIPPED tools to deliver its payload, with no server-side derived navigation.

- The row's cell names the composition: which tools, with which arguments.
- The row's state is the weakest of its parts: PROVEN only when every part is proven, otherwise UNFIRED.

Rows: J 57, J 131, N 197.

## 5. Contact import stays manual

RULED: (orchestrator, 2026-10-10) CONTACT-IMPORT-STAYS-MANUAL: an address-book import or sync is not built; the rows are EXCLUDED-RULED with the reopener "he asks to import or sync his address book".

The import uploads OTHER PEOPLE's contact data, and it completes on Google's consent screen, on another domain.

Rows: N 106, N 108, P N21.

## 6. The scroll on a named profile

Already answered by NAMED-PROFILE-DETAIL-PAGES (lane NP): the profile's own details sub-page is loaded, with no scroll.

Rows: N 65, N 178.

## 7. The sessions surface

RULED: (orchestrator, 2026-10-10) SESSION-SURFACE: reading the active-sessions list (P N9) is GAP, admissible only as ONE named settings page after a capture proves the address is the current settings page and that loading it changes nothing. Signing out of sessions (P N10) is EXCLUDED-RULED with the reopener "he names it".

P N9 is never read through the legacy `/psettings/` path. P N10 is excluded because it would end this server's own session (`CREDENTIAL-SETTINGS-NEED-THE-OPERATOR`).

## 8. Sign-in challenges are his

RULED: (orchestrator, 2026-10-10) SIGN-IN-CHALLENGES-ARE-HIS: this server never answers a sign-in or account-recovery challenge; P N13 and P N14 are EXCLUDED-RULED, reopener "never by this server -- he completes them himself".

Password and 2FA entry are the operator's own gate. Detecting a checkpoint is already the auth-wall check.

## 9. Opening the apply flow is the application

RULED: (orchestrator, 2026-10-10) APPLY-FLOW-IS-THE-APPLICATION: opening the Easy Apply flow is the first step of an application, so the read stays refused; J 82 is a PRECONDITION row (observable only when the daily limit is reached).

## 10. A post's text, and an organisation's prose, at runtime

RULED: (orchestrator, 2026-10-10, applying the operator's NAMES-AT-RUNTIME) THIRD-PARTY-TEXT-AT-RUNTIME: a post's own text (M C43) and an organisation Page's prose (J 110) are returned at runtime under PEOPLE-DATA-MITIGATIONS.

NAMES-AT-RUNTIME reaches "items of other people's content", which a read RETURNS as its result. The mitigations:
- the text is returned as untrusted third-party text;
- it is sanitised;
- its length is bounded;
- it is never stored.

FEED-CONTENT-READ-RULING's counts-only rule still governs what is STORED.

## 11. One filter, matched by its fixed label

RULED: (orchestrator, 2026-10-10) FIXED-UI-LABEL-MATCH: N 82's Actively-hiring filter is matched by its exact LinkedIn UI label, with a control showing a near-miss label is refused.

The label is a fixed product string, not third-party text.

## 12. Location by D6, not by geolocation

RULED: (orchestrator, 2026-10-10) GEOLOCATION-BY-D6: no browser geolocation permission is granted; J 17 moves under D6 on the shipped location-parameter search (geo ids), by its own bar.

## 13. The away message: relayed to the operator

Q-AWAY-MESSAGE (M M39) is the OPERATOR's question, because its cell names him as the reopener. It is relayed to him and not ruled here.

## 14. A control no route can aim

RULED: (orchestrator, 2026-10-10) P-A9-CANNOT-DELIVER: P A9 is COVERED-CANNOT-DELIVER on the P A2/P A4 precedent, with the reopener "LinkedIn draws a distinguishing name".

Its two switches carry the same label. This was measured in session 7's editor skeleton, 2026-10-10.

## 15. A broadcast edit, built behind the grant

RULED: (orchestrator, 2026-10-10) P-D29-BUILT-BEHIND-THE-GRANT: P D29 is built behind the grant under EVERY-OUTWARD-CLASS-BUILT-BEHIND-GRANTS and never live-proven unless he names a certificate to add.

## 16. Safety reports stay manual

RULED: (orchestrator, 2026-10-10) SAFETY-REPORTS-STAY-MANUAL: N 152 is EXCLUDED-RULED, with the reopener "an in-product structured report exists, or he names one".

A safety report is an accusation filed through an off-product Help Center form.

## 17. Rows outside the product's purpose

RULED: (orchestrator, 2026-10-10, applying the operator's rule that every feature must serve the product's core purpose) OUTSIDE-THE-PRODUCT-PURPOSE: a row whose capability serves neither his job search nor his professional presence is EXCLUDED-RULED with the reopener "he asks for it".

Rows:
- M C99: daily games;
- M C95: a live video stream, with nothing to read;
- M C98: general news;
- M C96: an image's provenance label;
- J 162, J 164 and N 198: product feedback to LinkedIn;
- P S10, P B7, P J1, P J2, P J3 and P J4: hiring;
- P L6: audio-event hosting.

EXCEPTION: a row whose own cell shows it tunes HIS job recommendations or his search is NOT excluded, because that serves his search. Lane K reads each cell before moving the row.
