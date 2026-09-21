# THE FIELD BESIDE THE MESSAGE: 20 SITES, ADJUDICATED ONE AT A TIME

Wave `the-field-beside-the-message`, 2026-09-21, from `479761e`.

**SUBJECT:** `ExtractionFailedError.url`, published by `server._error` with no
scrubber. The measuring wave (`_audit/2026-09-21-the-landed-url.md`, section
6.1) proved the leak and drove 12 of the 12 `dom.py` sites to their own raise.
**This wave does not re-derive any of that.** It does the thing that audit said
the field needed instead of an edit: a per-site ruling.

No browser was opened. No LinkedIn page was loaded. Everything below is
offline, against the committed tree and fakes.

---

## 0. THE ANSWER, FIRST

    sites feeding ExtractionFailedError.url      20   (my own AST count, section 1)
    WITHHELD -- repaired                         12   every dom.py site
    ASKED_FOR -- published deliberately           7   every server.py site
    PASSTHROUGH -- a relay, ruled by its callers   1   dom.require_rows

**THE SPLIT IS REAL AND IT IS NOT A COMPROMISE.** It falls out of one question
asked twenty times: *at the moment of this raise, does an address THIS SERVER
COMPOSED exist in scope?*

* In `server.py` it always does -- each of the seven raises sits inside a tool
  that built its own url out of `BASE_URL` and either nothing, a closed stage
  token, or digits already proven numeric. Publishing THAT is the field's
  declared contract honoured exactly: *"the operator can open the same page by
  hand"*, and opening the requested address travels the same redirect.
* In `dom.py` it never does. Those twelve are library readers holding a `page`
  and nothing else, and `_url_of(page)` is the only address they can reach.

**AND THE `dom.py` TWELVE HAVE A WORSE PROPERTY THAN "IT IS A LANDING", WHICH
IS THE ARGUMENT THAT DECIDES THEM.** Every one reads `page.url` in an
`except` block entered because `page.evaluate` raised. The production raising
class the measuring wave named is Playwright's *execution context destroyed by
a navigation mid-evaluate*. **On exactly that path, `page.url` is the url of
the page that REPLACED the one being read** -- so the field is not merely
leaking a landing, it is reporting an address that is by construction not the
page the error is about. Both halves point one way.

---

## 1. THE ENUMERATION -- MINE, NOT INHERITED

By AST over `linkedin_server/`, every `url=` keyword argument, with the callee
resolved and the argument unparsed:

| file | function | callee | `url=` argument | count |
|---|---|---|---|---:|
| `dom.py` | 12 readers, listed in section 3 | `ExtractionFailedError` | `_url_of(page)` | 12 |
| `dom.py` | `require_rows` | `ExtractionFailedError` | `url` (its own parameter) | 1 |
| `server.py` | `_read_cards`, `linkedin_notifications` | `require_rows` | `final_url` | 2 |
| `server.py` | `_read_tracker`, `linkedin_job_detail`, `linkedin_followed_companies`, `linkedin_my_profile` | `ExtractionFailedError` | `final_url` | 4 |
| `server.py` | `linkedin_who_viewed_me` | `ExtractionFailedError` | `last_url` | 1 |
| | | | **total** | **20** |

**FOUR MORE `url=` SITES EXIST AND ARE NOT THIS FIELD**, named so that a later
reader who runs the same enumeration and gets 24 knows why: `press.disclose`
x2 pass `url=getattr(page, "url", None)` to `press.evaluate`, which is the
disclosing-press GATE and not an exception; `writes.py` builds two
`_TrackerStage(url=SAVED_LIST_URL/APPLIED_LIST_URL)` records at module level
out of constants.

**THE BRIEF'S LINE NUMBERS HAVE MOVED AND ITS SYMBOLS HAVE NOT.** It cites
`server.py:1074` and `server.py:5327` as the two `require_rows` callers; at
`479761e` they are lines 1074 and **5384**, and the symbols are `_read_cards`
and `linkedin_notifications`. The brief's five direct `server.py` sites are
confirmed by name, all five.

### 1.1 AND ONE OF THE TWENTY IS UNREACHABLE AT HEAD

`_read_cards` takes `allow_empty` and guards its `require_rows` call with
`if not allow_empty:`. **It has exactly ONE caller at `479761e`** --
`linkedin_search_jobs`, through the local `_search_url(place)` -- **and that
caller passes `allow_empty=True`.** So the `require_rows` call inside
`_read_cards` cannot fire from any live path today.

Recorded rather than acted on. It is still ruled, because reachability is not
the question a provenance ruling answers and because the flag is a caller's
argument, one edit from flipping. It also corrects a stale sentence in the
sibling ruling, which describes `_read_cards` and `_read_tracker` as having
"THREE callers"; `_read_cards` has one.

---

## 2. WHAT THE FOURTEEN-ROW RULING ACTUALLY REQUIRES, QUOTED

The standing ruling is `tests/test_the_source_url_split_was_never_ruled.py`,
which governs `source_url` -- the SUCCESS-PATH TWIN of this exact value, in
several of the same functions. Its requirements, in its own words:

**(a) IT FORBIDS THE REFLEXIVE WRAP, IN BOTH DIRECTIONS.**

> **THE FINDING IS THE SPLIT, NOT THE COUNT, AND THE FIX IS NOT TO WRAP THE
> SEVEN.** Wrapping a deliberate publication is as much a defect as leaking an
> accidental one: it silently breaks a tool's contract, and the next reader
> cannot tell which shapers were reasoned and which were reflexive.

and its category-drift test says the same as an executable rule:

> CATEGORY DRIFT FAILS IN BOTH DIRECTIONS. Removing a shaper from a SHAPED
> site is the leak this guards. ADDING one to a PUBLISHES or UNMEASURED site
> is the other defect and is guarded just as hard.

**(b) IT REQUIRES A PER-SITE DECLARATION WITH A STATED REASON**, and it names
the three answers a site may give:

> these write `source_url` and are not declared: ... Decide which it is --
> PUBLISHES (the tool's contract deliberately returns an identifying url),
> SHAPED (incidental, and it goes through a shaper), or UNMEASURED (raw, and
> nobody has measured what that surface emits) -- and say why. Do NOT wrap it
> reflexively.

**(c) THE COUNT IS PART OF THE DECLARATION.**

> The COUNT is part of the declaration so that a NEW emission point added to a
> function that already has one fails here rather than inheriting its
> neighbour's ruling.

**(d) A ROW IS CLOSED BY MEASURING, NEVER BY REASONING ABOUT WHAT A PATH OUGHT
TO BE.**

> **Closing one means MEASURING it** -- landing on the surface and reading what
> the url came back as -- and then moving it to PUBLISHES or SHAPED with the
> measurement cited. Do not close a row by reasoning about what the path ought
> to be.

**(e) IT PINS THE NEUTRAL RELAY AS A CHECKED FACT** rather than a sentence,
because a shaper added inside a relay silently changes every caller:

> ``shape.envelope`` IS DELIBERATELY ABSENT and that is the whole reason this
> file can be written: it passes ``source_url`` through verbatim, so treating
> it as a shaper would mark all four of its call sites safe on the strength of
> the function they call rather than the value they hand it.

**SO THE RULING DOES NOT BLOCK THIS WORK; (b) IS AN INSTRUCTION TO DO IT.**
What it forbids is the twelve-and-seven being wrapped as one gesture. What it
requires is a declaration per site, a reason per site, a count per site, a
relay pinned as a relay, and a check that fails in BOTH directions.

### 2.1 WHERE I OBEY (d) AND WHERE I CANNOT

Requirement (d) is about closing an UNMEASURED row -- moving a value from
"nobody has looked" to "published". **No row here is closed that way.** The
seven `ASKED_FOR` rows are not closed by a claim about where a page lands;
they are closed by changing WHICH VALUE the field carries, from one this
server read off a page to one this server wrote. That is a provenance fact
about the expression, readable in the source, and it is the same ground the
measuring wave's baseline already uses for `readonly.assert_read_url:url`.

**What (d) forbids and I have not done: I have NOT ruled any landing safe on
the strength of what its path ought to carry.** Every landing in this wave is
withheld or removed from the payload. Section 6 carries the one place where a
landing's content is still an open measurement.

---

## 3. THE TWENTY, EACH WITH A VERDICT AND A REASON

Verdict vocabulary IMPORTED from the measuring wave's
`tests/landing_interpolation_baseline.json`, which already rules the MESSAGE
channel with `ASKED_FOR` / `SERVER_CONSTRUCTED` / `WITHHELD` /
`PUBLISHED_BY_CONTRACT` / `NAMES_NO_ADDRESS`, plus `PASSTHROUGH` taken from
the `source_url` ruling's pinned relay. **Nothing here is a second
vocabulary.** Two of the imported verdicts go unused and are named in 3.4
rather than quietly dropped.

The executable form of this table is `tests/test_the_error_url_is_ruled_per_site.py`.

### 3.1 WITHHELD -- 12 sites, all in `dom.py`, all repaired

Every one is the same three lines::

    try:
        data = await page.evaluate(<one module-level script constant>, cfg)
    except Exception as exc:
        raise ExtractionFailedError(f"...: {type(exc).__name__}: {exc}",
                                    url=_url_of(page)) from exc

| # | site | what its `url` held | verdict |
|---|---|---|---|
| 1 | `dom.harvest_linked_cards` | `page.url` at raise time | WITHHELD |
| 2 | `dom.harvest_block_cards` | same | WITHHELD |
| 3 | `dom.read_profile_fields` | same | WITHHELD |
| 4 | `dom.read_surface_census` | same | WITHHELD |
| 5 | `dom.read_self_owned_editor_fields` | same | WITHHELD |
| 6 | `dom.read_self_owned_editor_values` | same | WITHHELD |
| 7 | `dom.read_own_activity_items` | same | WITHHELD |
| 8 | `dom.read_compose_modes` | same | WITHHELD |
| 9 | `dom.read_selected_recipients` | same | WITHHELD |
| 10 | `dom.read_job_insight_panels` | same | WITHHELD |
| 11 | `dom.read_profile_views_insights` | same | WITHHELD |
| 12 | `dom.read_search_appearances` | same | WITHHELD |

**ONE REASON, APPLIED TWELVE TIMES, AND IT IS THE SAME RULING RATHER THAN
TWELVE DECISIONS** -- exactly as the `source_url` ruling treats
`linkedin_connections`'s four sites as *"ONE ruling applied four times rather
than four independent decisions"*. These twelve are textually identical, take
the same argument, and are the same function of their input. Ruling them
separately would be theatre.

**THE REASON.** Three facts, each measurable off the source:

1. **A `dom` reader is handed a `page` and never a url.** There is no address
   in scope that this server composed, so `ASKED_FOR` is not available here --
   not declined, unavailable.
2. **`_url_of(page)` is `page.url` read INSIDE an `except`** entered because
   `page.evaluate` raised. The production raising class the measuring wave
   named is Playwright's *execution context destroyed by a navigation
   mid-evaluate*; on that path `page.url` is the address of the page that
   REPLACED the one being read. **The old field was publishing a string
   LinkedIn chose AND describing the wrong page with it.**
3. **The reproduction affordance was the weakest of the twenty anyway.** These
   raises mean *the reader script did not run*, not *the page was wrong*.
   "Open this url" does not reproduce a reader failure; the exception type in
   the message is the diagnosis.

**THE REPAIR, AND WHY IT IS NOT A WRAP.** `url=` is not passed at all.
`server._error` already omits the key when it is empty, so no edit to the
error envelope was needed -- and **that is the single most important property
of this repair**, because that function is the failure boundary for the whole
package and an uncertified edit to it would be worse than the leak.

The landing is DESCRIBED instead, in `hint`, through one new dom-local helper::

    dom._landing_note(page) -> "the page this reader failed on: " + landing.withheld(_url_of(page))

`landing.withheld` is the shipped mechanism, imported, not re-written. The
descriptor did NOT go into `url`: that field is documented as an address the
operator can OPEN, and a descriptor sentence there would be a type lie that
sends a caller following this server into nonsense.

### 3.2 ASKED_FOR -- 7 sites, all in `server.py`, all published deliberately

| # | site | the address it now publishes | how that address is built |
|---|---|---|---|
| 13 | `server._read_cards` | its own `url` parameter | composed by its one caller, `linkedin_search_jobs._search_url`, as `f"{BASE_URL}/jobs/search/?{urlencode(...)}"` |
| 14 | `server._read_tracker` | local `url` | `f"{BASE_URL}/jobs-tracker/?stage={stage}"` |
| 15 | `server.linkedin_who_viewed_me` | new local `last_requested_url` | the last of two module constants |
| 16 | `server.linkedin_job_detail` | local `url` | `f"{BASE_URL}/jobs/view/{digits}"`, digits already proven numeric and >= 6 long |
| 17 | `server.linkedin_followed_companies` | local `url` | `f"{BASE_URL}/mynetwork/network-manager/company/"` -- a pure constant |
| 18 | `server.linkedin_notifications` | new local `requested_url` | `f"{BASE_URL}/notifications/"` -- a pure constant |
| 19 | `server.linkedin_my_profile` | new local `requested_url` | `f"{BASE_URL}/in/me/"` -- a pure constant |

**WHAT CHANGED IS WHICH VALUE THE FIELD CARRIES, NOT WHETHER IT CARRIES ONE.**
All seven previously published `BROWSER.goto`'s return, and `goto`'s own source
settles what that is -- `return page.url`, with the requested url only as a
fallback when reading `page.url` raises. So all seven were landings.

**THE GROUND FOR PUBLISHING THE REQUESTED ADDRESS IS ALREADY RULED, ONE FIELD
OVER.** The measuring wave's baseline rules `readonly.py:assert_read_url:url`,
`browser.py:goto:url` and `writes.py:assert_write_url:url` as `ASKED_FOR`, on
this reason:

> refuses the url it was HANDED; `test_navigation_is_never_derived` is the
> standing proof that no navigation target is page-derived, so the quoted
> value is one this package or its caller composed

That is the same value class at the same seven sites. Importing the ruling is
what the brief asked for and it is also the only consistent answer: a package
cannot rule a requested navigation target publishable in the message and
unpublishable in the field beside it.

**AND THE CONTRACT IS HONOURED BETTER, NOT MERELY PRESERVED.** The field's
docstring says *"so the operator can open the same page by hand and see what
this server saw"*. Opening the REQUESTED address travels the same redirect
the server travelled and arrives where the server arrived. Opening the LANDED
address skips the navigation that is half the diagnosis.

**THE ONE THING THE SEVEN LOSE, SAID PLAINLY:** the payload no longer says
*where you ended up*. That is smaller than it looks, because the landing class
worth naming is already named upstream: `assert_not_authwall(final_url, ...)`
runs before every one of these seven raises and, since the measuring wave,
refuses with a full `landing.withheld` descriptor. By the time an
`ExtractionFailedError` is raised at these sites the landing has already been
gated and is not an authwall.

#### The site-by-site notes that are NOT the shared reason

* **19, `linkedin_my_profile`, is the sharpest and it was measured, not
  argued.** `/in/me/` lands on `/in/<vanity>/`, and a vanity slug is a name.
  The shipped `tests/test_tools.py::test_a_profile_page_with_no_readable_name_is_a_failure`
  drove exactly that redirect and asserted the resolved slug reached `$.url`.
  **It passed. Its passing was the leak.** Section 5.1.
* **19 also carries an asymmetry nobody had seen**, and it is the finding of
  this wave that is not about the twelve. `source_url` in the SAME function on
  the SUCCESS path is declared **SHAPED** by the fourteen-row ruling. The same
  value, in the same function, was shaped on one branch and raw on the other,
  **because the two branches are ruled by different files and neither file
  knew about the other.** That is what "the failure-path field has no ruling
  at all" looks like from inside one function.
* **15, `linkedin_who_viewed_me`, is the one surface whose own docstring
  records the divergence**: *"The older /me/profile-views/ address now
  redirects to that same page"*. Requested and landed are documented to differ
  here, so this is not a hypothetical. The new local is bound BEFORE the
  navigation deliberately: if `goto` raises, the requested address is still
  the one that was tried.
* **13, `_read_cards`, publishes a url containing the CALLER'S OWN keywords**
  (`_search_url` urlencodes them). That is the caller's string returning to the
  caller, and it is the same open question the measuring wave filed as `D1` --
  *a caller-supplied needle can still be a third party's name*. **Not
  re-litigated here**, because D1 is unruled and covers `browser.goto`,
  `readonly.assert_read_url` and `writes.assert_write_url` identically. A
  ruling on D1 changes all of them at once, and this wave making a private
  exception for one would be the fragmentation `CANONICAL-RULING-ID` forbids.
* **13 is also unreachable at HEAD** (section 1.1). Ruled anyway: a ruling is
  about provenance, and the `allow_empty=True` that makes it dead is one
  caller's argument.
* **16, `linkedin_job_detail`: its MESSAGE is already ruled SERVER_CONSTRUCTED
  in the landing baseline** (`server.py:linkedin_job_detail:BASE_URL`). The
  field beside it now matches, which is the point of doing this per site.

### 3.3 PASSTHROUGH -- 1 site

| # | site | verdict |
|---|---|---|
| 20 | `dom.require_rows` | **PASSTHROUGH** -- writes its own `url` parameter into the exception verbatim |

Pinned exactly as `tests/test_the_source_url_split_was_never_ruled.py` pins
`shape.envelope`, and for its reason:

> treating it as a shaper would mark all four of its call sites safe on the
> strength of the function they call rather than the value they hand it

`require_rows` neither reads a landing nor shapes one, so the verdict belongs
entirely to its two callers -- sites 13 and 18, both now `ASKED_FOR`. The
guard asserts the relay's `url` is still a bare parameter of its own function,
so a `require_rows` that grew a `page` argument and read a landing of its own
would go red rather than silently re-ruling both callers.

### 3.4 THE TWO IMPORTED VERDICTS NOBODY USED, NAMED RATHER THAN DROPPED

`A CATEGORY THAT NEVER FIRES HAS NOT BEEN TESTED, IT HAS BEEN ASSUMED` is the
measuring wave's law and it cuts here too, so:

* **`PUBLISHED_BY_CONTRACT` fires at no site.** It is right for `$.profile` and
  `$.company_url` -- success-path fields with readers that depend on them. **No
  tool in this package declares "my FAILURE names the landing"**, which is why
  that string had no defenders. `ExtractionFailedError.url` has a contract, but
  the contract is *an address the operator can open*, and it is satisfied by
  the requested one.
* **`NAMES_NO_ADDRESS` fires at no site here.** Its one real instance is
  `dom.JOB_HREF`, a regex that spells `href`, and it lives in the message
  census rather than this field.

Because a verdict this table cannot use would be dead weight, neither is
declared in the guard. What the guard DOES declare and this section does not
count is `NO_ADDRESS_IN_SCOPE`: **12 further `ExtractionFailedError` sites in
`dom.py`** -- the selector builders (`named_role_selector` x2,
`save_control_selector`, `follow_control_selector`, `unfollow_control_selector`,
`settings_radio_label_selector`, `post_submit_selector`,
`compose_recipient_selector`, `compose_send_selector`,
`comment_submit_selector`, `escaped_needle`, `_typeahead_selector_named`).
Not one takes a page or a url; they are pure string builders and could not
publish an address if they tried. **They are declared so the guard's subject is
the whole feeder population rather than the leaking subset** -- a `url=` added
to one of them tomorrow arrives undeclared and goes red. They are NOT part of
the twenty and this document never counts them as such.

---

## 4. `$.message` AND `$.hint` -- WHAT I TOUCHED AND WHAT I DID NOT

### 4.1 `$.message` -- NOT TOUCHED, AND IT IS A DIFFERENT DECISION

Every one of the twelve `dom.py` messages is
`f"could not read the X page: {type(exc).__name__}: {exc}"`. The re-run probe
still reports `inner_needle_at: ['$.message']` **at all twelve** -- a needle
planted only inside the exception `page.evaluate` raised still arrives at
`$.message`. **That channel is open and this wave did not close it.**

It is a different decision for three reasons, and none of them is effort:

1. **THE PROVENANCE IS A THIRD PARTY'S, WHICH IS THE ONE CASE THIS PACKAGE HAS
   NO SAY IN.** `{exc}` is composed by Playwright or the standard library. The
   census puts this bucket at **89 sub-expressions**, 86 of them under
   `except Exception`. A remedy here is not a per-site ruling at all -- it is a
   policy about how this package renders foreign exception text, and it reaches
   far outside these twenty sites.
2. **THE ONLY MEASURED READING POINTS THE OTHER WAY FOR THE NAVIGATION CASE.**
   The measuring wave read Playwright's own driver source and found both
   navigation-failure templates interpolate the REQUESTED url, not the landing.
   That is a source reading over two templates out of a bundle -- it does not
   clear the other 87 -- but it means the obvious severity argument is not
   established, and a repair that rests on an unestablished premise is the
   thing this repository keeps paying for.
3. **THE HONEST REMEDY IS TYPE-ONLY, AND IT IS A REFUSAL THIS PACKAGE ALREADY
   KNOWS HOW TO WRITE.** `press.disclose` does it: *"ONLY THE EXCEPTION TYPE. A
   library's message is composed by code nobody here controls and has been
   measured carrying selectors and urls."* Applying that to twelve reader
   messages deletes the diagnosis those messages exist for, and whether that
   trade is worth making is a ruling, not an edit. **RECOMMENDED AS THE NEXT
   WAVE**, with `press.disclose` as its worked precedent and the 89-site census
   as its denominator.

### 4.2 `$.hint` -- TOUCHED AT THE TWELVE, DELIBERATELY NOT AT `linkedin_my_profile`

**TOUCHED:** the twelve `dom.py` sites had no hint; they now carry
`_landing_note(page)`. Everything it can emit is a literal from `landing.py`,
an integer or a boolean, and that is driven rather than asserted --
`test_the_landing_note_publishes_no_character_the_site_chose` plants a
`/in/<slug>/` authwall landing and requires the slug absent AND the note still
informative.

**NOT TOUCHED:** `linkedin_my_profile`'s
`hint=f"headings seen: {[s.get('heading') for s in sections]}"`, the one
page-derived hint in the package. The measuring wave drove it and found the
needle at `$.hint`; `scrub` removes only paths, so page text passes through.

**IT IS LEFT PUBLISHED, ON PURPOSE, AND THE REASON IS THE FOURTEEN-ROW RULING
RATHER THAN CAUTION.** The same list is published on this tool's SUCCESS path
as `headings_seen`, and `tests/test_tools.py` asserts it there
(`assert "Analytics" in completeness["headings_seen"]`). So it is the tool's
own contract, and wrapping it would break that contract on one branch while
leaving it standing one branch away -- *"the next reader cannot tell which
shapers were reasoned and which were reflexive"*. The section headings of the
operator's OWN profile are also not a third party's text.

**WHAT WOULD CHANGE MY ANSWER, SAID SO THE ROW CAN BE REOPENED:** a measurement
showing `dom.read_profile_fields` returning a heading that carries a person's
name rather than a section label. `linkedin_my_profile` reads `/in/me/`, so a
heading here is the operator's own page furniture -- but nobody has censused
what headings that surface actually draws, and that is a page measurement this
wave could not take.

---

## 5. THE RULING, STATED ONCE SO IT CAN BE CITED

`CANONICAL-RULING-ID` requires every ruling to have ONE id and every citation
to resolve to a SYMBOL rather than to a re-derived phrase, so this wave's
decision is written here once and registered in `_audit/RULINGS.md` as
`ERROR-URL-ASKED-FOR-OR-NOTHING`. Every code comment this wave left cites that
id's document.

**RULED: the error envelope's url field carries the address this server ASKED
FOR, or it carries nothing at all.** A landing -- `page.url`, or
`BROWSER.goto`'s return, which is the same string -- is never published there,
because it is a value the remote site chose and `server._error` publishes that
field with no scrubber. Where a requested address exists in scope, publishing
it is REQUIRED and not merely permitted: the field is a reproduction
instruction and a tool that withheld it would break a declared contract to buy
nothing. Where no requested address exists, the key is omitted and the landing
is DESCRIBED in the hint through `landing.withheld`, whose alphabet is closed.
**A descriptor never goes into the url field**, which is documented as an
address the operator can open.

---

## 6. THE CONTROLS -- FAILING FIRST, THEN PASSING

### 6.1 THE SHIPPED TEST THAT ASSERTED THE LEAK, AND ITS INVERSION

`tests/test_tools.py::test_a_profile_page_with_no_readable_name_is_a_failure`
shipped driving `/in/me/` with `redirect_map={PROFILE_ME_URL: PROFILE_RESOLVED_URL}`
and asserting `result["url"] == PROFILE_RESOLVED_URL` -- **that the vanity
landing reached the caller.** It passed on the unrepaired tree, alongside six
other url-contract tests:

    venv/Scripts/python -m pytest tests/test_tools.py -q \
        -k "profile_page_with_no_readable_name or empty_page_is_extraction_failed \
            or both_profile_view_pages or notification_failure_names_the_selector"
      -> 7 passed, 117 deselected in 2.39s        [BEFORE the repair]

**ITS PASSING WAS THE LEAK**, and after the repair it went red -- the
leak-closed proof arriving as a failure, exactly as the measuring wave's
`test_the_shipped_authwall_refusal_publishes_the_slug_it_bounced` did:

    FAILED tests/test_tools.py::test_a_profile_page_with_no_readable_name_is_a_failure
    E   AssertionError: assert 'https://www....in.com/in/me/' == 'https://www....om/in/alex-r/'
    E     - https://www.linkedin.com/in/alex-r/
    E     + https://www.linkedin.com/in/me/
    1 failed, 760 passed

**IT IS INVERTED, NOT DELETED.** Deleting it would have removed the only test
that ever demonstrated the defect. The inversion asserts the requested address
POSITIVELY -- `result["url"] == PROFILE_ME_URL` -- rather than only that the
slug is gone, because **an absence assertion on its own passes on a refusal
that publishes nothing**, and flipping an assertion to an absence is precisely
where that trap is set. Beside it,
`test_that_assertion_convicts_the_payload_that_actually_shipped` hands the same
two assertions the pre-repair payload and requires them to convict.

The other six url-contract assertions were UNCHANGED and still pass, which is
the half that shows the seven `ASKED_FOR` rows kept their contract:
`test_an_empty_page_is_extraction_failed_not_a_fake_empty_success` asserts
`result["url"] == expected_url` across four tools with the comment *"the
operator must be able to look himself"*, and those four expectations are
already the CONSTANTS this server requests.

    venv/Scripts/python -m pytest tests/test_tools.py -q
      -> 125 passed in 5.07s                       [AFTER, with the inversion]

### 6.2 THE STANDING GUARD, SHOWN FAILING ON THE STATE THAT SHIPPED

`scripts/_check_the_error_url_ruling_can_fail.py` restores the pre-repair
spelling by substitution IN MEMORY -- nothing written to `linkedin_server/` --
and requires the guard to convict every row. **The mutation is the real
previous state, so no argument is needed that it is representative.**

    the plant restores the spelling that shipped at 479761e

    1. THE TREE AS IT STANDS -- every declared row must be GREEN
       rows checked 31, rows red 0

    2. THE PLANT -- substituted in memory, never on disk
       dom.py     hint=_landing_note(page),  -> url=_url_of(page),  replaced 12 (declared 12)
       server.py  url=url,                   -> url=final_url,      replaced  4 (declared  4)
       server.py  url=requested_url,         -> url=final_url,      replaced  2 (declared  2)
       server.py  url=last_requested_url,    -> url=last_url,       replaced  1 (declared  1)

    3. WHAT THE PLANT DOES TO EACH DECLARED ROW
       rows planted 19
       CONVICTED    19
       ACQUITTED    0

    4. THE ROWS THE PLANT DOES NOT TOUCH MUST STAY GREEN
       untouched rows 12, wrongly red 0

    PASS -- 31 rows green on the tree, all 19 convicted by the plant,
            12 untouched rows unaffected

**SECTION 4 IS THE HALF THAT STOPS THIS BEING A RUBBER STAMP.** A control that
convicts everything convicts nothing, so the plant must leave the twelve
`NO_ADDRESS_IN_SCOPE` rows and the relay green. It does.

**AND IT RUNS THE GUARD'S OWN CODE, NOT A COPY.** The per-verdict rules live in
`ruling.verdict_violations`, which the test parametrises over and this script
imports. Two copies of one rule drift and the drift is invisible in exactly
the direction that matters -- the measuring wave's words about its own census.

**NO EXTERNAL TOOL IS CONSULTED.** Rebuilding the previous state by
substitution rather than by `git show` means there is no outage to misreport as
an absence -- the failure `test_an_outage_is_never_filed_as_an_absence` caught
in a sibling instrument yesterday. If a pattern stops matching, the declared
count is short and the script fails saying so.

### 6.3 THE REGISTERED PROBE, RUN BEFORE AND AFTER

`scripts/_probe_dom_error_url_field.py` is the measuring wave's instrument,
IMPORTED rather than re-implemented. It drives all twelve `dom.py` readers to
their own raise by making `evaluate` fail for ONE script chosen by identity,
asserts `reached` from the TRACEBACK, and hunts two needles.

    BEFORE   12 rows, 12 reached, url_needle_at ['$.url'] x12,
             inner_needle_at ['$.message'] x12, voided_by []
    AFTER    12 rows, 12 reached, url_needle_at []       x12,
             inner_needle_at ['$.message'] x12, voided_by []

**THE `$.url` COLUMN IS THE REPAIR AND THE `$.message` COLUMN IS SECTION 4.2.**
The probe's own controls held in both runs.

### 6.4 THE NEW GUARD'S OWN CONTROLS

`tests/test_the_error_url_is_ruled_per_site.py` -- 45 tests, of which nine are
controls over synthetic module sources never written into `linkedin_server/`:
the leak direction, the wrap direction, a bare `page.url`, a loop-bound
landing, a relay that stopped relaying, an undeclared site, the describer and
feeder names existing, and `test_there_are_sites_to_rule_on`. Two are DRIVEN --
`_landing_note` against a planted authwall landing carrying a slug, and the
round trip through the real `server._error` -- and each has its positive
control beside it, because *"the slug is not in the note"* would pass on a
helper that returned `""`.

    venv/Scripts/python -m pytest tests/test_the_error_url_is_ruled_per_site.py -q
      -> 45 passed in 12.78s

### 6.5 A REGISTERED INSTRUMENT PRODUCED A FALSE FINDING ON THIS WAVE'S OWN EDIT

Worth more than the green, so it is recorded rather than smoothed over.

The repair added a 38-line helper above the twelve raises. The probe's
`TARGETS` table carried each raise's LINE, frozen at commit `a29c281`, and
compared it against the traceback inside an 8-line window. **Nine of the twelve
rows came back `wrong_site`** -- a verdict that reads as *the probe reached the
wrong raise* and was in fact *dom.py grew*. Nothing had moved except line
numbers, and the three rows that stayed `reached` were the three sites ABOVE
the inserted helper.

> A LINE CITATION DOES NOT ROT INTO A DANGLING REFERENCE. IT ROTS INTO A
> PLAUSIBLE WRONG ANSWER, WHICH STOPS THE READER INSTEAD OF SENDING THEM
> LOOKING.

Repaired in place: `_expected_raise_lines()` resolves each reader's raise from
the source at run time through the probe's own AST census, and a reader whose
raise cannot be located UNIQUELY gets `line_unresolved`, which is added to the
probe's `voided_by` rather than compared against a guess. **Filling in "the
first one" would have been a guess wearing a measurement's clothes.** The
control count in that function's docstring moved from three to four.

**THIS IS AN EDIT TO ANOTHER WAVE'S REGISTERED INSTRUMENT AND IT IS DECLARED
AS SUCH.** It was made because leaving nine false `wrong_site` rows in the
instrument for this field -- rows my own edit caused -- would poison the next
reader of the only probe that measures it.

---

## 7. THE IMPACT GATE -- IT WIDENED, SO THERE IS NO `NOT CHECKED` LINE

Staged first, then run. **The impact set crossed the threshold and the gate
widened to the full suite, so it printed the widening notice and no
`NOT CHECKED` line at all** -- which is the case the brief asked to be reported
if it happened. Verbatim:

    + 15 CORPUS-WIDE guard(s), run unconditionally -- they sweep the tracked set and take no input from the diff,
      so no impact analysis can ever select them. Omitting them is how a fast gate ships a real name.

    WIDENING TO THE FULL SUITE, because the impact set is 168 of 206 test files (82%), at or above the 45% line where running everything costs about the same and answers more.

**WHY IT WIDENED IS WORTH A SENTENCE**: `linkedin_server/dom.py` and
`linkedin_server/server.py` are the two most-imported modules in the package,
so a diff touching both reaches 82% of the suite by imports alone. A scoped
gate has nothing to scope here, and it says so rather than pretending.

### 7.1 THE FIRST RUN REFUSED, AND THE THREE REDS WERE MINE

    REFUSED: a test this change can reach is RED.
        FAILED tests/test_the_audit_index_is_derived.py::test_the_committed_index_is_what_the_corpus_derives
        FAILED tests/test_the_audit_index_is_derived.py::test_there_is_a_corpus_and_the_index_covers_all_of_it
        FAILED tests/test_the_rulings_register_is_derived.py::test_the_committed_register_is_what_the_corpus_derives
        3 failed, 7900 passed, 8 skipped, 1 xfailed in 954.92s (0:15:54)

All three are the same cause and they named their own remedy: **this document
is a new `_audit/` file and both indexes are GENERATED**, so adding it made
them stale.

    _audit/INDEX.md drifted from the corpus at line 30.
      committed: | audit documents git tracks under `_audit` | 211 |
      derived  : | audit documents git tracks under `_audit` | 212 |
    Run: python scripts/build_audit_index.py --write

Regenerated with the two committed generators; the diff is purely additive --
one row for this document, the tracked count 211 -> 212, and the register's
unscanned-signal counts moving because this document contains ruling-shaped
prose. `rulings registered` stays at 34 until the entry in section 5 lands,
which is in this commit.

---

## 8. WHERE DISK DISAGREED WITH THE BRIEF

Every one of these is small, and they are recorded because the instruction was
to trust disk and say so.

1. **THE BRIEF'S LINE NUMBERS ARE STALE; ITS SYMBOLS ARE EXACT.** It names
   `server.py:1074` and `server.py:5327` as the two `require_rows` callers. At
   `479761e` they are 1074 and **5384**, and the symbols are `_read_cards` and
   `linkedin_notifications`. Every symbol the brief names -- the twelve
   `dom.py` readers, `dom.require_rows`, and the five direct `server.py`
   raises -- is confirmed by my own AST count. **The count of 20 is exactly
   right.**

2. **THE SAME ENUMERATION RETURNS 24 IF YOU ASK IT FOR `url=` KEYWORDS**, and
   four of those are not this field: `press.disclose` passes
   `url=getattr(page, "url", None)` TWICE into `press.evaluate`, the
   disclosing-press gate, and `writes.py` builds two `_TrackerStage` records
   from constants at module level. A later reader who gets 24 and expects 20
   has not found a discrepancy.

3. **ONE OF THE TWENTY IS UNREACHABLE AT HEAD.** `_read_cards` guards its
   `require_rows` behind `if not allow_empty:` and its ONE caller passes
   `allow_empty=True`. Ruled anyway; section 1.1.

4. **THE SIBLING RULING CARRIES A STALE SENTENCE.** It describes `_read_cards`
   and `_read_tracker` as internal helpers whose landed url is "whatever their
   THREE callers supplied". `_read_cards` has one caller at `479761e`. **Not
   edited** -- that file is the `source_url` ruling and changing its prose from
   a wave whose subject is a different field is how a ruling gets quietly
   amended by a neighbour. Named here for its owner.

5. **THE TWO AST CENSUSES IN THIS REPOSITORY DISAGREE ABOUT `enclosing`.**
   `scripts/_probe_dom_error_url_field._argument_census` builds its owner map
   with `owner.setdefault(...)` walking from module level, so the OUTERMOST
   function wins; `tests/test_the_source_url_split_was_never_ruled._enclosing`
   deliberately takes the INNERMOST, saying *"several of these sit in nested
   helpers and the outer name would misattribute them"*. **Harmless for the
   twelve** -- all are top-level functions with one raise each, which is why
   nobody has met it -- and a real divergence waiting for the first nested
   raise. My own walk takes innermost. Named, not fixed in the probe.

6. **THE PROBE'S PAYLOAD REPORTS A COMMIT IT NO LONGER RUNS AT.** Its output
   carries `"commit": "a29c281"` as a frozen literal; this wave ran it at
   `479761e`. That is the same class of defect as the frozen line table I did
   repair in the same file, one field over. **NOT CHANGED**: correcting it to
   today's sha makes it stale again on the next commit, and resolving it
   honestly needs a decision about where that truth comes from -- and I had
   already edited another wave's instrument once, for a defect I caused.
   Recorded for its owner rather than churned.

**NOTHING IN THE BRIEF'S SUBSTANCE WAS WRONG.** The defect, the 20, the
reachability argument, the three-channel picture and the severity framing all
held against the tree.

---

## 9. INSTRUMENTS

| path | disposable? |
|---|---|
| `linkedin_server/dom._landing_note` | shipped code -- one importable home for the twelve, so the class closes for readers nobody has written |
| `tests/test_the_error_url_is_ruled_per_site.py` | **REGISTER** -- the per-site declaration, nine synthetic controls both directions, two driven controls with their positive halves, and a pinned headline count |
| `scripts/_check_the_error_url_ruling_can_fail.py` | **REGISTER** -- shows the guard convicting the state that actually shipped, 19 of 19, and shows the plant leaving the 12 untouched rows green |
| `scripts/_probe_dom_error_url_field.py` | **REGISTER, AMENDED** -- expected raise lines now RESOLVED from source instead of frozen; a reader that cannot be located uniquely voids the run |
| `scripts/build_rulings_index.py` | shared generator -- one `Ruling` row added, `ERROR-URL-ASKED-FOR-OR-NOTHING` |
| `_audit/2026-09-21-the-field-beside-the-message.md` | this document |

**DISPOSABLE, DECLARED AS SUCH:** three throwaway enumerators lived only in
the session scratchpad and are not committed -- a `url=` keyword lister, a
feeder-call lister, and a probe-output summariser. Each exists inside a
committed instrument in a better form, which is why none was harvested.

---

## 10. THE LEDGER LINE

One field, twenty sites, three verdicts. **Twelve withheld, seven published
deliberately, one relay** -- and the split is the finding, not a compromise: a
`dom` reader is handed a page and never an address, and a `server` tool always
composed its own.

**THE NUMBER WORTH KEEPING IS 12 AND NOT 20.** A wave that wrapped all twenty
would have closed the same leak and overturned a standing ruling by side
effect, on weaker evidence than made it -- and nobody reading the result a
month later could have told which of the twenty were reasoned.

**THE SHARPEST SINGLE FACT IS THAT THE SUITE ALREADY ASSERTED THE LEAK.**
`test_a_profile_page_with_no_readable_name_is_a_failure` drove `/in/me/`
through its redirect and required the resolved vanity slug to reach `$.url`.
It was green every day it existed. Beside it, in the same function, the
success path's twin of that value is declared **SHAPED** by a different ruling
in a different file. **The same value, in the same function, shaped on one
branch and raw on the other, because the two branches were ruled by two files
and neither knew about the other.** That is what an unruled field looks like
from the inside, and it is the argument for the register entry more than for
the repair.

**WHAT IS STILL OPEN AND IS NAMED, NOT SMUGGLED:** `$.message` carries the
browser's own exception text at all twelve sites and still does -- measured,
`inner_needle_at: ['$.message']`, twelve of twelve, after the repair. That is
a third party composing the string, 89 sub-expressions package-wide, and the
remedy `press.disclose` already uses -- report the exception TYPE and nothing
else -- deletes diagnosis the messages exist for. It needs a ruling and a
denominator, which is the next wave, not an edit at the end of this one.

## 11. THE ONE THING I DECIDED NOT TO DO, WITH THE ARGUMENT FOR IT

**Should the seven `ASKED_FOR` sites ALSO describe where they landed?** They
could: `hint=... + landing.withheld(final_url)` costs nothing in leak terms,
because the descriptor's alphabet is closed, and it would restore the one
thing the repair takes away -- the payload no longer records that a redirect
happened.

**NOT DONE, AND THE REASON IS NOT CAUTION.**

1. **The landing class worth naming is already named, upstream.**
   `assert_not_authwall(final_url, ...)` runs before every one of the seven
   raises and, since the measuring wave, refuses with a full descriptor. What
   remains is a non-authwall redirect on a page that then failed to render
   rows, where the redirect is not the diagnosis.
2. **It is additive scope on a repair that is already certified**, and four of
   the seven hints are one fixed English sentence that tests may read.
   *Adding is cheap, feels like rigour, and is indistinguishable from progress
   from the inside*, which is exactly when it should be a separate decision.

**THE ONE SITE WHERE I THINK THE ANSWER IS PROBABLY YES**, named so the next
wave does not have to rediscover it: `linkedin_who_viewed_me`. Its own
docstring says `/me/profile-views/` redirects to the analytics page. After
this repair, a both-attempts-failed payload reports
`url: https://www.linkedin.com/me/profile-views/`, and an operator who opens
it lands somewhere else and may conclude the server read the wrong surface.
One `landing.withheld(last_url)` in that hint would say *you were redirected,
to a route of this class* in literals. **That is a one-line change with a
real argument and it belongs to whoever takes the `$.message` wave**, beside
the other decision about what this package's failures are allowed to say.

## 12. MASTER IS RED, AND IT IS NOT THIS WAVE. MEASURED, THEN THE MERGE WAS ABORTED

The brief said to re-check `git log master..HEAD` before freezing. That check
earned its place twice over.

**MASTER HAD MOVED FOUR COMMITS** while this wave ran, landing the
`the-compound-rows` wave: `826798a`, `5ab40c7`, `2d41db8`, `e5ba6c5`. This
wave's own certification was taken BEFORE that:

    full suite at 479761e + this wave    PASS, 7912 tests, 0 failed, 687.6s

### 12.1 THE MERGE, AND WHAT IT COST TO RESOLVE

Merged locally to see what would happen. Two files conflicted and they are the
two that cannot be hand-resolved:

    _audit/INDEX.md                 CONFLICT
    _audit/RULINGS.md               CONFLICT
    scripts/build_rulings_index.py  auto-merged, both Ruling rows intact

Both conflicting files carry **GENERATED. Do not hand-edit.**, so there is
exactly one correct resolution and it is not a resolution: **take either side
to clear the markers, then REGENERATE, then `--check`.** Hand-merging two
derivations yields a file matching neither corpus, which that file's own drift
guard then convicts. Done that way it came out clean -- 213 tracked documents,
36 rulings, all anchors resolving.

**RECORDED FOR WHOEVER MERGES THIS**, because it will recur on every wave that
writes an audit document while another one does.

### 12.2 AND THEN THE GATE REFUSED, ON A TEST THIS WAVE DOES NOT TOUCH

    REFUSED: a test this change can reach is RED.
        FAILED tests/test_the_blocker_reason_locator_states_its_recall.py
               ::test_recall_against_a_hand_built_set_does_not_regress
        1 failed, 2354 passed, 3 skipped in 202.34s

    E  6 of 9 hand-found documents are in the top 3, below the floor of 7

**FOUR EXPERIMENTS, AND THE FOURTH IS THE ONE THAT SETTLES IT.** Each is the
same single test, run with one thing removed from the working tree and then
restored:

| what was removed | result |
|---|---|
| this wave's audit document | **still RED** |
| the compound-rows wave's audit document | **still RED** |
| both new audit documents together | **still RED** |
| **master's 19-line addition to `_audit/2026-09-21-the-write-ceiling.md`**, with this wave's every file left in place | **GREEN** |

**SO THE RED IS `e5ba6c5`'s, AND THIS WAVE CONTRIBUTES NOTHING TO IT.** The
same conclusion arrives from the other side: the full suite was green at
`479761e` + this wave, 7912 tests, and that run included this test.

### 12.3 THE MECHANISM, AND THE TEST PREDICTED IT IN WRITING

`scripts/find_blocker_reason.py` ranks documents per blocker. Measured:

    GROUPS-SURFACE
      1. (11) _audit/2026-09-05-groups-surface-measured.md
      2.  (9) _audit/2026-09-03-linkedin-gap-blockers.md
      3.  (7) _audit/2026-09-21-the-write-ceiling.md     <-- grown by e5ba6c5
      4.  (7) _audit/2026-09-19-groups-admission.md      <-- hand-found, TIED

**THE HAND-FOUND DOCUMENT DID NOT LOSE ON SCORE. IT LOST A TIE AT 7-ALL**, and
the tie-break is reverse-lexicographic on the path, so the LATER DATE IN THE
FILENAME WINS. `2026-09-21-...` beats `2026-09-19-...` for no reason connected
to relevance.

That guard's own docstring names this exact failure mode, one wave earlier:

> **THE SHAPER DOCUMENT FELL OUT OF THE TOP 3 ON A TIE, NOT ON MERIT.** [...]
> So a `top3` floor is sensitive to an ARBITRARY TIE-BREAK whenever a new
> document lands on an existing score -- which is a property of this
> measurement nobody had written down, and it is the reason the corpus growing
> can look exactly like the locator getting worse. The floor stays at 7 and is
> not lowered: lowering it would have hidden the tie instead of naming it.

**THE GUARD IS WORKING AS DESIGNED.** Its author chose to let it go red rather
than lower the floor, precisely so a human would look. This is the human
looking, and the reading is: the locator has not got worse, the corpus grew
into a second tie, and the tie-break is arbitrary.

### 12.4 WHAT I DID NOT DO, AND WHY

**THE MERGE WAS ABORTED AND THIS BRANCH IS HANDED BACK AT `479761e` + one
commit, gate-green.** Three things were available and two are wrong:

| option | verdict |
|---|---|
| lower `RECALL_TOP3_FLOOR` to 6 | **REFUSED** -- the file says in writing that lowering hides the tie instead of naming it, and the locator did not get worse |
| change the tie-break to path-ascending | **REFUSED** -- that fixes this instance and is exactly as arbitrary; which document should win a tie is a ruling nobody has made, on an instrument this wave does not own |
| commit the merge with `--no-verify` | **REFUSED** -- a bypassed gate on somebody else's red buries the signal inside my merge commit, and a red branch cannot be serially verify-merged anyway |
| **abort, stay green, report the cause with the reproduction** | **TAKEN** |

**THE DECISION THE LEAD OWNS**, stated so it is not rediscovered: master is red
at `e5ba6c5` on `test_recall_against_a_hand_built_set_does_not_regress`, the
cause is a 7-7 tie broken by filename date, and the fork is (a) rule the
tie-break, (b) move the floor with a reason, or (c) change the metric so
growth cannot look like regression. **Nothing merges cleanly until one of
those is chosen**, and that is true of every wave in flight, not only this one.

---
