# The settings addresses exist, and knowing them does not make `allowlist +1` right

**THE HEADLINE, IN THREE LINES.** Seven gap-ledger blockers are each charged
`allowlist +1, WriteSpec`. Two committed audits had already established that not
one of their census rows names an in-product address, so that charge stands for
an unknown. This wave went and got the addresses -- off LinkedIn's own settings
index, at an address already on the allowlist, adding no pattern -- and the
charge is wrong a second time, more deeply: **16 of the 20 addresses that index
draws are refused by a FORBIDDEN SUBSTRING, which an allowlist addition cannot
lift.**

Read-only. No pattern added, no denylist edit, no write fired, no boundary
digest moved. Two commits.

---

## 1. WHAT WAS ALREADY KNOWN, so this document does not re-derive it

`_audit/2026-09-05-settings-tail.md` section 2.3 measured that none of these
rows names an address, and section 2.4 drew the decision procedure. Its own
stated limit is the reason this wave exists:

> I am not asserting which of the seven are in the settings family, because the
> rows do not say **and I did not open the pages**.

`_audit/2026-09-05-profile-rest.md` then took row 78 and row 72 individually,
declined to write a pattern for either, and built
`tests/test_the_settings_boundary_refuses_account_deletion.py` instead.

**Both are right and neither is superseded here.** What follows is the page
load they each declined, plus what it settles.

## 2. THE INSTRUMENT WAS BUILT, ADMITTED, JUSTIFIED, FIRED -- AND ITS ANSWER WAS THROWN AWAY

`readonly.py` admitted `https://www.linkedin.com/mypreferences/d/` on 2026-08-30
in these words:

> A census wants the index -- which sections exist, and whether a section is
> url-addressed or a modal -- and the index is exactly what this admits.

`_audit/2026-08-30-linkedin-writes.md` then read it and recorded: *"33 links, 0
forms and no toggle of any kind -- it is an index."*

**The 33 were counted and never named.** The one output that answers seven rows
was reduced to a cardinal before anybody read it. That is the gap this wave
closed, and it cost one page load at zero boundary change.

Re-read 2026-09-19. **33 anchors again** -- the count reproduces twenty days
later, which is worth more than either reading alone -- of which 20 are distinct
`/mypreferences/` paths. Two absolute readings, never subtracted; identical.
Control needle `easy apply` read 0 on both. The invitation badge was read
immediately before and after, bracketing this page and no other.

## 3. THE TWENTY ADDRESSES, AND THE GATE THAT REFUSES EACH

Pinned in `tests/test_the_settings_index_addresses_are_pinned.py` (5 tests,
shown failing before admission). Measured at allowlist 32, forbidden 33.

| gate | count | addresses |
|---|---:|---|
| allowlist match | 2 | the index itself, `dark-mode` |
| FORBIDDEN SUBSTRING `/mypreferences/d/categories/` | 6 | `account`, `ads`, `notifications`, `privacy`, `profile-visibility`, `sign-in-and-security` |
| FORBIDDEN SUBSTRING `/settings/` | 5 | `autoplay-videos`, `enable-sounds-desktop`, `language`, `preferred-view`, `show-profile-photos` |
| FORBIDDEN SUBSTRING (named, one each) | 5 | `/close-accounts`, `/hibernate-account`, `/unfollow` (`unfollowed`), `verification` (`verifications`), `/connect` (`connected-microsoft-accounts`) |
| **NO PATTERN MATCHES** | **3** | `demographic-info-copy`, `language-for-translation`, `premium-manage-account` |

**THE SPLIT IS THE FINDING.** A refusal by forbidden substring cannot be lifted
by adding an allowlist pattern -- that gate runs before the allowlist loop is
consulted at all. So for 16 of 20 addresses the boundary cost is not
`allowlist +1`; it is *narrow a standing forbidden substring*, which is a far
more expensive and more dangerous edit, and one nobody has costed.

### The blast radius of the obvious shortcut, measured rather than feared

The one edit a future wave would most plausibly make to discharge several
`allowlist +1` rows at once is a family pattern,
`^https://www\.linkedin\.com/mypreferences/d/[a-z0-9-]+/?$`. Applied by
monkeypatch, it admits **exactly three** of the twenty:
`demographic-info-copy`, `language-for-translation`, `premium-manage-account`.
Every denylisted one stays refused.

**A name-based refusal survives a widened allowlist; a shape-based one does
not.** That is asserted now for twenty real addresses, where it was previously
asserted for five hypothetical spellings of one.

### And one correction to the fear, in the safer direction

The standing warning is that a settings-family wildcard would admit six
account-ending spellings, three defended by nothing. Against the addresses
LinkedIn **actually draws**, both account-ending entries -- `/close-accounts`
and `/hibernate-account` -- are denylisted BY NAME and survive the widening.
The singular `/close-account` that nothing names is not a spelling this page
serves. The hazard is real and the existing guard should stay; its live blast
radius is three unruled addresses, not an account-ending one.

## 4. THE SEVEN BLOCKERS, ANSWERED

**None of the twenty addresses is any of the six non-feed subjects.** The index
draws navigation only -- 0 forms, 0 inputs, 0 toggles, 849 chars of text. The
toggles live one level down, under `categories/`, which is denylisted as a
family.

| # | blocker | row(s) | does the address exist? | first blocker, corrected |
|---|---|---|---|---|
| 78 | `OPEN-PROFILE-SETTING` | P B10 | **not on the index.** A toggle under `categories/privacy` or `categories/profile-visibility`, both denylisted | not `allowlist +1` -- either a denylist narrowing or a modal with no address |
| 80 | `ACTIVITY-VIEW-SETTING` | P G2 | **not on the index.** Nearest drawn address `settings/preferred-view` is the site view preference, not the profile Activity section | unidentified surface; MEASURE, not BUILD |
| 86 | `EMBED-SETTING` | M C73 | **not on the index** | unidentified surface; MEASURE, not BUILD |
| 85 | `FEED-PREFERENCES` | M C52 | **YES -- `/mypreferences/d/unfollowed`** | refused by forbidden substring `/unfollow`. An allowlist edit cannot reach it. **Row already closed by a sibling** -- see 5 |
| 72 | `MULTILANG-PROFILE` | P D27, P D28 | **not on the index**; `settings/language` is the UI display language, a different capability | for the READ half, refuted already: the phrase renders on `/in/me/`, an admitted address |
| 87 | `SKILL-PAGE-SURFACE` | N 49 | **not on the index** -- not a settings surface at all | unidentified surface; MEASURE, not BUILD |
| 79 | `LEARNING-CERTIFICATE` | P D29 | **not on the index** -- not a settings surface at all | unidentified surface; MEASURE, not BUILD |

### The `/unfollow` finding sharpens a prior one rather than overturning it

`_audit/2026-09-05-settings-tail.md` reasoned that `FEED-PREFERENCES` is
substring-blocked, using `/feed/follows/` -- a **guessed** address -- blocked by
`/follow`. The real address the product draws is `/mypreferences/d/unfollowed`,
blocked by `/unfollow`. **Same conclusion, different address, different
substring.** The conclusion was right for a reason that was not the real one,
which is worth recording: a guessed address that happens to reach the right
verdict still leaves the row unmeasured.

## 5. WHAT I DID NOT CLOSE, AND WHY

* **No row changed state by my hand.** The counter reads GAP 362 before and
  after. An assignment moves a row between blockers inside one denominator; it
  is not coverage, and reporting it as coverage is the error this census's own
  section 1 warns about.
* **M C52 was moved to MEASURED-ABSENT today by a sibling wave** (`a402c35`, a
  live read of the feed). It is in my assignment's row list and it is **not my
  claim**. My assignment named 8 rows; 7 are live GAP.
* **I did not open any `categories/` page.** That is where the toggles for rows
  78, 80 and 86 most likely live, and every one of them is denylisted. Opening
  one requires narrowing a standing refusal, which is a boundary change with an
  owner and a re-freeze protocol, and is not a measurement to take unilaterally.
* **I built no WriteSpec.** A WriteSpec for a surface whose address nobody has
  is a specification of a guess. Building it to discharge the ledger's
  `WriteSpec` half would have made the cost model look satisfied while leaving
  the row exactly as blocked -- which is the failure mode this wave was warned
  about and is the one thing that would have been worse than doing nothing.

## 6. THE NEXT ARTIFACT, named rather than implied

For rows 78, 80 and 86 the next unit of work is **a ruling, not a build**: does
this server narrow `/mypreferences/d/categories/` to admit one named category
page? That is the operator's, it is a denylist narrowing, and the measurement
that would inform it now exists -- the family has exactly six category pages and
they are enumerated in section 3.

For rows 87 and 79 the next unit is **a page load on a surface nobody has
opened**, and neither is a settings surface, so neither belongs in this blocker
cluster at all.

## 7. PROVENANCE

Commits `65cc1fd` (the guard), `78618f6` (the census assignment). The probe is
`_audit/_scratch/_probe_settings_index_hrefs.py`, untracked by design: it is a
measurement, not an instrument, and promoting it would be a separate deliberate
admission. Its output filter is structural -- settings paths publish verbatim
because no member segment lives under `/mypreferences/`; every other href is
reduced to a count bucketed by its first path segment, and link text never
leaves the page at all.

Guards run after staging, not before: `sweep_tracked_for_identity.py` PASS, 0
hits across 391 files, on both commits.
