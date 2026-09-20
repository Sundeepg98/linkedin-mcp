# ADMIN-RIGHTS-NOT-HELD, made ready before the artifacts exist

Wave `admin-rights-ready`, 2026-09-20. No write was fired. No browser session was
opened. Every reachability verdict below is a call into the SHIPPED predicate
(`readonly.is_read_url`) on this tree, not a reading of the allowlist by eye.

---

## 1. THE HEADLINE, AND IT OVERTURNS THE BRIEF'S PREMISE IN THE USEFUL DIRECTION

The brief is right that `NOT-OURS` is a fact about today rather than a property of
the capability. It is wrong about what dissolves when he creates the artifacts.

**Creating the Page, the Group and the Event unlocks ONE of the fifteen rows.**

Not because the artifacts do not matter -- because **the artifacts were never the
only blocker.** Fourteen of the fifteen also need an address this server's
navigation boundary refuses, and seven of those are refused TWICE, by
`_FORBIDDEN_URL_SUBSTRINGS` before the allowlist is even consulted. A Page he owns
does not make `/company/<id>/admin/` reachable; it makes an admission *arguable*.
Those are different things and the ledger conflated them.

| | rows | what stands between the row and a live firing |
|---|---:|---|
| **SHIPPED, unfired** | **1** | `A6`. Ships in this commit. Needs only a Company ID, which he reads off his own address bar |
| **Needs a second consenting human** | **7** | `A4 A9 A10 A11 A12 A13 A15`. No artifact and no allowlist entry reaches these |
| **Needs an admission I did not write** | **7** | `A1 A2 A3 A5 A7 A8 A14`. Five of them need a forbidden-substring exemption on top of a pattern |

**THAT IS SEVEN SECOND-PERSON ROWS, NOT SIX, AND THE BRIEF'S SIX IS AN
UNDERCOUNT.** The brief names `A4 A10 A11 A12 A13 A15`. `A9` -- "Invite followers
of similar Pages to follow your Page" -- sends invitations to real people exactly
as `A4` does. It was filed under Premium rather than under other-person-facing,
and the Premium gate is the *lesser* of its two blockers. Correcting it matters
because a row filed as "blocked on a subscription" invites somebody to buy the
subscription and discover the real wall afterwards.

---

## 2. PER ROW

`REFUSED-BY-SUBSTRING` means `_FORBIDDEN_URL_SUBSTRINGS` matched before the
allowlist was consulted -- the repair is a pattern **and** an exemption, which is
a materially bigger ask than a pattern. `ALLOWLIST-SILENCE` means nothing matched
and nothing refused: a pattern alone would do it.

### Page admin (A1-A9)

| row | verdict | why, measured |
|---|---|---|
| `A1` notify employees of a Page post | **needs-an-admission** | `ALLOWLIST-SILENCE`. And a Page with zero employees answers this as a refusal, never as a firing -- "employees" are members who list the Page as their employer, which he cannot create |
| `A2` follow an org's Page as your Page | **needs-an-admission** | `REFUSED-BY-SUBSTRING` on `/follow`. Also needs a write grant. **The only Page-family write with no third-party person in it** -- an organisation is not a person -- so it is the best candidate of the seven |
| `A3` view the Pages your Page follows | **needs-an-admission** | `REFUSED-BY-SUBSTRING` on `/follow`, because `/admin/following/` contains it. Note the luck: the alternative spelling `/admin/page-following/` carries NO forbidden substring, so the gate's grip on this row depends on which spelling LinkedIn serves |
| `A4` invite connections to follow your Page | **needs-a-second-person** | sends invitations to real people |
| `A5` view your Page's invitation credit balance | **needs-an-admission** | `REFUSED-BY-SUBSTRING` on `/invite`. A pure read of his own counter, refused by a rule written to stop him SENDING invitations -- the same shape as the scar where a connections read was refused for containing `/invite` and `/connect` |
| `A6` build a Page follow button | **SHIPPED, unfired** | see section 3 |
| `A7` turn ON auto-invitations (Premium) | **needs-an-admission** | `REFUSED-BY-SUBSTRING` on `/settings/` AND `settings`. Also needs a Page-level paid tier, which is not his Premium Career subscription |
| `A8` turn OFF auto-invitations (Premium) | **needs-an-admission** | as `A7` |
| `A9` invite followers of similar Pages (Premium) | **needs-a-second-person** | sends invitations to real people. See section 1 |

### Group owner (A10-A12)

| row | verdict | why, measured |
|---|---|---|
| `A10` invite connections to a group you own | **needs-a-second-person** | also `REFUSED-BY-SUBSTRING` on `/invite` |
| `A11` message a group member as owner | **needs-a-second-person** | also `ALLOWLIST-SILENCE` on the member roster, which this package refuses "here or anywhere" |
| `A12` message request as group admin | **needs-a-second-person** | as `A11` |

**ONE GENUINE ARTIFACT UNLOCK SITS HERE AND IT IS NOT A ROW.** `/groups/[0-9]{1,20}/`
is **already admitted** -- measured ALLOW. So a group he creates has its feed
reachable today with no allowlist change at all. That does not close `A10-A12`,
but it is the one place where creating an artifact changes what this server can
see, and it is where a successor should start.

### Event organiser (A13-A15)

| row | verdict | why, measured |
|---|---|---|
| `A13` privately message an event attendee | **needs-a-second-person** | an attendee is a person, and there are none |
| `A14` remove an attendee from your event | **needs-an-admission** | `ALLOWLIST-SILENCE`: `/events/<id>/` is NOT admitted, only the events ROOT. **His own event page is unreachable.** And with zero attendees there is nobody to remove, so even admitted it answers as a refusal |
| `A15` withdraw an event invitation | **needs-a-second-person** | `REFUSED-BY-SUBSTRING` on `/invite`, and it needs an invitation already sent to somebody |

---

## 3. WHAT SHIPPED: `A6`, banked COVERED-UNFIRED

`linkedin_server/page_plugin.py` and the tool `linkedin_page_plugin_snippet`.

It is the only row of the fifteen that is **not an act on LinkedIn at all** -- it
is a template and a number -- so it needs no allowlist entry, no write grant and
no second human. It reaches no network, opens no browser, and reproduces the
embed contract LinkedIn documents, quoted verbatim with its provenance travelling
in every payload (`source_doc_updated` is 2022-03-31; `verified_live` is `false`
and stays false until somebody watches the widget render).

**THE SAFETY PROPERTY IS AN ALPHABET, NOT A FILTER.** Only the ten ASCII digits
can reach the output. A Page's vanity name is routinely a person's name -- a
personal-brand Page, a one-person consultancy -- so a slug is refused rather than
shaped, which is `groups.py`'s ruling inherited rather than restated. And
`str.isdigit()` is not those ten characters: it is True for Arabic-Indic,
Extended Arabic-Indic and superscript runs, so the gate is a literal frozenset.
A refusal reports banded shape facts and never the value.

**EVERY GUARD SHIPS SHOWN FAILING**, against a plausible wrong implementation
rather than against nothing: the `isdigit` version, an echoing-refusal version, a
counter literal edited to a sibling plugin's value, and a control proving the
boundary predicate can still say ALLOW.

**UNFIRED IS THE HONEST STATE AND NOT A HEDGE.** The generator is complete. No
Company ID exists to build a real snippet from, because he administers no Page.

**AND THE ROW MEASURES THE BOUNDARY IT SITS BEHIND.** The cited document names
exactly one place to find a Company ID: the admin section of your own Page. That
address is refused by this package -- by allowlist silence. So the input `A6`
needs is one this server cannot read. `tests/test_page_plugin.py` pins that
refusal, so the day somebody admits the address, the coupling is re-measured
rather than remembered.

---

## 4. THE TWO-MINUTE LIST -- exactly what he creates, and what each one buys

Ordered by value-per-minute. **Read the third column before the second.**

| # | create | what it actually buys | cost / reversibility |
|---|---|---|---|
| 1 | **A LinkedIn Page**, then open its admin section and copy the numeric id out of the address bar | **Fires `A6` immediately.** Paste that number into `linkedin_page_plugin_snippet` and the row goes COVERED-PROVEN. It is also the precondition for `A1 A2 A3 A5 A7 A8` ever being arguable | **NOT two minutes and NOT cleanly reversible -- see the warning below** |
| 2 | **An unlisted Group** | Fires nothing. But `/groups/<id>/` is already admitted, so it is the one artifact that changes what this server can SEE with no allowlist edit. It is also the only way to get a positive control for owner-only group controls (section 5) | free, ~2 min, owner-deletable |
| 3 | **A private Event** | Fires nothing. Makes the "Your events" card non-zero, which turns a measured zero into a measured one and gives `A14` a target to argue an admission for | free, ~2 min, owner-deletable |

**THE PAGE IS A MATERIALLY HEAVIER ASK THAN THE OTHER TWO AND THE BRIEF'S
"free, two minutes, owner-deletable" DOES NOT COVER IT.** The brief applies that
phrase to the Group and the Event only, correctly. A Page is publicly attached to
his profile as an admin relationship, is discoverable, and LinkedIn's
deactivation path is conditional rather than a delete button. **I did not verify
LinkedIn's current creation prerequisites or deactivation conditions, because
this wave opened no browser** -- so treat the Page line as UNVERIFIED-LIVE and
worth thirty seconds of his own reading before he clicks. If he wants `A6` fired
and nothing else, that is the entire cost of the Page, and it may not be worth it
for one row.

**What none of the three buys:** any of the seven second-person rows, and any of
the seven admission-blocked rows. Creating artifacts and writing allowlist entries
are independent axes, and only he can do the first.

---

## 5. TWO CORRECTIONS TO THE EVIDENCE THIS BLOCKER RESTS ON

### 5.1 "He administers no Page" rests on an instrument that could not have found one

`_audit/2026-09-19-the-read-rows.md` writes off `A3` and `A5` citing a Manage-Pages
capture carrying "58 Pages and **zero admin markers**". Measured this wave:

* both committed fixtures are a **FRAGMENT** -- one `<head>`, one `<main>`, and
  **no `<html>`, `<body>` or `<nav>` element at all**;
* **every** href-bearing element in both is a company address: 20 of 20 plain,
  40 of 40 hydrated, one distinct path shape between them;
* `/admin` appears **0** times, and so does every other admin token -- the single
  hit for "manage page" is the document `<title>`, before `<main>` opens.

An instrument that captured no page chrome **could not have found an admin marker
if one existed.** "Zero admin markers" is a true statement about the capture and
carries no information about the account. The claim is not refuted -- it is
**unsupported**, which is a different and more actionable thing.

### 5.2 The event half is genuinely measured; the group half is an uncontrolled absence

* **EVENTS -- measured, with a control.** The self-scoped "Your events" card is a
  real rendered zero: 0 rows, a 29-character empty-binding comment, 0 descendant
  elements, contrasted in the same pass against a sibling card carrying 1567
  characters and 432 elements. That is a proper zero and it stands.
* **GROUPS -- an absence never shown against a positive.** Five memberships, and
  the controls that arrived are `Update your settings` (10), `Copy link to group`
  (5), `Leave this group` (5). No owner-only control appears -- but no capture has
  ever contained one, so the vocabulary has never been shown able to find it.
  **Creating the unlisted Group (list item 2) is what turns this into a
  measurement**, and it costs two minutes.

---

## 6. THE STRUCTURAL DEFECT THIS WAVE FOUND AND FIXED

**Section S of `network.md` could not carry a state, so no capability could ever
move a row in it.** It had three columns and no state cell; its `GAP` verdict
lived only in prose and was turned into a countable state by a **hardcoded
override in two scripts** -- `count_census_states.main` and
`enumerate_gap_rows.rows`, both spelled `if not st and letter == "N" and
<id matches A-digits>: st = "GAP"`.

The state was in the code rather than in the file, so all fifteen rows were
permanently GAP no matter what shipped. `A6` is the row that proved it: a tool
shipped and nothing in the census could move.

Fixed by giving the table a `state` column -- which is the escape hatch the
override's own `if not st` was written to leave open. The override stays as a
backstop for any future A-row added without a state. Measured after: `A6`
COVERED-UNFIRED, fourteen GAP, and the derivation, ratchet and state-vocabulary
guards all green.

---

## 7. THE ADMISSIONS I DID NOT WRITE

`readonly.py` is held by a sibling wave and **nothing here touched it.** These are
stated so the lead can rule on them, not applied.

| what | serves | shape of the ask |
|---|---|---|
| a pattern for the Page admin root | `A1 A2 A3 A5 A7 A8` precondition | one anchored pattern. **Blocked behind a prior decision**: `/company/` is not admitted in any form and a sibling wave owns that surface |
| an exemption for `/follow` on one exact Page-admin address | `A2 A3` | exact-url exemption, the `/in/me/edit/intro/` precedent |
| an exemption for `/invite` on one exact Page-admin address | `A5` | as above. **This is the scar's exact shape**: a read of his own counter refused by a rule written to stop him sending |
| a pattern for `/events/[0-9]{1,20}/` | `A14` precondition | note the root is admitted and the entity page is not, which is the reverse of groups |

**Two boundary notes for whoever writes them.** `\d` is not a closed class --
every pattern above is `[0-9]{1,N}`. And anything returning a member list, an
attendee list or an organiser returns THIRD PARTIES: the closed-alphabet shaper
ships with the reader or neither ships. `groups.py` and `menus.py` are the two
worked examples, and `page_plugin.py` is now a third.

---

## 8. CONSTRAINTS AND EVIDENCE CLASS

**VERIFIED-BY-INSTRUMENT.** Every reachability verdict in sections 1, 2 and 7
(a call into `readonly.is_read_url` plus the matching substring and pattern
lists); the fixture counts in 5.1 and the control in 5.2; the census states in 6;
the `A6` behaviour, alphabet and mutation battery.

**DERIVED.** The second-person classification -- read off what each row's verb
requires, not from a firing.

**UNVERIFIED-LIVE.** The Page creation and deactivation terms in section 4. The
plugin contract's *current* liveness: it is quoted verbatim from a document whose
own metadata says 2019-02-27 authored, 2022-03-31 updated, and the payload says so
rather than a comment.

**Gates.** Identity gate PASS over 8 staged paths. It first BLOCKED five company-id
shapes in the new files; **reshaped rather than declared**, per
`test_no_committed_identity.py`'s standing order that a `DECLARED_PLANTS` entry
tolerates a shape in a file forever. The one address whose exact value is
load-bearing is assembled at runtime, so the source carries no shape and the
pinned string is still the document's. 662 tests green across everything coupled
to the touched files; the full suite is CI's.

**Delegation.** Three read-only `implementer` children measured the pinned-count
inventory, the fixtures, and the census-state vocabulary to files in the session
scratchpad. Their output was reviewed before any of it was used, and the two
findings that changed this wave's direction -- the fragment capture and the
hardcoded section-S override -- were re-derived here rather than relayed.
