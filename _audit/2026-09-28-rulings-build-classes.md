# Rulings, 2026-09-28: the classes the census still leaves undecided

## Why these are the orchestrator's

The census left 253 write rows on disposition `classify-only`. Most carry the
ground "not a first-round verb" or "undecided", and that ground predates two
standing decisions:
- the operator's ruling (b) of 2026-09-23 18:15 (`WRITE-CLASS-B`), which
  allows the server to connect, message, apply, post and open messaging;
- his principle of 2026-09-24 08:11 (`NAMES-AT-RUNTIME`): do not ask whether
  to deliver a capability; follow the best practice and mitigate the risk.

`OUTWARD-ACTS-NEED-THE-OPERATOR` already puts every call that does not target
another person and is not irreversible with the orchestrator. That includes
allowlist and press-gate defaults. What still waits on him is the target of an
outward act (`OPERATOR-NAMES-THE-TARGET`). Building an act is not firing it.

So the calls below are made by the orchestrator, on the written evidence, as
applications of those decisions. The operator can override any of them. None
of them fires anything at anyone.

## 1. Every outward class is built behind the grant

RULED: (orchestrator, 2026-09-28, applying WRITE-CLASS-B and the operator's 08:11 principle) EVERY-OUTWARD-CLASS-BUILT-BEHIND-GRANTS: every act toward other people is BUILT behind the single-use grant, off by default, and fired only at a target he names.

This extends `OUTWARD-CLASSES-BUILT-BEHIND-GRANTS`, which named three classes
(repost or share, endorse or recommend, delete or withdraw his own item), to
every act toward other people. That includes:
- publishing his own content: posts, articles, newsletters, polls, comments,
  events he creates, and the parameters and modes of each;
- invitations that are not connection requests: to an event, a Page or a
  group, requests for service reviews, requests for a recommendation;
- RSVPs and group membership requests;
- reports to LinkedIn about another member's content, and their undo.

The conditions are those of `OPERATOR-NAMES-THE-TARGET`:
- the preview names the resolved target and the audience;
- a live proof fires only at a person, item or words he names;
- a report is never fired for a proof unless he names a real item to report.

It does not reach:
- `PERMANENTLY_FORBIDDEN` entries whose grounds are measured;
- `ACCOUNT-DESTRUCTION-STAYS-MANUAL`;
- purchases (ruling 4 below).

## 2. His own settings are not outward

RULED: (orchestrator, 2026-09-28, applying OUTWARD-ACTS-NEED-THE-OPERATOR) HIS-OWN-SETTINGS-NOT-OUTWARD: a setting of his own account is not an outward act; it is built behind the grant and live-proven by the SELF-PROFILE-EDITS pattern.

The live proof runs in this order, one setting at a time:
1. read the setting;
2. write a benign value;
3. read it back;
4. restore the exact original value;
5. read it back again.

Any failed restore is STOP-ALL. Settings pages are still admitted one by name
(`ONE-NAMED-SETTINGS-PAGE-AT-A-TIME`, `MESSAGING-SETTINGS-CAPABILITY-LEVEL`).

A setting whose change shows to other people, such as profile visibility, the
photo audience or the public profile, is proven by restoring it inside the
same minute and reading it before and after.

These are BUILT and never live-proven unless he names them:
- the set in `CREDENTIAL-SETTINGS-NEED-THE-OPERATOR`;
- a setting whose change cannot be put back exactly. Changing the custom
  public URL (`P C2`) or unlinking a prior one (`P C6`) can release an address
  another member may take, and it breaks every link to his profile from his
  resume and his applications. The preview must say so.
- a setting that records a sensitive personal attribute: demographics,
  disability or veteran status, or self-identification answers. A test value
  would itself assert that attribute.

## 3. Curating his own feed and items is not outward

RULED: (orchestrator, 2026-09-28, applying OUTWARD-ACTS-NEED-THE-OPERATOR) HIS-OWN-CURATION-NOT-OUTWARD: curating his own feed and his own items is not an outward act; each is built behind the grant and proven with its inverse.

It covers:
- mute and unmute;
- hide, and "not interested";
- follow and unfollow from a feed item;
- save and unsave;
- a post's notification switch;
- the per-post controls on his own items (comments off and on, pin and unpin).

The proof conditions:
- The inverse runs in the same session and is read back.
- Where the inverse itself could notify someone (a re-follow), the target is
  a member he named, or a company or Page he already follows.
- Where LinkedIn draws the undo only once, right after the act, the act is
  proven only through that undo. If the undo is not drawn, it is not proven.

## Not ruled here: uploads

Uploads are the OPERATOR's decision, made 2026-09-04 and landed in `615a5c4`.
`_audit/2026-09-20-the-decides.md` section 1 records it: "the blocker retires,
the rows do not". The scope is restated in `linkedin_server/uploads.py`:
profile photo, post media and message attachments.

`FILE-UPLOAD-UNSANCTIONED` is therefore a stale label. What those rows lack is
an AIM (`_audit/2026-09-05-upload-sanction.md`): a performable upload verb and
a capture of each surface's file input. Nothing here re-decides his ruling,
and nothing narrows it.

## 4. Purchases stay manual

RULED: (orchestrator, 2026-09-28, applying COST-AWARE STAKES-GATING) PURCHASES-STAY-MANUAL: a purchase (Premium, InMail credits, ads, boosts, any paid upgrade) is not built; its row is EXCLUDED-RULED with the reopener "he names a purchase to automate".

## 5. Reading past a substring written to stop an act

RULED: (orchestrator, 2026-09-28, applying OUTWARD-ACTS-NEED-THE-OPERATOR and D3-UNREGISTERED-REFUSAL-IS-NOT-A-RULING) READ-PAST-AN-ACT-SUBSTRING: a forbidden substring whose recorded ground is an ACT does not bar the READ of a page of his own account that carries it.

Some forbidden substrings were written to stop the server doing something:
"invitation", "/invite", "/follow", "/unfollow", "/jobs/application" and
"job-application" stop it sending, following or applying. None of them was
written to stop it reading the page where he manages those things.

Such a page is admitted by ONE exact, anchored pattern, under these
conditions:
- A control is shown failing: the substring still refuses every other
  spelling and every sibling path.
- The press gate still refuses every control on the page unless a press is
  separately permitted.
- A page that lists other people is read under the ruling `NAMES-AT-RUNTIME` and
  `PEOPLE-DATA-MITIGATIONS`.
- A badge the load may clear is a passive cost (`D5-PASSIVE-COST-IS-NOT-A-ROW`),
  recorded on the row.

A page refused by allowlist SILENCE alone, with no substring, is admitted the
same way when a row needs it and no ruling holds it.

It does NOT reach a substring whose ground is the read itself:
- a GET that changes state;
- a credential, recovery, session or security surface;
- a sign-in challenge.

Rows resting on one of those are named to the orchestrator with the ground
quoted. It also does not reach a refusal whose ground is a ruling of the
operator's; those rows are named to the orchestrator with the ruling quoted.

---

EDITED ONCE, 2026-10-10, ON ITS AUTHOR'S AUTHORISATION. The orchestrator, who
wrote this document, authorised one edit at 14:56 IST that day, made by lane
G2: in the read-admission conditions, the ruling id the people-page condition
names is now introduced as "the ruling", because it is a ruling id and not a
code name, and the asserted-names check had read it as a blocker. The meaning
does not change, and no other line of the ruling text was touched.
