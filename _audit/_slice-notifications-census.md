# Slice census: is there a mark-read control on the LinkedIn notifications surface?

READ-ONLY census. No code edited, no git run, no pytest run, no browser launched.

Instrument: `html.parser` walk of the frozen fixture plus literal `grep` counts.
The walk script is disposable (a one-surface DOM enumeration; nothing general
enough for the instrument register) and was kept in the session scratchpad.

## 0. Sources actually read

| file | role | bytes |
|---|---|---|
| `tests/fixtures/notifications.html` | THE evidence. Frozen, sanitised, tracked. Invented names, safe to quote. | 31029 on disk / 30209 after newline normalisation |
| `linkedin_server/dom.py` | harvester + selector constants | 42763 |
| `linkedin_server/shape.py` | `parse_notification` + the chrome-phrase list | 63297 |
| `linkedin_server/server.py` | `linkedin_notifications`, `known_side_effects` | 71988 |
| `tests/test_sdui_surfaces_fixture.py` | what the fixture is pinned to | 44468 |
| `linkedin_server/writes.py` | `PERMANENTLY_FORBIDDEN` | context only |
| `tests/test_readonly.py` | navigation allowlist / blocklist | context only |

### Other captures: swept, and they hold nothing

Every `_audit/_probe-*.html` (15 files) and every other `tests/fixtures/*.html`
(17 files) was scanned for `nt-card`, `notification-card-container`,
`nt-card--unread`, `nt-card-settings-dropdown` and `mark all as read`.

- `notification-card-container`: **0** occurrences outside the fixture.
- `nt-card--unread`: **0** occurrences outside the fixture.
- `nt-card-settings-dropdown`: **0** occurrences outside the fixture.
- `nt-card`: 2 occurrences in each of 5 probe files, and **all 10 are false
  positives** -- the substring inside the A/B flag key
  `games-web.pinpoi[nt-card]-clue-overflow`. Not markup. Not a notification.

Repo-wide, the only two source files carrying this surface's markup are
`tests/fixtures/notifications.html` (76 matching lines) and `dom.py`
(2 lines, the selector constants).

**Consequence: `notifications.html` is the ONLY capture of this surface that
exists anywhere in the repo.** Nothing corroborates it and nothing extends it.
No PII from any raw probe reached this document, because no raw probe contained
any notification markup to begin with.

### One artifact deliberately NOT examined

A repo-wide sweep also matched `nt-card-settings-dropdown` inside
`_state/chrome-profile/Default/Code Cache/js/58876478c99f7273_0` -- a Chrome
compiled-JS cache blob in the operator's live browser profile, i.e. LinkedIn's
own shipped bundle. Reading it was attempted and **denied by the permission
system**, and no attempt was made to work around that. It is out of this
slice's named scope (`_audit/` and `tests/fixtures/`), and it is the operator's
live profile.

Recorded here as a pointer, not a gap silently closed: that blob is the one
place on this machine that might name a mark-read control the DOM does not
expose. It is the natural next probe **if** the wave wants the question closed
beyond the rendered surface. Note that the same repo-wide sweep for
`mark all as read` returned **zero** hits across every file including that
blob, which is weak evidence in the same direction.

---

## 1. Complete control inventory

Root of the fixture is `<main>` with exactly ONE child, `div.nt-card-list`,
holding 6 `<article>` elements. See section 5 for why that root matters.

### Totals

| kind | count |
|---|---|
| `<article>` notification cards | **6** |
| `<button>` elements, all kinds | **22** |
| `<a>` elements | **12** |
| elements with `role="button"` | **0** |
| elements with `role="link"` | **2** (both are `<button role="link">`) |
| `<input>`, `<form>`, `<nav>`, `<header>`, `<footer>` | **0** each |
| total activatable controls | **34** |

### The 22 buttons, by kind

| kind | accessible name | count | source of the name |
|---|---|---|---|
| overflow trigger | `Settings menu` | **6** | `aria-label` |
| dropdown item | `Change notification preferences` | **6** | button text (`p.nt-card-settings-dropdown-item__headline`) |
| dropdown item | `Delete notification` | **6** | button text |
| dropdown item | `Show less like this` | **2** | button text |
| card CTA | `View jobs` | **2** | visible span plus a `.visually-hidden` twin (printed twice) |

6 + 6 + 6 + 2 + 2 = 22. Confirmed.

### The 12 anchors, by kind

| kind | count | accessible name source |
|---|---|---|
| left-rail avatar link, `data-view-name="notification-card-image"` | **6** | `aria-label` |
| headline link, `a.nt-card__headline`, no `data-view-name` | **6** | text content only; NO `aria-label` on any of the six |

### Position in the card structure

Every card is the same skeleton:

```
article.nt-card [aria-label, data-view-name="notification-card-container"]
  div.nt-card__container
    div.nt-card__left-rail
      figure.nt-card__blue-dot-figure      <- UNREAD CARDS ONLY (1 of 6)
      a [aria-label, data-view-name="notification-card-image"]   <- CONTROL 1
    div.display-flex.flex-column.flex-grow-1
      a.nt-card__headline                                        <- CONTROL 2
        p.visually-hidden "Unread notification."   <- UNREAD CARDS ONLY
      [optional] section.nt-social-counts          (text, not a control)
      [optional] button[role=link] "View jobs"                   <- CONTROL 3
    div.display-flex.flex-column.text-align-right
      p.nt-card__time-ago                          (text, not a control)
      div.artdeco-dropdown
        button[aria-label="Settings menu"][aria-expanded="false"] <- CONTROL 4
        div.nt-card-settings-dropdown__content[aria-hidden="true"]
          button.nt-card-settings-dropdown-item__button  x2 or x3 <- CONTROLS 5..7
```

### Per-card breakdown

| card | line | unread | avatar `a` | headline `a` | CTA button | overflow trigger | dropdown items | controls |
|---|---|---|---|---|---|---|---|---|
| 1 | 8 | **YES** | 1 | 1 | 1 (`View jobs`) | 1 | 2 | 6 |
| 2 | 151 | no | 1 | 1 | 0 | 1 | 2 | 5 |
| 3 | 286 | no | 1 | 1 | 0 | 1 | 3 | 6 |
| 4 | 410 | no | 1 | 1 | 0 | 1 | 3 | 6 |
| 5 | 554 | no | 1 | 1 | 1 (`View jobs`) | 1 | 2 | 6 |
| 6 | 691 | no | 1 | 1 | 0 | 1 | 2 | 5 |
| **totals** | | **1 / 6** | **6** | **6** | **2** | **6** | **14** | **34** |

Accessible names of the 6 avatar anchors, verbatim from `aria-label`
(fixture values are invented and safe to quote; two apostrophes are written as
the entity `&#8217;` in the source, i.e. U+2019 when decoded):

1. `Profile image for several companies on LinkedIn`
2. `View Dana Whitfield&#8217;s profile.`
3. `View Forgeworks`
4. `View Robin Ellery&#8217;s profile.`
5. `Profile image for several companies on LinkedIn`
6. `Sam Okonkwo's connection is hiring for a Senior Software Engineer (SDE-3) Java at Brightpath. Explore jobs in your network.`

**Not one of the 34 controls names read, unread, seen, or a badge.**

---

## 2. The overflow menu

One per card, 6 total. Trigger:

```html
<button aria-expanded="false" aria-label="Settings menu"
        id="nt-card-settings-dropdown-trigger-ember54"
        class="artdeco-button artdeco-button--muted artdeco-button--tertiary
               artdeco-button--circle artdeco-dropdown__trigger
               artdeco-dropdown__trigger--placement-bottom ember-view"
        type="button">
```

All 6 triggers carry `aria-expanded="false"`. All 6 dropdown content wrappers
carry `aria-hidden="true"`.

### Every item, verbatim, in document order

| card | pos | item headline (verbatim) | line |
|---|---|---|---|
| 1 | 1 | `Change notification preferences` | 112 |
| 1 | 2 | `Delete notification` | 133 |
| 2 | 1 | `Change notification preferences` | 247 |
| 2 | 2 | `Delete notification` | 268 |
| 3 | 1 | `Change notification preferences` | 354 |
| 3 | 2 | `Delete notification` | 375 |
| 3 | 3 | `Show less like this` | 392 |
| 4 | 1 | `Change notification preferences` | 498 |
| 4 | 2 | `Delete notification` | 519 |
| 4 | 3 | `Show less like this` | 536 |
| 5 | 1 | `Change notification preferences` | 652 |
| 5 | 2 | `Delete notification` | 673 |
| 6 | 1 | `Change notification preferences` | 779 |
| 6 | 2 | `Delete notification` | 800 |

**14 items across 6 menus.** Three distinct labels. Menu size is 2 or 3: the
two job-alert cards (1, 5) and the two profile/network cards (2, 6) get 2; the
two feed-content cards (3, 4) get a third, `Show less like this`.

Every item carries an empty `p.nt-card-settings-dropdown-item__sub-headline` --
no item has explanatory sub-text.

### Does any item mark the notification read?

**No. Zero of 14.** What the 14 actually offer:

- **`Change notification preferences` (6)** -- navigates to a SETTINGS surface.
  Changes what LinkedIn sends in future. Does not touch the state of this card.
- **`Delete notification` (6)** -- DESTROYS the row. This is the only per-card
  state mutation on offer, and it removes the notification entirely rather than
  marking it read. It is also already covered by `writes.PERMANENTLY_FORBIDDEN`
  under `delete_or_withdraw_anything`: *"destruction is not a write this design
  covers, at any confirm level"*.
- **`Show less like this` (2)** -- a RANKING signal to the feed algorithm.
  Not a read-state change.

### Is the dropdown in the DOM before activation?

**Yes -- present, not deferred.** All 14 item buttons and their full text sit in
the static markup while `aria-expanded="false"` and the wrapper is
`aria-hidden="true"`. The menu is CSS/ARIA-hidden, not lazily rendered.

Independently corroborated by `shape.py:105-111`, which lists the three item
labels as chrome precisely because they leak into `innerText` depending on
render state:

```
    # The notification card's overflow menu. LinkedIn keeps these behind a
    # button, so whether they reach innerText depends on whether the menu is
    # open -- the same render-state dependency the harvesters are arranged to
    # be immune to. Named here so the body reads the same either way.
    "change notification preferences",
    "delete notification",
    "show less like this",
```

**This is a load-bearing negative.** Because the dropdown IS in the DOM
unactivated, a mark-read item -- if one existed -- would be visible to a static
read. Its absence is not an artefact of the capture missing a lazy render. The
menu is fully enumerated here, and it has no mark-read item.

---

## 3. How unread state is expressed

Exactly **four** signals, all on card 1, none anywhere else:

| # | signal | exact string | count in file |
|---|---|---|---|
| 1 | class on the `<article>` | `nt-card--unread` | 1 |
| 2 | `aria-label` on the `<article>` | `Unread notification.` (read cards say `Notification`) | 1 |
| 3 | decorative figure in the left rail | `<figure class="nt-card__blue-dot-figure mt5" aria-hidden="true">` | 1 |
| 4 | visually-hidden `<p>` inside the headline anchor | `<p class="visually-hidden">Unread notification.</p>` | 1 |

The unread card's opening tag, verbatim:

```html
<article class="nt-card
      nt-card--unread
      nt-card--with-hover-states

      " aria-label="Unread notification." data-view-name="notification-card-container">
```

A read card's, for contrast:

```html
<article class="nt-card

      nt-card--with-hover-states

      " aria-label="Notification" data-view-name="notification-card-container">
```

The blue dot is an empty decorative element -- `aria-hidden="true"`, no text,
no child. It is a visual marker only, and it is the sole `<figure>` in the file.

**Counts: 1 unread card, 5 read cards, of 6.**

Corroborated by `tests/test_sdui_surfaces_fixture.py:839-845`:

```python
async def test_the_unread_flag_is_read_before_the_page_load_destroys_it():
    """Exactly one of the six was unread, and the badge is about to be cleared."""
    ...
    assert sum(1 for row in rows if row["unread"]) == 1
```

### Data attributes -- the negative that matters

The file contains exactly **one** `data-*` attribute NAME, `data-view-name`,
with exactly two values:

- `notification-card-container` x6 (on the articles)
- `notification-card-image` x6 (on the avatar anchors)

There is **no** `data-id`, `data-urn`, `data-notification-id`, `data-read`,
`data-unread`, `data-seen`, or anything equivalent. Confirmed by enumerating
every `data-` attribute in the file.

### There is no per-notification identifier at all

- **0 of 6** articles carry an `id` attribute.
- The only `id` values on the surface are Ember render ids (`ember51`,
  `ember138`, `nt-card-settings-dropdown-trigger-ember54`, ...). These are
  per-render-session and not stable across a reload. `dom.py` never uses one,
  and the fixture itself shows the numbering is not even contiguous
  (`ember51..ember104`, then `ember138..ember140` for three avatars).
- The only `urn:li:` strings on the page are **content** urns inside hrefs
  (2 x `urn:li:activity`, 1 x `urn:li:ugcPost`) -- they identify the POST a
  notification is about, not the notification. **Two of the six cards (the job
  alerts) carry no urn of any kind.**

Term counts across the whole fixture (case-insensitive):
`mark` = **0**, `as read` = **0**, `seen` = **0**, `dismiss` = **0**,
`badge` = **0**, `checkbox` = **0**, `switch` = **0**, `menuitem` = **0**,
`aria-current` = **0**. `read` = 3, and **all three are the substring inside
`unread`** (`nt-card--unread`, and the two `Unread notification.` strings).

---

## 4. Is unread state addressable per notification?

**No.**

Three independent blockers, any one of which is sufficient:

1. **No control.** Nothing in the 34-control inventory, and nothing in the 14
   fully-enumerated menu items, changes read state. There is no element to click.
2. **No target.** Even granting a hypothetical control, there is no stable
   handle for "this one notification": no id on the article, no urn for the
   notification, no data attribute, and 2 of 6 cards carry no identifier of any
   kind. The only addressing available is ordinal position in a list whose
   order changes between loads.
3. **No read path.** Unread state on this surface is EXPRESSED (a class, an
   aria-label, a dot, a hidden paragraph) but never OFFERED as something a
   caller can set. It is output, not input.

Stated plainly, as the brief asks: **the only mark-read mechanism on this
surface is page-level and server-side.** LinkedIn decides the whole list is seen
at the moment it serves `/notifications/`. There is no per-item read, no
per-item write, and no per-item address.

---

## 5. Does any control exist that would clear the badge deliberately?

### In the fixture: no -- with one honest limit on what the fixture can prove

Search terms run over the fixture, all case-insensitive, all **0 hits**:
`mark`, `mark all`, `as read`, `mark as read`, `seen`, `dismiss`, `clear`,
`badge`, `checkbox`, `switch`, `menuitem`, `aria-current`, `form`, `input`.

**The limit, stated rather than glossed:** the fixture's root is
`<main><div class="nt-card-list"> ... </div></main>`. `main` has exactly ONE
child. The capture retains **no** `<nav>`, `<header>`, `<footer>`, `<form>` or
`<input>` -- so the live page's filter strip (the All / Jobs / My posts /
Mentions pills) and any page chrome above the list are simply not in this
capture. A header-level control could not have appeared here either way.

That gap is **not fillable from disk**: as established in section 0, no probe
capture and no other fixture holds any notifications markup. There is no capture
of the notifications page header anywhere in this repository.

So the honest scope of the finding is: **absent from the card list, and absent
from every control the server can currently see.** Whether a page-header
"mark all as read" exists on live LinkedIn is UNVERIFIED here and would need a
fresh capture that keeps the header.

### The one adjacent thing found repo-wide, and what it is

`grep -ri "mark all as read|mark as read|markAllRead|markRead"` over the whole
linkedin package returns exactly **two** hits, both the same URL, and neither is
a DOM control:

- `tests/test_readonly.py:432` -- inside the `BLOCKED` list (declared at :423),
  parametrized into `test_write_and_foreign_urls_are_blocked` at :496-497:

  ```
      "https://www.linkedin.com/notifications/?action=markAllRead",
  ```

- `_audit/_slice-parity-census.md:354` -- a quotation of that same test line.

Read it precisely, because it is easy to over-read:

- It is a **navigation address**, not a control on the surface.
- It exists in this repo only as a **hostile input the allowlist must refuse**.
  The allowlist admits `https://www.linkedin.com/notifications/` and nothing
  with a query on it.
- Whether live LinkedIn actually honours that query parameter is **UNVERIFIED**
  -- no capture, no measurement, no observation on disk supports it. It is a
  test fixture asserting a refusal, not evidence of a feature.
- Even taken at face value it is **all-or-nothing and page-level**: `markAllRead`
  has no per-notification variant. It would not make unread state addressable.

---

## 6. The pre-existing side effect

### The exact `known_side_effects` line

`linkedin_server/server.py:1455-1458`:

```python
            "known_side_effects": [
                "opening the notifications page clears the unread badge",
                "running a job search adds to your own recent-search history",
            ],
```

The same block, a few lines above, already lists the write as forbidden --
`server.py:1447-1454`, inside `out_of_scope_by_design`:

```python
                "marking notifications read",
```

### The code path that loads that page

`linkedin_server/server.py:1173-1183`, inside `linkedin_notifications`:

```python
        async with BROWSER.session() as page:
            final_url = await BROWSER.goto(page, f"{BASE_URL}/notifications/")
            assert_not_authwall(final_url, surface="notifications")
            records = await dom.harvest_block_cards(
                page,
                selectors=dom.NOTIFICATION_SELECTORS,
                max_items=limit * 2,
                hidden_selector=dom.NOTIFICATION_HIDDEN_SELECTOR,
                time_selector=dom.NOTIFICATION_TIME_SELECTOR,
                unread_class=dom.NOTIFICATION_UNREAD_CLASS,
            )
```

That is the whole of it. **One `goto`. No click, no scroll, no per-item open.**
The harvest is a single `page.evaluate` over already-served markup
(`dom.harvest_block_cards`, `dom.py:442-478`).

The tool docstring already says so, `server.py:1149-1153`:

> It cannot be avoided. LinkedIn marks the list seen on the server when the
> page is served, so there is no read of this surface that leaves the badge
> alone: no click, no scroll and no per-item open is involved, and there is
> no mark-as-read call anywhere in this package. The only way not to clear
> the badge is not to call this tool.

The runtime envelope repeats it to the caller at `server.py:1198-1206`, along
with the compensating `unread_when_read` count.

### The consequence, in one sentence

**A mark-read WRITE would add nothing: the READ already causes the entire
observable effect a mark-read would cause -- the badge cleared, all of it,
server-side, on page serve -- so the write would be a second, riskier, less
honest way to produce a change that has already happened by the time any control
could be clicked.**

Two corollaries worth carrying into the wave:

- The write could not even be *sequenced* usefully. To click a control you must
  first load the page; loading the page is what clears the badge. The write can
  only ever run AFTER its own effect has already landed.
- It is therefore unconfirmable by construction, which is exactly the reason
  already recorded in `writes.py:533-536`:

  ```python
      "mark_notifications_read": (
          "clearing his unread badge destroys signal he has not seen, and the "
          "act is server-side on page serve so it cannot even be confirmed first"
      ),
  ```

  This census **confirms that stated reason on the evidence** rather than
  restating it, and adds a second, independent ground the original entry did not
  claim: there is no control and no target.

---

## 7. Counts, consolidated

| quantity | count |
|---|---|
| notification cards (`article.nt-card`) | 6 |
| unread cards | **1** |
| read cards | **5** |
| `<button>` total | 22 |
| ... overflow triggers (`Settings menu`) | 6 |
| ... dropdown item buttons | 14 |
| ... card CTA buttons (`View jobs`, `role="link"`) | 2 |
| `<a>` total | 12 |
| ... avatar links (`data-view-name="notification-card-image"`) | 6 |
| ... headline links (`a.nt-card__headline`) | 6 |
| elements with `role="button"` | 0 |
| distinct dropdown item labels | 3 |
| dropdown items that mark a notification read | **0** |
| dropdown items that DELETE a notification | 6 |
| controls of any kind that change read state | **0** |
| page-level "mark all as read" controls in the capture | **0** |
| stable per-notification identifiers (id / urn / data-*) | **0** |
| `data-*` attribute names in the file | 1 (`data-view-name`) |
| occurrences of "mark" / "as read" / "seen" / "badge" (ci) | 0 / 0 / 0 / 0 |
| other captures in the repo holding notification markup | **0** |

---

## 8. Verdict

A mark-notifications-read write **has no observable control to act on, and no
target to act on it with.** The surface was enumerated exhaustively -- 34
controls across 6 cards, including all 14 overflow-menu items, which are present
in the static DOM before activation and therefore cannot be hiding a mark-read
affordance behind a lazy render -- and not one of them changes read state; the
three things the menu actually offers are a settings navigation, a DESTRUCTIVE
delete, and a feed-ranking signal. Unread state is expressed only as output (a
class, an `aria-label`, an `aria-hidden` blue dot, a visually-hidden paragraph)
and never exposed as anything settable, and the surface carries no stable
per-notification identifier of any kind -- no article `id`, no notification urn,
no `data-*` beyond `data-view-name` -- so even a hypothetical control could not
be aimed at one row: two of the six cards carry no identifier whatsoever. The
only mark-read mechanism that exists is page-level and server-side, fired by
LinkedIn when it serves `/notifications/`, which the server already triggers
with its single `goto` and already declares in `known_side_effects`. That makes
the proposed write not merely forbidden but **unbuildable, and additionally
pointless**: its entire observable effect has already occurred by the time any
control could be clicked, so it would be a mutation that cannot be confirmed
first, cannot be targeted, and cannot change anything the existing READ has not
already changed. The standing `PERMANENTLY_FORBIDDEN` entry is upheld on the
evidence, and this census adds a second independent ground the original entry
did not claim -- absence of a control -- alongside the one it did.

**One caveat the wave should carry, not bury:** the fixture's root is `<main>`
and retains no page header or filter strip, and no other capture in the repo
holds notifications markup, so the absence of a header-level "mark all as read"
is established for the card list and for everything the server can currently
see, but is UNVERIFIED for the live page header. The nearest artefact,
`.../notifications/?action=markAllRead`, exists in this repo only as a BLOCKED
navigation input in `tests/test_readonly.py:432` -- unmeasured against live
LinkedIn, and page-level regardless, so it would not make unread state
addressable even if it worked.
