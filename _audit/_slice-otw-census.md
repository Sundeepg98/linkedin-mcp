# Slice: Open-To-Work surface census (read-only)

Question: is `url_template=None` on `linkedin_set_open_to_work` still a correct
description of reality, and exactly what would have to happen to reach the editor?

Method: static analysis of five captures already on disk. Python `re` only, no new
dependencies, no browser, no network, no writes outside this file. Every raw-capture
value below is written as a SHAPE (`<vanity>`, `<member urn>`, `<other member>`);
values quoted verbatim come from the SANITISED, tracked fixtures.

Answer in one line: **CORRECT, and not by omission -- there is no url to find. The
editor is fetched by an SDUI `ServerRequest` RPC, and even the sibling screen-navigate
actions on the same card carry `"url":""`.**

---

## 0. The corpus, measured

| tag | file | bytes | chars | `<script>` blocks | chars inside script | chars outside |
|---|---|---|---|---|---|---|
| FX-pre | `tests/fixtures/profile_topcard.html` | 34,628 | 34,618 | 0 | 0 (0.0%) | 34,618 |
| FX-hyd | `tests/fixtures/profile_topcard_hydrated.html` | 29,730 | 29,720 | 0 | 0 (0.0%) | 29,720 |
| FX-skl | `tests/fixtures/profile_skills.html` | 10,767 | 10,757 | 0 | 0 (0.0%) | 10,757 |
| RAW-pre | `_audit/_probe-profile-me-pre.html` | 1,177,615 | 1,177,077 | 17 | 1,091,238 (92.7%) | 85,839 |
| RAW-hyd | `_audit/_probe-profile-me-hyd.html` | 402,731 | 402,345 | 16 | 3,686 (0.9%) | 398,659 |

All five read in full. The two raw captures are the SAME page at two hydration states
and they are NOT the same document: RAW-pre is 92.7% React-Server-Components flight
payload inside `<script>` and only 85,839 chars of actual DOM; RAW-hyd is 0.9% script
and 398,659 chars of DOM. **Everything below therefore reports DOM and PAYLOAD
separately**, because a string that exists only in the flight payload is not a rendered
control -- and that distinction turns out to be the whole answer.

The fixtures carry NO script blocks at all, so for them DOM == whole file.

---

## 1. Every open-to-work control, per capture

Four distinct controls exist. Not one of them is an anchor with a usable href.

### C1 -- the topcard "Open to" button (the disclosure)

| property | value |
|---|---|
| tag | `button`, `type="button"` |
| accessible name | `aria-label="Open to"`, inner text also `Open to` |
| `componentkey` SHAPE | `<vanity>_openToButton` (fixture value: `alex-rivera-8c21_openToButton`) |
| `aria-expanded` | **ABSENT pre-hydration; `"false"` hydrated** -- in BOTH the fixtures and the raw captures |
| href | none. It is a `button`, not an `a` |

Occurrence count (DOM, per file): FX-pre 2, FX-hyd 2, FX-skl 0, RAW-pre 2, RAW-hyd 2.
The two per page are a responsive duplicate pair -- identical `componentkey` and
`aria-label`, differing only in the class list. A selector on
`button[aria-label="Open to"]` matches 2 nodes, not 1.

RAW-pre carries a THIRD button whose inner text is `Open to`, sitting OUTSIDE and before
`<main id="workspace">` (offset 20088), with `componentkey="e205ae22-...uuid"` and NO
`aria-label`. In RAW-hyd the same node has gained `aria-expanded="false"` (offset 44036).
It is the server-rendered skeleton copy of the action row. Counting it, "Open to"-bearing
buttons per raw capture = 3.

### C2 -- the state card ("Open to work &#183; Recruiters only")

| property | value |
|---|---|
| container | `div` with `componentkey="auto-component-<uuid>"` (FX: `auto-component-9b53a9f4-...`; RAW: `auto-component-8834fa65-...`) |
| payload viewName | `opento_preview_otw` |
| clickable element | an `a` (RAW-pre) / `a tabindex="0"` (RAW-hyd, FX) wrapping the text |
| href, pre-hydration | `https://www.linkedin.com/` -- the bare root, in BOTH FX-pre and RAW-pre |
| href, hydrated | `https://www.linkedin.com/in/<vanity>/?isSelfProfile=true` -- the profile you are already on |
| rendered text | `<strong>Open to work &#183; Recruiters only</strong>`, then `India | On-site &#183; Hybrid`, then `Show details` |
| lives in | `<ul data-testid="carousel-children-container">`, first `<li>` |

The href is decorative. The card's real behaviour is in the flight payload (RAW-pre
chunk `17a`, offset 926141): a `proto.sdui.actions.core.Navigate` ->
`NavigateToScreen` with

```
screenId  : com.linkedin.sdui.flagshipnav.jobs.PrefCollectionDetailView
pageKey   : seeker_preference_collection_detail_view
presentationStyle : PresentationStyle_MODAL   (ModalSize_MEDIUM)
url       : ""            <-- EMPTY STRING
role      : "button"
tracking  : actionType "clickThrough"
```

So even the SCREEN navigate carries an empty url. The screen is addressed by
`screenId`, not by an address a browser could be pointed at.

### C3 -- the "Edit" button (THE editor entry point, and it is not a link)

| property | value |
|---|---|
| tag | `button`, `type="button"` |
| accessible name | `aria-label="Edit"` |
| `componentkey` SHAPE | opaque uuid (FX: `4623f77c-1a18-4c85-9f42-d4115640cc74`; RAW: `e7d233d0-530a-4a4e-ae04-3cdd7d05f262`) |
| `aria-expanded` | **absent in all four profile captures** -- it is not a disclosure |
| href | none |
| position | immediate sibling of the C2 card's anchor, inside the same carousel `<li>` |
| icon | `svg id="edit-small"`, `data-token-id="75"` (hydrated); a `data-dynamic-icon-loading` placeholder pre-hydration |

Occurrence count of `button[aria-label="Edit"]` in DOM: FX-pre **1**, FX-hyd **1**,
FX-skl 0, RAW-pre **1**, RAW-hyd **1**. In every capture it is the ONLY button whose
accessible name is exactly `Edit`, so the selector is unambiguous today.
(Other `Edit*` labels present -- `Edit profile`, `Edit about`, `Edit profile language`,
`Edit Public profile & URL`, `Edit default activity` -- none is an exact match.)

Its click action, resolved from the RAW-pre flight payload (offsets 681922 and 682537),
under `viewName: "profile-edit-open-to"`, `legacyControlName: "edit_open_to"`:

```
1  SetState  BUTTON_STATE_PREF_COLLECTION_SeekerPrefCollectionOrigin_PROFILE = "Disabled"   (isOptimistic)
2  SetState  BUTTON_DISABLED_VISUAL_PREF_COLLECTION_SeekerPrefCollectionOrigin_PROFILE = true (isOptimistic)
3  ServerRequest
     requestId : com.linkedin.sdui.requests.preferenceCollection.saveAndFetchNextStepRequest
     payload   : currentStep = SeekerPrefCollectionStepType_ENTRY_POINT
                 origin      = SeekerPrefCollectionOrigin_PROFILE
                 isEditFlow  = true
                 isOtwV2     = false
                 hasSemanticPref = false, isPreNile = false
                 skipNextStepNavigation = false, skipBackNavigation = false
                 fromDeleteConfirmationPrivateSetting = false
   tracking    : actionType "edit"
```

There is no url anywhere in that action. The editor is an RPC response, and the RPC is
named `saveAndFetchNextStep` -- read that name again before designing the capture (see
section 6).

### C4 -- photo-frame markers

None on the operator, at either hydration state. Full detail in section 5.

### Which controls appear where

| control | FX-pre | FX-hyd | FX-skl | RAW-pre | RAW-hyd |
|---|---|---|---|---|---|
| `button[aria-label="Open to"]` | 2 | 2 | 0 | 2 | 2 |
| same button carries `aria-expanded` | no | yes (`false`) | - | no | yes (`false`) |
| C2 card text `Open to work &#183; Recruiters only` | 1 | 1 | 0 | 1 | 1 |
| `button[aria-label="Edit"]` (the OTW editor entry) | 1 | 1 | 0 | 1 | 1 |
| any `role="menu"` / `role="menuitem"` in DOM | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| any `role="dialog"` in DOM | 0 | 0 | 0 | 0 | 0 |
| `#OpenToWork` frame marker on the operator's photo | 0 | 0 | 0 | 0 | 0 |

`profile_skills.html` contains ZERO open-to-work signal of any kind (0 buttons at all,
0 occurrences of every OTW search term). It is in the corpus as a control, and it
behaves as one.

---

## 2. Is there ANY navigable url that reaches the editor? No. Here are the numbers.

### What was enumerated

| tag | `<a href>` in DOM | any `href=` attr in DOM | distinct `<a>` href values | distinct absolute URL strings in WHOLE file | distinct quoted path strings in unescaped payload |
|---|---|---|---|---|---|
| FX-pre | 11 | 11 | 6 | 6 | 0 |
| FX-hyd | 19 | 19 | 11 | 11 | 0 |
| FX-skl | 7 | 7 | 7 | 7 | 0 |
| RAW-pre | 30 | 32 | 24 | 97 | 35 |
| RAW-hyd | 142 | 144 | 75 | 116 | 2 |
| **total** | **209** | **213** | **123** | **237** | **37** |

209 anchor hrefs examined. 237 distinct absolute-URL strings examined across the whole
of all five files, script payload included. 37 distinct payload path strings examined
(the RAW-pre payload had to be un-escaped first -- its JSON lives inside a JS string
literal, so a naive scan reports 0 and is wrong).

### Buckets

RAW-hyd `<a>` hrefs, 142 occurrences / 75 distinct, by first path segment:

```
/in/ 72   /feed/ 21   /analytics/ 9   /safety/ 7   /company/ 4   root(/) 4
relative 4   /help/ 3   /mynetwork/ 2   /showcase/ 2
/accessibility/ /ad/ /advertise/ /dashboard/ /grow/ /jobs/ /learning/ /legal/
/messaging/ /mypreferences/ /notifications/ /public-profile/ /sales-solutions/
/talent-solutions/  -- 1 each
```

RAW-pre `<a>` hrefs, 30 occurrences / 24 distinct: root(/) 11, `/in/` 6, `/help/` 3,
and 1 each of `/accessibility/ /ad/ /advertise/ /grow/ /legal/ /mynetwork/
/mypreferences/ /public-profile/ /sales-solutions/ /talent-solutions/`.
The 11 bare-root hrefs are the pre-hydration placeholder state: every SDUI link that
gains a real href after hydration renders as `https://www.linkedin.com/` before it.

Fixtures: FX-pre root(/) 6 + `/in/` 4 + `/mynetwork/` 1; FX-hyd `/in/` 11 +
`/analytics/` 6 + `/dashboard/` 1 + `/mynetwork/` 1; FX-skl `/in/` 7.

### The nearest misses, all inspected individually

26 of the 237 URL strings matched an editor-hint substring
(`opentowork|open-to-work|careerinterests|career-interests|psettings|jobseeker|
opportunit|hiring|providing|preferences|jobalert|/edit`). Every one was read.
The complete set of distinct near-miss targets, in shape form:

| url (shape) | what it actually is | reaches OTW editor? |
|---|---|---|
| `/in/<vanity>/opportunities/hiring-opportunities/onboarding/` | the **Hiring** product's onboarding, a different open-to surface | no |
| `/in/<vanity>/opportunities/services/education/` | **Providing services** explainer ("How it works") | no |
| `/in/<vanity>/opportunities/volunteering/education/?profileId=<member urn>` | **Volunteering** explainer ("How it works") | no |
| `/in/<vanity>/edit/intro/` | name / headline / location editor | no |
| `/in/<vanity>/edit/secondary-language/` | profile language | no |
| `/in/<vanity>/edit/forms/summary/new/` | About section | no |
| `/in/<vanity>/edit/forms/content-collections-star-pill/new/` | featured collections | no |
| `/in/<vanity>/overlay/contact-info/` | contact info overlay | no |
| `/public-profile/settings/` | public-profile visibility | no |
| `/mypreferences/d/`, `/mypreferences/d/categories/privacy/` | account settings hub | no |
| `/psettings/select-language` | interface language | no |
| FX-skl `/in/<vanity>/details/skills/edit/forms/<id>/` x6 | skill editors | no |

**Count of urls, in any of the five captures, that reach an open-to-work editor, a
job-opportunities preferences page, or a career-interests page: 0 out of 237.**

Two supporting measurements:

- The literal strings `opentowork` and `open-to-work` occur **0 times** in all five
  files combined. The legacy url `https://www.linkedin.com/psettings/open-to-work`
  that `tests/test_readonly.py` lists under BLOCKED does not appear anywhere in any
  capture -- the denylist entry is defending a door LinkedIn no longer builds.
- The string `psettings` occurs exactly **2 times**, both in RAW-pre, both non-navigable:
  once as `/psettings/select-language`, and once inside the SDUI router's own
  `disallowedPathnames` list -- LinkedIn's client explicitly refuses to interop-navigate
  to `/psettings`.

---

## 3. Activation shape, and whether any capture holds the revealed menu

### The shape

`button[aria-label="Open to"]` carries `aria-expanded="false"` once hydrated and no
`aria-expanded` at all before hydration. That is a **disclosure**: the thing it controls
does not exist in the DOM until the button is activated, and `aria-expanded` flipping to
`true` is the only DOM-visible acknowledgement. Confirmed against the flight payload --
its click trigger is `proto.sdui.actions.core.ShowMenu`:

```
placement : Placement_BOTTOM_START
isExpandable : true
component : div role="menu" style maxWidth 26.8rem, children [$L153, $L154, $L155]
dismissActionType : actionType "dismissMenu"
```

The menu's markup is a lazy chunk reference. It is rendered client-side on click, which
is why no capture holds it.

### Does any capture hold the revealed menu, or the modal?

| | FX-pre | FX-hyd | FX-skl | RAW-pre | RAW-hyd |
|---|---|---|---|---|---|
| `role="menu"` in DOM | 0 | 0 | 0 | 0 | 0 |
| `role="menuitem"` in DOM | 0 | 0 | 0 | 0 | 0 |
| `role="dialog"` in DOM | 0 | 0 | 0 | 0 | 0 |
| `aria-modal` in DOM | 0 | 0 | 0 | 0 | 0 |
| `<dialog>` elements in DOM | 0 | 0 | 0 | 2 | 4 |
| `"role":"menu"` in flight payload | 0 | 0 | 0 | 12 | 0 |
| `"role":"menuitem"` in flight payload | 0 | 0 | 0 | 24 | 0 |
| `ShowMenu` actions in payload | 0 | 0 | 0 | 15 | 0 |
| `ServerRequest` actions in payload | 0 | 0 | 0 | 24 | 0 |

**No capture contains a rendered menu or a rendered modal.** The `<dialog>` elements
found in the raw captures were opened and read: all of them are LinkedIn's ad-options
overlays ("Ad Options / Why am I seeing this ad?" and "Don't want to see this"), 2
distinct shells rendered twice each in RAW-hyd. Not one is an open-to-work surface.

RAW-hyd is the interesting negative: it has 40 `aria-expanded` attributes (35 on
buttons), every single one `"false"`, and 0 menus in the DOM. Nothing was expanded when
the capture was taken.

### Menu-item text, presence and absence, per capture

`whole file | DOM only`:

| text a reader would expect | FX-pre | FX-hyd | FX-skl | RAW-pre | RAW-hyd |
|---|---|---|---|---|---|
| `Share that you're open to work` | 0\|0 | 0\|0 | 0\|0 | **0\|0** | 0\|0 |
| `Finding a new job` | 0\|0 | 0\|0 | 0\|0 | **0\|0** | 0\|0 |
| `Hiring` | 0\|0 | 0\|0 | 0\|0 | **3\|0** | 4\|4 (unrelated: a company name) |
| `Providing services` | 0\|0 | 0\|0 | 0\|0 | **3\|0** | 0\|0 |
| `Share that you` (prefix) | 0\|0 | 0\|0 | 0\|0 | **3\|0** | 0\|0 |
| `Showcase services you offer` | 0\|0 | 0\|0 | 0\|0 | 2\|0 | 0\|0 |
| `Finding volunteer opportunities` | 0\|0 | 0\|0 | 0\|0 | 3\|0 | 0\|0 |

Two things to read off that table.

**(a) The menu text that IS present is present only in RAW-pre's script payload, never
in any DOM.** `Hiring` / `Providing services` / `Finding volunteer opportunities` and
their subtitles appear 3x each -- once per rendering variant -- inside
`self.__next_f` flight chunks, at DOM count 0. A grep of the raw file that does not
strip `<script>` will report these as "found" and be wrong. The 4 DOM hits for `Hiring`
in RAW-hyd are a third-party company name in an unrelated card, not a menu item.

**(b) The Open-To menu, as this account is currently served, does NOT contain an
open-to-work item at all.** The three lazy children were resolved out of the payload:

| chunk | `legacyControlName` | label | action | url |
|---|---|---|---|---|
| `$L153` / `$L166` | `opento_button_hiring` | `Hiring` / "Share that you're hiring and attract qualified candidates" | CloseMenu, SetState, **Navigate -> NavigateToUrl** | `/in/<vanity>/opportunities/hiring-opportunities/onboarding/` |
| `$L154` / `$L167` | `opento_button_smp` | `Providing services` / "Showcase services you offer so new clients can discover you" | CloseMenu, **Navigate -> NavigateToScreen** `ProfileServicesEducation` | `/in/<vanity>/opportunities/services/education/` |
| `$L155` / `$L168` | `opento_button_otv` | `Finding volunteer opportunities` / "Show that you are open to skill-based volunteering" | CloseMenu, **Navigate -> NavigateToScreen** `ProfileOpenToVolunteerEducation` | `/in/<vanity>/opportunities/volunteering/education/?profileId=<member urn>` |

3 items, each `role="menuitem"`, no fourth. The "Finding a new job" item is absent
**because the account already has it on** -- the menu offers only the open-to products
not yet enabled. That is a load-bearing finding: **clicking "Open to" is a dead end for
this action in the current state.** Any procedure that starts there reaches hiring,
services or volunteering, and never the audience control.

For completeness, the topcard `More` button's menu was resolved the same way -- 5 items,
`share_profile_via_message` / "Save to PDF" / `resources_my_items` / "Activity" /
`profile_verification`. No open-to-work item there either.

---

## 4. The current state, as rendered (SANITISED FIXTURES ONLY)

LinkedIn prints one string, and it is a single text node:

```
Open to work &#183; Recruiters only
```

`&#183;` is MIDDLE DOT (U+00B7), which is exactly what `shape.MIDDLE_DOT` /
`shape._OPEN_TO_WORK` expect.

Where it sits, verbatim from the tracked fixtures:

- **FX-pre** (`profile_topcard.html`, offset ~15,472): inside
  `<section><ul><li><div componentkey="auto-component-9b53a9f4-..."><a href="https://www.linkedin.com/">`
  -> `<div><p><span><strong>Open to work &#183; Recruiters only</strong></span></p></div>`,
  followed by sibling `<p><span>India | On-site &#183; Hybrid</span></p>` and
  `<p><span>Show details</span></p>`.
- **FX-hyd** (`profile_topcard_hydrated.html`, offset ~15,096): byte-identical text
  node, identical `componentkey`, identical DOM shape. The only difference in the
  surrounding markup is the anchor href, which hydrates from
  `https://www.linkedin.com/` to `https://www.linkedin.com/in/alex-rivera-8c21/?isSelfProfile=true`.

So the read side's premise holds: **the audience string is readable at BOTH hydration
states, from the same node, with no extra page load.** `parse_open_to_work` returns
`{on: True, audience: "Recruiters only"}` off either fixture. Occurrence count in each
fixture: exactly 1.

**Audience states represented anywhere in the corpus: 1 of 3.**

| state | occurrences across all five files |
|---|---|
| `Recruiters only` | FX-pre 1, FX-hyd 1, RAW-pre 2 (1 DOM + 1 payload), RAW-hyd 1 |
| `All LinkedIn members` | **0** |
| `My network only` | **0** |
| off / no line rendered | **0** (never observed) |

`shape.OPEN_TO_WORK_AUDIENCES` names two audiences and `writes.py` adds an `off` third.
Only the first has ever been rendered on this account. The reader's refusal to
interpret an unseen audience string is therefore still doing real work, not defending
a hypothetical.

---

## 5. The photo frame -- there IS a DOM discriminator, and it says "no frame"

Search terms used: `profile-framedphoto`, `profile-displayphoto`, `framedphoto`,
`displayphoto`, `photoFrame`, `PhotoFrame`, `photo-frame`, `frame`, `hashtag`,
`#OpenToWork`, `OPEN_TO_WORK`, `openToWork`, `is open to work`.

Findings:

| tag | `profile-framedphoto` | `profile-displayphoto` | `alt`/`aria-label` matching `open to work` |
|---|---|---|---|
| FX-pre | 0 | 0 | 0 |
| FX-hyd | 0 | 0 | 0 |
| FX-skl | 0 | 0 | 0 |
| RAW-pre | 0 | 49 (9 in DOM) | 0 |
| RAW-hyd | **1** | 37 | **1** |

**The discriminator exists and it is nameable.** LinkedIn serves a member's avatar from
one of two media paths, and the path itself declares whether a frame is drawn:

- `https://media.licdn.com/dms/image/v2/<id>/profile-displayphoto-<variant>/...` -- no frame
- `https://media.licdn.com/dms/image/v2/<id>/profile-framedphoto-<variant>/...` -- framed

and the framed variant is accompanied by an accessible name that says so in words. The
single framed photo in RAW-hyd (offsets 346090 and 347053) belongs to a THIRD-PARTY
member in a recommendations rail, and carries both
`aria-label="<other member> is open to work"` on the placeholder `<svg role="img">` and
`alt="<other member> is open to work"` on the `<img>`.

The operator's own topcard photo, in RAW-hyd at offsets 24468 / 26645 / 33035 / 35212
(4 renders of the same node), is
`.../profile-displayphoto-scale_100_100/...` with `alt=""`. **No frame.** That is exactly
consistent with the `Recruiters only` audience, and it means a reader CAN verify the
public badge independently of the text line:

```
frame drawn  <=>  the topcard <img> src contains "profile-framedphoto"
             <=>  an alt/aria-label reading "<name> is open to work" exists on it
```

Two caveats, both measured:

1. **The fixtures cannot test this.** Both topcard fixtures contain 0 occurrences of
   `displayphoto` and 0 of `framedphoto` -- the sanitiser stripped the media urls, and
   the surviving `<img>` tags (1 in FX-pre, 2 in FX-hyd) have empty `alt` and no
   usable src. A frame check written against the fixtures would be a check that cannot
   fail. It needs a fresh sanitised fixture that PRESERVES the photo-path segment.
2. **The positive case has only ever been observed on someone else's photo.** We have
   the framed shape from a third party, never from this account -- so the check is
   founded on one real observation of the ON state, in the right product surface, on
   the wrong person.

Terms that found nothing anywhere: `#OpenToWork` (0), `OPEN_TO_WORK` (0),
`openToWork` (0), `photoFrame`/`PhotoFrame`/`photo-frame` (0), `hashtag` (0).

---

## 6. The exact procedure that would capture the editor

Named by accessible name. `[NAV]` = navigation, `[ACT]` = activation (a click on a live
control). The order matters and the danger is concentrated in one step.

| # | kind | control / target | what it does | risk |
|---|---|---|---|---|
| 1 | `[NAV]` | `https://www.linkedin.com/in/<vanity>/` | loads the profile. Already on the read allowlist. | none |
| 2 | -- | wait for hydration | proof: `button[aria-label="Open to"]` has gained `aria-expanded="false"`, and the carousel anchor's href has changed from `https://www.linkedin.com/` to the self-profile url. Both are measured discriminators, not timers. | none |
| 3 | -- | locate the card | first `<li data-testid="carousel-child-container">`; assert its text starts `Open to work &#183; ` . No scroll or activation needed -- it is carousel index 0 in both raw captures. | none |
| 4 | `[ACT]` | **`Show details`** (the card body; `role="button"` in the payload, an `<a>` in the DOM) | opens screen `com.linkedin.sdui.flagshipnav.jobs.PrefCollectionDetailView` as a MEDIUM modal. Its action list contains **one** `Navigate` and **no** `ServerRequest`. Tracking `actionType: "clickThrough"`. | **low** -- read-shaped. Capture here FIRST. |
| 5 | -- | capture the detail modal | this is the first surface that shows the current preferences as controls. Nothing in any capture on disk tells us whether the AUDIENCE control lives here or only one level deeper -- that is precisely what step 4 buys. | none |
| 6 | -- | dismiss | the modal declares its own dismiss tracking (`spcPrefDetailsDismissIcon`). Use it rather than a back-navigation. | none |
| 7 | `[ACT]` | **`Edit`** (`button[aria-label="Edit"]`, the only exact match on the page) | fires `SetState` x2 then `ServerRequest com.linkedin.sdui.requests.preferenceCollection.saveAndFetchNextStepRequest` with `isEditFlow: true`, `currentStep: SeekerPrefCollectionStepType_ENTRY_POINT`. | **THIS IS THE DANGEROUS STEP** |
| 8 | -- | capture the returned screen | **step 7 is the step that first shows the editor's controls.** There is no intermediate. | -- |
| 9 | -- | repeat 7-8 for each subsequent step | the payload names `skipNextStepNavigation`, `skipBackNavigation`, `skipComplexBackNavigation` and `fromDeleteConfirmationPrivateSetting`, so the editor is a multi-step wizard with a delete/turn-off confirmation somewhere in it, not one modal. Budget for N screens, not 1. | rising |

Explicitly:

- **First step that shows the editor's controls: step 7.**
- **First step that could change state if mis-clicked: also step 7.** The two are the
  same click. The request's own id is `saveAndFetchNextStep` -- LinkedIn's naming, not
  ours -- and the button optimistically writes two `SetState` values before the request
  even leaves. Nothing readable on disk proves the ENTRY_POINT step persists anything;
  nothing proves it does not. **Treat step 7 as a write until a supervised capture says
  otherwise.** Steps 1-6 are provably safe by their own action lists.
- The `Open to` topcard button is NOT in this procedure. It is the obvious-looking
  control and it is the wrong one: in the current state its menu offers Hiring,
  Providing services and Finding volunteer opportunities, and nothing else (section 3).
  Clicking it is harmless -- `ShowMenu` is client-side, no ServerRequest -- but it is a
  detour, and two of its three items navigate away from the profile.
- The whole procedure needs a human at the keyboard for step 7 onward. No part of it
  can be reached by navigation, so no part of it can be reached by a url allowlist.

What a completed capture would yield for the write spec: not a `url_template` -- there
is none to yield -- but the accessible names, `componentkey` shapes and
`aria-*` states of the audience control, at which point `set_open_to_work` could be
specced the way `save_job` is: an anchor label plus a measured before/after read. Until
then the honest field is `url_template=None` and the honest verdict is UNPERFORMABLE.

---

## 7. Counts, collected

| measurement | value |
|---|---|
| files read in full | 5 |
| total chars read | 1,654,517 |
| chars of RAW-pre that are flight payload, not DOM | 1,091,238 of 1,177,077 (92.7%) |
| `<a href>` occurrences enumerated | 209 |
| distinct absolute URL strings enumerated (DOM + payload) | 237 |
| distinct payload path strings enumerated (after un-escaping) | 37 |
| of those, matching an editor-hint substring | 26 |
| of those 26, reaching an OTW editor / job-preferences / career-interests page | **0** |
| occurrences of `opentowork` or `open-to-work` in all five files | **0** |
| occurrences of `psettings` | 2, both non-navigable (one is in `disallowedPathnames`) |
| `button[aria-label="Open to"]` per profile capture | 2 (+1 unlabelled skeleton copy in raw) |
| `button[aria-label="Edit"]` per profile capture | 1, unique |
| items in the `Open to` menu, resolved from payload | 3 |
| of those, offering the open-to-work audience | **0** |
| items in the `More` menu, resolved from payload | 5, none OTW |
| rendered `role="menu"` / `role="menuitem"` / `role="dialog"` in any DOM | 0 / 0 / 0 |
| `<dialog>` elements in raw DOM | 2 (pre), 4 (hyd) -- all ad-options overlays |
| `aria-expanded` attributes in RAW-hyd DOM | 40, all `"false"` |
| audience states observed of 3 possible | **1** (`Recruiters only`) |
| `profile-framedphoto` on the operator's photo | 0 |
| `profile-framedphoto` anywhere in RAW-hyd | 1, belonging to a third party |
| SDUI `Navigate` actions in RAW-pre payload carrying a non-empty `url` for an OTW surface | **0** |

---

## 8. Verdict

`url_template=None` is a **correct description of reality as of these captures**, and
the reason is stronger than the comment in `writes.py` currently states. The comment says
the editor "is a modal that has never loaded", which reads as an accident of capture
coverage -- as though someone simply never clicked the right thing. The payload says
something harder: the open-to-work editor is not addressed by a url AT ALL. It is
fetched by an SDUI RPC, `com.linkedin.sdui.requests.preferenceCollection.saveAndFetchNextStepRequest`,
fired from a `button[aria-label="Edit"]` that has no href, no `aria-expanded`, and an
opaque uuid `componentkey`; and the sibling action on the same card that DOES use a
screen navigate (`PrefCollectionDetailView`) carries `"url": ""` -- an empty string --
because in this architecture screens are addressed by `screenId`, not by an address a
browser can be pointed at. I enumerated 237 distinct URL strings and 37 payload path
strings across all five captures and zero of them reach the editor, a job-opportunities
preferences page, or a career-interests page; the legacy `psettings/open-to-work` url
that the read denylist still guards appears nowhere, and `/psettings` is on LinkedIn's
own `disallowedPathnames` list. There is no url nobody tried. There is a **button**
nobody has clicked, and clicking it is the only way in -- which is why the action stays
UNPERFORMABLE and why `assert_write_url` refusing it outright is the right behaviour
rather than a gap. Two things did change, though, and the wave should take them: (1) the
editor's entry point is now IDENTIFIED and, better, it is already pinned in the tracked
sanitised fixtures at both hydration states as the page's unique `button[aria-label="Edit"]`
beside `Open to work &#183; Recruiters only` -- so the control can be asserted in tests
today without touching a raw capture; and (2) the `Open to` topcard button, the control
the current spec cites as evidence, does NOT lead to the audience editor in this
account's state -- its three menu items are Hiring, Providing services and Finding
volunteer opportunities, because "Finding a new job" is already on. Any future capture
attempt that starts at `Open to` will fail, and the reason will not be obvious from the
DOM.
