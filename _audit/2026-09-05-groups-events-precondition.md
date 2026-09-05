# The groups/events precondition, answered

**CORRECTS:** `_audit/2026-09-03-linkedin-gap-blockers.md` -- GROUPS-SURFACE is not a possible three-row blocker; he belongs to five groups and its 32 rows stand.

That ledger's `GROUPS-SURFACE` entry treats "he belongs to zero groups" as a
live possibility, one that would make 29 of that blocker's 32 rows unreachable
in principle for this account. Measured 2026-09-05: five distinct groups are
listed on his own Groups page, disjoint from the five that page itself calls
suggestions, each carrying a per-row management control the suggestion rows
lack.

Wave: groups-events. Date: 2026-09-05. Every number here was taken by an
instrument carrying a control that fired.

---

## 1. THE QUESTION, AND WHY IT WAS WORTH A PAGE LOAD

`GROUPS-SURFACE` (32 census rows) and `EVENTS-SURFACE` (18) both rest on one
unestablished fact. The ledger states it plainly: if he belongs to zero groups,
29 of the 32 are unreachable in principle for this account and the largest
blocker in the census is a three-row one.

Two waves reached for a cheap answer before this one. Both were right to try
and both were wrong.

## 2. THREE ROUTES WERE MEASURED AND ALL THREE WERE DEAD

**THE ALLOWLIST.** `scripts/_probe_unmeasured_surface_addresses.py`, re-run at
HEAD rather than relayed: 15 Groups/Events addresses, ALLOWED 0, all 7 controls
passing. This is the gate everybody sees and the least interesting of the
three, because it is one line of code.

**THE RENDER, and this is the one nobody had stated.** A tabbed category's rows
are not in the document until its tab is pressed, so every profile-side route
to the answer is blind. Proven by a control rather than argued: the Companies
category holds at least 20 rows -- 20 and 40 distinct company anchors in
`tests/fixtures/manage_pages_following.html` and its hydrated sibling -- and
renders ZERO of them on the Interests capture and ZERO again on a live
396909-character profile read.

**A page where a known-non-empty category reads zero cannot answer the
membership question FOR ANY ANSWER.** The previous wave called that same
reading VOID because its control read zero; that verdict is right about his
memberships and wrong about the route, and the difference is what let this wave
stop looking for a cheaper page.

**THE ADDRESS.** `/in/me/details/interests/` was admitted on 2026-09-04 for
exactly this purpose and REDIRECTS, with two same-run siblings as its control.

**AND NO OFFLINE ROUTE EXISTED.**
`scripts/_probe_membership_signal_in_corpus.py` swept 30 documents and 2522736
characters for six group and event route needles: all ZERO, with a must-fire
control at 90 and a must-stay-silent control at 0.

## 3. A TRAP WORTH NAMING, BECAUSE IT LOOKS LIKE AN ANSWER

The profile's Interests strip draws five tabs and one is labelled `Groups`. That
is **not** evidence he belongs to a group: it would require LinkedIn to omit a
tab for an empty category, and there is no category he is known to have zero of
to test that with. Three of the five are known non-empty, two unknown, none
known empty.

**A reading no instrument can fail is not a reading.**

## 4. THE LIVE READ

Taken twice per surface, with a surface of known count read at the START and
the END of the same session.

    CONTROL  /mypreferences/d/dark-mode   20 read, expected 20   PASS, both ends
    GROUPS   SERVED exact    74 controls, twice AGREE    10 group-marked hrefs
    EVENTS   SERVED exact   104 controls, twice AGREE    54 event-marked hrefs

He is not at zero. But a count of entity links is not a count of memberships:
both roots draw recommendations alongside his own and both are entity links.

## 5. THE CHEAP DISCRIMINATOR FAILED, AND THAT IS RECORDED RATHER THAN DELETED

`read_surface_census` reports a CONTAINER per control, so if his own groups and
LinkedIn's suggestions sat in different containers the split would fall out
with no name ever crossing. **Measured: 10 of 10 and 54 of 54 report
`container: none`, one distinct container each.**

The container does not separate them. Kept here because the next person will
reach for it too, and a negative that saves an hour is worth its lines.

## 6. THE ANSWER, FROM TWO INDEPENDENT SIGNALS THAT AGREE

`scripts/_probe_membership_sections.py`, offline over the capture.

**SIGNAL ONE -- the section, and the identifiers in it:**

| surface | section | links | DISTINCT | overlap |
|---|---|---:|---:|---:|
| groups | `Groups listing` | 5 | **5** | 0 |
| groups | `Groups you might be interested in` | 5 | 5 | -- |
| events | `Recommended for you` | 45 | 15 | 0 |
| events | `Exclusive for <redacted>` | 9 | **3** | -- |

Two disjoint sets of five on groups. One is labelled suggestions by LinkedIn's
own heading; the other shares no identifier with it, so this is not one set
drawn twice.

**SIGNAL TWO -- the per-row control, which is independent of the heading:**

    'Groups listing'                       5  'More'
                                           1  'More options for <redacted>'
                                           ... one per group, names redacted
    'Groups you might be interested in'    NONE

A row he belongs to carries a per-row management control; a suggestion does not
have one until he interacts with it. **Five rows have one and five do not, and
the split falls exactly on the heading boundary.** Measured at two window sizes
(1500 and 3000 characters) with the same result, so it is not an artefact of a
number somebody picked.

## 7. WHAT IS MEASURED AND WHAT IS READ

**MEASURED:** five distinct group identifiers on his own Groups page, disjoint
from five the page itself calls suggestions, each carrying a per-row management
control the suggestion rows lack.

**READ, NOT MEASURED:** that `Groups listing` is LinkedIn's word for "groups
you belong to". That is a reading of LinkedIn's wording. The three structural
facts above all point the same way and none of them is the word "member".

**WHAT WOULD SETTLE IT ABSOLUTELY:** the label text inside one of those
overflow menus, which needs a PRESS. Not taken, and not needed for the
consequence below.

**THE CONSEQUENCE HOLDS EITHER WAY.** `GROUPS-SURFACE` is not a three-row
blocker. Its 32 rows have a live account behind them.

## 8. MEASURED-ABSENT: THERE IS NO "EVENTS YOU ARE REGISTERED FOR" SURFACE

Filed as an ABSENCE with its evidence, the way `N 118` and `P L2` were retired
as MEASURED-ABSENT rather than deleted -- **a row that vanishes is
indistinguishable from a row nobody thought of**, and this ledger has already
dispatched one wave after something that is not there.

The census, the ledger, and the ruling that ratified `/events/` all assumed
such a surface existed and that `/events/` was the route to it. **It does not
exist.** Eighteen distinct events across two sections and not one of them is
his attendance: 15 are recommendations by LinkedIn's own heading, 3 sit under a
curated heading the singleton rule redacted.

Corroborated from the census side before it was measured: the Events family has
no row for "the events you are registered for". Its nearest neighbours are
`N 185` "attend an event you accepted" (a WRITE) and `N 183` "receive event
invitations only from your 1st-degree connections" (a SETTING). The censused
content of the root is `N 180` -- recommendations and what his network is
attending -- and that is what the page draws.

**CORRECTED BY:** `_audit/2026-09-05-events-surface-recosted.md` -- the root does draw a "Your events" region; it is present, structurally complete and EMPTY for this account, which this pass could not see because it assigned anchors to headings and a heading with zero anchors under it produces no output at all

**THE ADDRESS STAYS OPEN.** The ratification condition attached to it was "if
the read returns nothing else, retire it". The read returns nothing SELF-SCOPED
but it does return `N 180`, a censused row, so retiring it would close a door
onto a capability somebody did ask for.

**WHAT `EVENTS-SURFACE` NEEDS INSTEAD OF A BUILD:** re-costing. Rows written on
the assumption of a registered-events surface are rows against a page that does
not draw one.

## 9. PROVENANCE

| instrument | control | outcome |
|---|---|---|
| `_probe_unmeasured_surface_addresses.py` | 7 addresses with stated expectations | all passed |
| `_probe_membership_signal_in_corpus.py` | must-fire `/company/` at 90; must-stay-silent at 0 | both passed |
| `_probe_groups_events_live.py` | dark-mode 20, start and end | passed both ends |
| `_probe_groups_events_capture.py` | dark-mode 20; refuses without CDP attach | passed; refusal shown firing |
| `_probe_membership_sections.py` | parsed total must equal the census total | AGREE, 10 and 54 |

The captures are raw and gitignored -- `.gitignore:140` matches
`*_probe-*.html`, verified with `git check-ignore` before a byte was written.
They are written by the capturing script and NOT read back by it; the section
analysis is a separate pass.

**THE SECTION PROBE'S CONTROL CAUGHT A DEFECT IN THE PROBE ITSELF** on its
first run: an absolute-href pattern found 5 of the 10 group links and ZERO of
the 54 event links, and the control refused both tallies as VOID rather than
printing a plausible half-answer. Both pages write RELATIVE hrefs -- the same
hazard `census_href_identifies_entity` documents at its own site as the reason
it uses containment rather than `startswith`.
