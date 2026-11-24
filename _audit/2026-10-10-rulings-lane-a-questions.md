# Rulings, 2026-10-10: lane A's admission questions

These answer the questions in lane A's record (`_audit/2026-09-28-lane-a-admissions.md`, section 5).
They are the orchestrator's, under `OUTWARD-ACTS-NEED-THE-OPERATOR`, and the operator may override any of them.

## 1. Received invitations stay admitted

RULED: (orchestrator, 2026-10-10) RECEIVED-INVITATIONS-READ-STAYS-ADMITTED: the received-invitations tab (N 13, N 14, N 19) stays admitted; any change a read makes to an invitation's seen state is a passive cost under D5-PASSIVE-COST-IS-NOT-A-ROW, recorded on the rows as UNMEASURED, with the reopener "a capture shows the SENDER can see it".

No surface measured so far shows a sender that an invitation was viewed.

## 2. One named settings page per commit is within the ruling

RULED: (orchestrator, 2026-10-10) NAMED-SETTINGS-PAGES-RATIFIED: each settings page lane A admitted by its exact address in its own commit (N 39, P P15, /jobs/application-settings/) is within ONE-NAMED-SETTINGS-PAGE-AT-A-TIME.

ONE-NAMED-SETTINGS-PAGE-AT-A-TIME asks for "a second ruling" before a second page. That ruling is this one, together with HIS-OWN-SETTINGS-NOT-OUTWARD. Each page is named exactly; no pattern widens.

## 3. Credential-adjacent pages stay refused

RULED: (orchestrator, 2026-10-10) CREDENTIAL-ADJACENT-STAYS-REFUSED: stored applicant accounts for other sites (P M9, J 77) are treated as credential-adjacent and stay refused, with the reopener "a capture shows the page holds no credential or account secret".

This rests on inference, not on measurement, and it is ruled that way deliberately, to be conservative.

## 4. A page whose address names a person is read only through a redacted log

RULED: (orchestrator, 2026-10-10) NAMED-ADDRESS-NEEDS-LOG-REDACTION: a page whose ADDRESS carries a person's or a publication's name (M C101's newsletter page) is admitted only after every log line that records a page load records that route's address as a SHAPE, never the slug.

PEOPLE-DATA-MITIGATIONS says names are "never stored". The redaction is built and shown failing first, and the page is admitted after it. Until then the row is GAP with that blocker.

## 5. Content search, not all-results search

RULED: (orchestrator, 2026-10-10) CONTENT-VERTICAL-NOT-ALL-RESULTS: D2-SEARCH-VERTICALS-WIDENED is NOT widened to the mixed /search/results/all/ page. The hashtag row M C93 is served under D6 by the CONTENT vertical, /search/results/content/?keywords=<hashtag>, admitted under D1's three conditions; post text comes back under THIRD-PARTY-TEXT-AT-RUNTIME.

The content vertical is admitted by its own exact pattern, with a control showing the /all/ page stays refused. M C70 shares the same admission.

## Answers that need no new ruling

- **Q4:** J 153 and J 159 stay as lane A left them: refused on its stated inference, with the row's reason written in its cell. M C95, M C98 and M C99 were already excluded by OUTSIDE-THE-PRODUCT-PURPOSE.
- **Q8:**
  - position-pinned judgements are answered by NO-INDEX-PINNED-JUDGEMENTS (no);
  - D6 for J 17 and J 57 is applied (lane K); N 197 is being built by lane B5;
  - M C43 and J 110 fall under THIRD-PARTY-TEXT-AT-RUNTIME;
  - J 131 waits on the C-P5 capture;
  - the press defaults for J 56 and M C96 stay as recommendations until a capture shows their controls.
- **Q9:** N 86 needs a capture of the followerOf facet's value shape before any build.
