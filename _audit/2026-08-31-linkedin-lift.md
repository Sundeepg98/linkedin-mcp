# Lifting the six: the instruments the rulings asked for, and what they measured

Date 2026-08-31. Repo `linkedin`, branch `master`. Baseline `4f45781`, suite
2132.

The lead ruled on five of the six remaining refusals and asked for an
instrument behind each. This document reports, per capability, THE INSTRUMENT
BUILT, THE MEASUREMENT IT PRODUCED, and whether the refusal LIFTED -- and
where it did not, the exact remaining blocker.

**No `confirm_token` was issued to anything, by anyone, at any point. No write
was performed. No third party's profile was loaded. No badge was spent.**

---

## 0. The state the process was in, checked before anything was read

The previous wave spent most of a day unable to take captures because the
loaded process was nine commits behind the tree. This one was not:

    linkedin_server_info()
      build.code.commit  4f4578188317      <- the tree's own HEAD
      dirty              false
      pid 7248, started 2026-08-31T07:53:46Z, uptime 304s

So every capture below was taken against the code on disk, and the commit was
verified BEFORE anything was interpreted.

---

## 1. #1 publish_post -- THE DETECTION WAS ENGINEERED, AND IT SAYS DO NOT OPEN

**The ruling.** Build a CONTENT-DRAFT READER FIRST. With one, opening the
composer stops being an unmeasurable risk: read drafts, open, capture, read
drafts again, report the difference. **If no content-draft surface is
reachable, do NOT open the composer** -- come back and say so, and #1 stays
refusing with that as its reason.

**No content-draft surface is reachable. The composer was not opened.**

That conclusion rests on two independent measurements, and the second is the
one that carries it, because it does not depend on the first being complete.

### 1a. Enumeration -- zero draft-shaped addresses on either readable surface

`linkedin_surface_census` returns `href_shapes`, a counted map of every href
on the controls it reads. Both surfaces this server may read were censused
today:

| surface | controls read | distinct href shapes |
|---|---|---|
| `/feed/` | 297 | 25 |
| `/in/me/` | 232 | 28 |

**Not one of the 53 is a content-draft surface.** The four that come closest,
and why each is not one:

    /article/new/                       the article COMPOSER. Not a draft list.
    /preload/sharebox/                  the post COMPOSER. Not a draft list.
    /my-items/saved-posts/              posts HE SAVED -- other people's items.
    /analytics/creator/content/         analytics over PUBLISHED posts.

**THE LIMIT OF THIS ENUMERATION, STATED RATHER THAN GLOSSED.** 39 hrefs on the
feed and 51 on the profile shape to `<opaque>` -- they failed the census's
length or character gate, which is what LinkedIn's tracking-parameter urls do.
A draft surface could be among them and this enumeration could not see it. On
its own, therefore, section 1a is NOT sufficient, and it is not what the
verdict rests on.

### 1b. The boundary -- 17 candidate addresses, 17 refused

Run against `readonly.is_read_url` and `readonly.assert_read_url` directly, so
the answer is the boundary's own rather than a reading of it:

    REFUSE  /post/new/                        forbidden substring '/post/'
    REFUSE  /post/edit/<id>/                  forbidden substring '/post/'
    REFUSE  /article/edit/<id>/               forbidden substring '/edit/'
    REFUSE  /feed/update/<urn>/               forbidden substring '/feed/update'
    REFUSE  /article/new/                     not on the allowlist
    REFUSE  /my-items/                        not on the allowlist
    REFUSE  /my-items/drafts/                 not on the allowlist
    REFUSE  /my-items/saved-posts/            not on the allowlist
    REFUSE  /my-items/posts/                  not on the allowlist
    REFUSE  /in/me/recent-activity/all/       not on the allowlist
    REFUSE  /in/me/recent-activity/shares/    not on the allowlist
    REFUSE  /preload/sharebox/                not on the allowlist
    REFUSE  /pulse/drafts/                    not on the allowlist
    REFUSE  /drafts/                          not on the allowlist
    REFUSE  /content/drafts/                  not on the allowlist
    REFUSE  /analytics/creator/content/       not on the allowlist
    REFUSE  /dashboard/                       not on the allowlist

**This is what makes 1a's incompleteness irrelevant.** Even a draft surface the
enumeration failed to see could not be OPENED: four of these families are
refused by a forbidden substring checked before the allowlist, and the
remaining thirteen match no anchored pattern. A content-draft reader cannot be
built without a read-boundary widening, and no such widening was ruled.

### 1c. The verdict

**#1 STAYS REFUSING, and its reason is now measured rather than argued.** The
previous wave's objection was that opening the composer might leave a draft
this server cannot see or clean up. That objection has now been converted from
a worry into a measurement: **there is no reachable surface on which such a
draft could be detected, so the cost of opening the composer would still be
unmeasurable after opening it.** The lead's own stop condition is met exactly,
and the composer was not opened.

**WHAT WOULD LIFT IT** is unchanged in kind and now specific in content: a
ruling admitting ONE named draft-listing address to the read allowlist, so
that the before/after difference the ruling described can actually be taken.
Nothing on the two readable surfaces names such an address, so the ruling
would have to be made on an address found by him rather than by this server.

---

## 2. #9 send_message -- THE MARGINAL-COST ARGUMENT CHECKED, AND ONE THING IT MISSED

**The ruling.** One messaging open is permitted for the capture, on the ground
that `linkedin_new_messages` and `linkedin_open_messaging` already perform
exactly that operation and are already sanctioned -- so the capture spends
nothing the operator has not already accepted. **Verify that before relying on
it. Check the MESSAGING badge specifically before opening, and if it is
non-zero, stop and report.**

### 2a. The badge -- ZERO, measured twice on two surfaces

`dom.read_messaging_badge` reads `a[href*="/messaging/"]`'s `aria-label`
through `shape.census_shape`. That is the same element, the same attribute and
the same shaper the surface census reads, so a census row IS that measurement.
Both of today's censuses carry it:

    /in/me/    shape "Messaging, 0 new notifications"   count 1   aria-label
    /feed/     shape "Messaging, 0 new notifications"   count 1   aria-label

**The messaging badge is ZERO**, on two different surfaces in one session. So
the lead's stop condition -- stop if it is non-zero -- is NOT triggered.

Recorded beside it, because the lead flagged the notification badge as having
moved 1 -> 4 and today it reads differently again:

    Home, 1 new notification            (both surfaces)
    Notifications, 0 new notifications  (both surfaces)
    <redacted>, 0 new notifications     (mynetwork, both surfaces)

The two nav controls disagree -- `Home` says 1, `Notifications` says 0 -- and
this server has no reading that resolves which is the unread count LinkedIn
would consume. **That is a disagreement between two labels on one page, not a
number**, and it is recorded as such rather than reported as "the badge is 1"
or "the badge is 0".

### 2b. The capture was NOT taken, and the reason is a permission denial

`linkedin_send_message` was **refused by the harness permission classifier**,
not by this server. It is recorded rather than worked around, exactly as
`linkedin_send_invitation` was on 2026-08-31: a tool named "send message" is
precisely what a permission layer should stop, and the correct response to a
denial is to stop rather than to find another door to the same act.

The badge reading above was NOT obtained by routing around that denial. It came
from a census of a page loaded for a different purpose -- which is the route
this server's own design already names as the way to measure a surface without
paying for it, and which reaches the identical string by the identical code
path.

### 2c. THE MARGINAL-COST ARGUMENT DOES NOT HOLD, and this is the finding

The lead asked for the argument to be checked rather than taken. Checked, it
fails -- and it fails on the composer, not on the badge.

`linkedin_open_messaging` and `linkedin_new_messages` load `/messaging/`.
LinkedIn is MEASURED TWICE to redirect that address into one conversation of
its own choosing. So those two tools pay: one badge, and one thread opened.

**A composer capture needs something neither of them touches.**
`/messaging/compose` is on `_FORBIDDEN_URL_SUBSTRINGS` -- it is the entry that
SURVIVED when the blanket `/messaging` ban was narrowed on 2026-08-26, and it
was kept for exactly this. The two sanctioned tools reach a THREAD; the send
composer is a different address, and it is forbidden.

So the operation is not the same operation:

| | the two sanctioned tools | a composer capture |
|---|---|---|
| address | `/messaging/` -> a thread | `/messaging/compose` |
| on the allowlist | yes, both spellings | **no** |
| on the forbidden list | no | **yes** |
| what it costs | the badge, one thread opened | the above, plus a surface nobody has ruled on |

**The marginal-cost argument is sound about the BADGE and unsound about the
COMPOSER.** Opening messaging costs nothing new; it also does not reach the
thing #9 needs measured. Reaching that needs a forbidden substring narrowed,
which is a boundary change and is not a marginal cost at all.

### 2d. The verdict

**#9 STAYS REFUSING.** Not on the deferral the lead lifted -- that deferral is
correctly lifted, and the badge check it was conditioned on passes at zero.
It stays on a different and firmer ground: **the composer address is on the
forbidden list, and opening messaging does not reach it.** The refusal's reason
changes from "deferred by ruling" to "the surface the capture needs is refused
by the read boundary, and the tool that would take it is refused by the
harness."

**WHAT WOULD LIFT IT:** a ruling narrowing `/messaging/compose`, which is the
single entry that has been kept through every other messaging relaxation. That
is a larger question than the one the lead lifted, and it is named here rather
than assumed.

---
