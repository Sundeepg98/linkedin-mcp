# Newsletter code-path inventory

Read-only inventory of every newsletter-touching code path shipped in this
repository, as of this worktree's checkout. Purely factual: no judgment
calls, no recommendations. Cited by symbol name, not line number (line
numbers were used only as a research aid and are not quoted below except
where a piece of shipped prose itself names a line number as content).

Person names appearing in fixtures/tests are synthetic; per instruction they
are written below as `<person-name>` / `<member-slug>` rather than
reproduced verbatim, even though the source files themselves state plainly
that the values are invented.

All finding are VERIFIED by direct reading of the file in this worktree,
or by running the shipped predicate through the worktree's own venv
interpreter, except where marked UNVERIFIED.

---

## 1. `linkedin_server/newsletters.py` -- every module-level constant and function

Module docstring frames this file as the reader for a page opened once, on
2026-09-05, with the capture kept at a gitignored path; it explicitly says
the file's predecessor wave shipped the shape layer and the address but
deliberately shipped no reader.

### Module-level constants (6 total: 5 public, 1 private)

- `SUBSCRIPTIONS_URL: str = "https://www.linkedin.com/mynetwork/network-manager/newsletters/"`
  -- the one address this module's reader is meant to be run against. Comment
  states it was admitted to the read allowlist on 2026-09-05 and MEASURED to
  be SERVED (as opposed to redirected) the same day.

- `ANCHOR_SELECTOR: str = 'a[href*="/newsletters/"]'` -- the Playwright
  locator string for "every anchor whose href mentions the product." Comment
  states this is deliberately the widest possible aim (a substring match, not
  a CSS class, not a position), because the page's classes are hashed build
  artefacts.

- `HEADING_WORD: str = "newsletters"` -- the control text the reader matches
  against every `h1, h2, h3` on the page before counting anchors, so a zero
  reading can be told apart as "the account has no subscriptions" vs. "the
  aim/instrument is wrong."

- `HEADING_SELECTOR: str = "h1, h2, h3"` -- where the heading control looks.

- `PARAGRAPH_SELECTOR: str = "p"` -- selects the paragraphs inside one row
  anchor; the reader takes the FIRST such paragraph as the title, a choice
  the docstring says is measured (not assumed) via an independent-witness
  comparison against the slug.

- `_NORMALISE = re.compile(r"[^a-z0-9]+")` (private) -- strips everything but
  letters/digits, used to compare a title against a slug on equal footing.

### Functions (2 total)

**`title_matches_slug(href: Optional[str], title: Optional[str]) -> Optional[bool]`**

Returns `True` if the normalised title is a prefix of the href's final path
segment (the slug), `False` if it computably is not, and `None` if the
question could not be put at all (empty title, or an href with no final
segment after stripping a query string and trailing slash). Refuses to leak
any fragment of either input -- the return type is deliberately a bare bit
(`True`/`False`/`None`) and nothing else; the docstring calls this "the
assertion that the measurement is still true," i.e. a live control on the
"first paragraph is the title" design choice, not a convenience function.

**`async def read_newsletter_subscriptions(page: Any) -> dict[str, Any]`**

Takes an already-opened Playwright `page` (no navigation, no press -- the
caller owns reaching `SUBSCRIPTIONS_URL` and the invitation-badge obligation
that address inherits from `/mynetwork/`). Reads the heading control, then
every `ANCHOR_SELECTOR` match, dedupes by href (stripped of query string and
trailing slash), drops the "illustration" anchors (same href, no paragraph
text at all -- this is what turns ten/eleven anchors into five newsletters),
and shapes each surviving row through `shape.subscription_row`, attaching a
`title_matches_slug` flag to each row. On any exception during the read, it
resets to an all-zero/empty state and reports the exception's class and
message but interpolates neither a title nor an href back into the message.

Return dict, exact keys, quoted from the docstring and cross-checked against
the code:

```
{
  "rows": [...],            # one shape.subscription_row per DISTINCT href
  "heading_seen": int,      # the control -- see HEADING_WORD
  "anchors": int,           # every anchor matching the product
  "anchors_without_text": int,
  "distinct": int,          # THE SUBSCRIPTION COUNT
  "published": int,
  "titles_matching_slug": int,
  "titles_unmatched": int,
  "error": str | None,
}
```

On the exception path specifically, only `error`, `rows` (`[]`),
`heading_seen` (`0`) and `anchors` (`0`) are guaranteed reset; the other
numeric keys (`anchors_without_text`, `distinct`, `published`,
`titles_matching_slug`, `titles_unmatched`) are left at the dict-literal's
initial `0` from `out`'s construction, since the `try` block returns early
before reassigning them -- i.e. every key is always present in both the
success and exception shapes, all still integers/None, none omitted.

---

## 2. Every OTHER `linkedin_server/` module mentioning "newsletter" (case-insensitive)

Confirmed by `grep -rli` over the whole package: exactly the 12 modules named
in the brief, no others. (`newsletters.py` itself is the 13th hit and is
covered in section 1.)

- **`dom.py`** -- enclosing symbol: module-level constant
  `INVITATION_BADGE_HREF`. The comment above that constant is a historical
  diagnosis: the invitation-badge aim used to require a trailing slash, which
  made it match nothing, because the ONE `/mynetwork` control that trails
  with a slash on the live feed is the (unlabelled) newsletters nav link, not
  the badge. Purely explanatory; `dom.py` contains no newsletter-specific
  code of its own.

- **`events.py`** -- enclosing symbol: the module docstring (top-of-file,
  lines 1-89 in this checkout). Cites `newsletters.py` once, as precedent for
  splitting a module out of `dom.py` rather than adding to it, to avoid a
  multi-writer-tree commit hazard. No functional connection.

- **`feed.py`** -- two distinct touch points, both inside the module
  docstring/data, not inside `dom.py`-style live code:
  - The module docstring (lines 1-196 in this checkout) mentions "newsletter"
    four times: once citing a defect class ("a newsletter title of the form
    `<publication> by <author>` passed through [`census_substitute`]
    INTACT"), once in a measured-count table ("newsletter 10" out of 217
    resolved authors across a 1353-anchor corpus scan), once naming
    `/newsletters/<...> -> "newsletter"` as one of six href-to-kind mappings,
    and once citing "the reason the newsletter wave gave for declining
    [a DOM reader]" as the precedent for this module also not shipping one.
  - The module-level dict `_KIND_FOR_SEGMENT` contains the literal entry
    `"newsletters": "newsletter"`, one of six path-segment-to-kind-word
    mappings (`in`->member, `company`->company, `newsletters`->newsletter,
    `school`->school, `groups`->group, `events`->event) that `author_kind()`
    (the function itself does not mention "newsletter" in its own body) uses
    to resolve a feed author's href to a published kind word, never an
    identifier.

- **`groups_page.py`** -- enclosing symbol: function `interpret_zero`. Its
  docstring cites "the newsletter tool" precedent (i.e.
  `read_newsletter_subscriptions`'s `heading_seen` field) as the model for
  why THIS function exists: to say whether a zero group-membership count is a
  fact about the account or a fact about the reader.

- **`page_plugin.py`** -- enclosing symbol: the module docstring. Cites
  `readonly.py`'s newsletter finding ("a slug is ROUTINELY ITS AUTHOR'S
  NAME") as precedent for why this module refuses a Page's vanity slug
  entirely rather than trying to shape it.

- **`premium.py`** -- three touch points, all inside the module docstring or
  the docstring of `async def read_premium_surface`:
  - Module docstring, twice: once naming
    `newsletters.read_newsletter_subscriptions` alongside
    `events.read_events_home` as the two siblings this module copies the
    "opens nothing, navigates nowhere" shape from; once citing
    `newsletters.py` (with `events.py`) as precedent for shipping as a
    standalone module rather than adding to a contended `dom.py`.
  - `read_premium_surface`'s own docstring cites
    `newsletters.read_newsletter_subscriptions`'s per-read error-tolerance
    discipline ("a control that cannot be read is skipped, not fatal") as the
    model this function's control-scanning loop follows.

- **`press.py`** -- enclosing symbol: module-level tuple constant
  `_COMPOSER_MARKERS`. This is a FUNCTIONAL (non-docstring) hit: the tuple's
  six entries are address fragments that mark a composer/editor, refused for
  *pressing* even on an address admitted for *reading*, and one entry is the
  literal string `"/newsletter/new"` (singular "newsletter", no trailing
  slash -- note this is a different spelling from the plural
  `/newsletters/...` used everywhere else in this inventory). See section 8
  for how this string relates to a fixture href that contains it as a
  substring.

- **`readonly.py`** -- all mentions (21 in this checkout) sit inside the
  single tuple `_ALLOWED_URL_PATTERNS` (module-level, lines 152-1336 in this
  checkout), which is one long, heavily-commented allowlist. Two distinct
  regions:
  - An early comment block (attached to the `/in/me/details/interests/`
    entry) explains that Groups, Newsletters and Schools "had never been
    asked about" before a probe measured all three shipping a name verbatim
    past both census guards, and separately states "The newsletter addresses
    stay closed" (written before the entry below existed).
  - The actual admission: `re.compile(r"^https://www\.linkedin\.com/mynetwork/network-manager/newsletters/?$")`,
    preceded by a long comment (roughly 95 lines) that (a) explains the
    address was found by accident while diagnosing the invitation-badge aim
    in `dom.py`, not designed for; (b) names
    `tests/test_newsletter_route.py` as the fixture-backed assertion that
    pins the spelling; (c) explicitly lists four addresses this admission
    deliberately does NOT cover -- a single newsletter's own page (slug
    form), the bare `/newsletters/` product root, per-newsletter analytics,
    and any query string on the admitted root; (d) notes creating a
    newsletter (`/newsletters/create/`) is refused twice over (by the
    forbidden-substring gate AND by no pattern admitting it); (e) notes the
    admission inherits the same pending-invitation-badge obligation as its
    `/mynetwork/` siblings, discharged by the caller, not by this list.

- **`recommendations.py`** -- two touch points, both in module-level
  docstring/comment prose, neither in code that runs:
  - Module docstring names "newsletter" as one of the five sibling entity
    kinds `shape._CENSUS_ENTITY_HREFS` also carries alongside the member
    marker this module derives locally.
  - A comment attached to the module-level constant
    `PUBLISHED_HREF = "<a recommender>"` says `groups.py` and (verbatim, as
    written in this file) "`newsletter.py`" publish a marker-shaped literal
    because their surfaces have a safe identifier shape to gesture at; this
    module's own literal deliberately does not even resemble an href. Note:
    the comment's own spelling is the singular `newsletter.py`, not the
    actual module name `newsletters.py` -- reported here exactly as written,
    not corrected.

- **`search_results.py`** -- four functional (non-docstring) touch points, in
  a family of closed-vocabulary/table constants that all treat "newsletter"
  the same way `/company/`, `/groups/`, etc. are treated -- as one ordinary
  search vertical, nothing special-cased:
  - `RESULT_KINDS: tuple[str, ...]` -- contains `"newsletter_result"`, one of
    14 closed output tokens.
  - `RESULT_TABLE: tuple[tuple[str, str, str, str], ...]` -- contains the row
    `("newsletter_result", "search", "results", "newsletters")`, one of 10
    segment-equality mappings from a 3-segment URL path to a result kind.
  - `def control_fixture() -> str` -- returns a fixed HTML string used as a
    test fixture; one of its 14 anchors is
    `'<a href="/search/results/newsletters/">h</a>'`.
  - `CONTROL_EXPECTATION: dict[str, int]` -- the fixture's predicted tally;
    contains `"newsletter_result": 1`.

- **`shape.py`** -- the module that `newsletters.py` actually delegates
  shaping to. Relevant symbols:
  - `_CENSUS_NEWSLETTER_PATH = re.compile(r"/newsletters/[A-Za-z0-9\-_%.]+/?")`
    -- one of the census path-substitution patterns; substituted to the
    literal `/newsletters/<newsletter>/` inside the general-purpose
    `census_shape`-family functions.
  - `_SUBSCRIPTION_HREF_MARKER = "/newsletters/<newsletter>"` -- "the one
    entity marker a newsletter subscription row is allowed to be about,"
    derived (comment's words) from `_CENSUS_ENTITY_HREFS` rather than
    hand-copied, so a marker added there tomorrow becomes a refusal here
    automatically.
  - `_SUBSCRIPTION_FOREIGN_MARKERS = tuple(marker for marker in _CENSUS_ENTITY_HREFS if marker != _SUBSCRIPTION_HREF_MARKER)`
    -- every other entity marker, i.e. anything that isn't a newsletter is
    "foreign" to this row.
  - `_SUBSCRIPTION_PUBLISHED_HREF = _SUBSCRIPTION_HREF_MARKER + "/"` -- the
    ONE literal href string ever published by a subscription row
    (`"/newsletters/<newsletter>/"`), never a shape of the actual input.
  - `_SUBSCRIPTION_TITLE_COUNT = 1` -- the constant count handed to
    `census_redact_rare`, justified as "not a trick to force redaction" but
    the actual tally (a member subscribes to a given newsletter once).
  - `def subscription_row(href: Optional[str], name: Optional[str]) -> dict[str, Any]`
    -- the function `newsletters.read_newsletter_subscriptions` calls per
    row. Refuses (returns `published: False`) when: the href is empty
    (`refused: "no_href"`); the shaped href carries any OTHER entity marker,
    e.g. a member's own newsletter-authoring tab
    (`refused: "href_identifies_another_kind_of_entity"`); or the shaped href
    carries no newsletter marker at all (`refused: "not_a_newsletter_href"`).
    Every refusal carries `saw: [...]`, the markers actually matched. On
    success it returns
    `{"published": True, "href_shape": "/newsletters/<newsletter>/", "name": <redacted-or-passthrough>, "name_redacted": bool}`.
    The docstring states its one designed difference from the sibling
    `membership_row`: a newsletter title is redacted UNCONDITIONALLY (through
    `census_shape` + `census_redact_rare` at the fixed count of 1) because,
    unlike a group name, a newsletter's title/slug routinely IS a person's
    name and the ordinary identity substitutions cannot see a plain human
    name. It documents its own known residual limitation: the redactor is a
    capitalised-run rule, not a name detector, so a title that spells its
    author in lower case survives unredacted -- stated as a measured finding,
    not a bug to silently fix.

---

## 3. MCP tools in `linkedin_server/server.py` that read or report on newsletters

All 45 tools in this file are registered with a bare `@mcp.tool()` decorator
(no `name=` argument anywhere -- confirmed: `grep -c "^@mcp.tool"` = 45,
`grep -n "@mcp.tool("` finds no instance with an argument), so the registered
tool name is the decorated function's own name in every case, including the
one below.

**Primary tool: `linkedin_newsletter_subscriptions`**

- Registered name: `linkedin_newsletter_subscriptions`
- Dispatches to: `newsletters.read_newsletter_subscriptions` (via
  `linkedin_server.newsletters`, imported as `newsletters`)
- Takes no parameters, returns `dict[str, Any]`.
- Behaviour: loads the feed first and reads the pending-invitation badge
  (BEFORE), then navigates to `newsletters.SUBSCRIPTIONS_URL` and reads the
  badge again (AFTER, off the newsletters page's own nav -- no third
  navigation). Refuses (via a shared `_badge_refusal` helper) in three
  distinct conditions: the BEFORE badge could not be read (nothing is spent
  in this case -- the newsletters page is never opened), the AFTER badge
  could not be read, or the badge value MOVED between the two reads. Only if
  none of those fire does it call `newsletters.read_newsletter_subscriptions`
  and return its reading.
- Exact returned dict keys, by branch:
  - Success:
    `ok, redirected, pages_loaded, badge_before, badge_after` plus every key
    `newsletters.read_newsletter_subscriptions` returns, merged in via
    `**reading`: `rows, heading_seen, anchors, anchors_without_text,
    distinct, published, titles_matching_slug, titles_unmatched, error`.
  - Badge refusal (`_badge_refusal(...)`):
    `ok (always False), error, why, badge_before, badge_after, pages_loaded`.
  - Uncaught-exception path (`_error(exc)`): if `exc` is a
    `LinkedInReaderError`, `error (exc.kind), message`, plus `url` and/or
    `hint` if the exception carried them; otherwise
    `error ("unexpected"), message`.
- The docstring states explicitly that this tool avoids the verb
  "subscribing" in its own headline because
  `test_no_docstring_claims_a_write` reads that phrasing as a read tool
  advertising a write, and says this fired on the first draft of the
  docstring.

**Secondary, non-data mentions** (report ABOUT the tool, do not read
newsletter data themselves):

- `linkedin_group_memberships` (dispatches to `groups.membership_tally`,
  unrelated function) -- its OWN docstring names
  `linkedin_newsletter_subscriptions` explicitly, as the contrasting sibling
  that WITHHOLDS its answer on a moved invitation-badge counter, to explain
  why `linkedin_group_memberships` instead REPORTS a moved counter rather
  than refusing (its address is not under `/mynetwork/`, so a moved counter
  there is not evidence this tool's own load spent anything). This is
  asserted by two tests -- see section 5,
  `test_the_tool_has_no_refusal_branch_and_that_is_deliberate` and
  `test_the_sibling_that_DOES_refuse_still_does` in
  `tests/test_the_groups_tool_keeps_its_properties.py`.
- `linkedin_server_info` (a general server self-description tool, returning a
  large `dict[str, Any]` built up across roughly 600 lines and trimmed by a
  helper `_trim_info(full, verbose)`) -- inside a nested
  `writes_sanctioned_but_not_performed.known_side_effects` list entry (prose,
  not a dedicated key), it names `linkedin_newsletter_subscriptions` alongside
  `linkedin_connections` as the two tools that load addresses UNDER
  `/mynetwork/` and both discharge the pending-invitation-badge obligation by
  refusing when they cannot certify it. This tool does not itself return any
  newsletter-specific field; it is a one-line mention inside a much larger,
  general-purpose self-audit payload.

No other `@mcp.tool()`-decorated function in this file mentions "newsletter"
anywhere in its own source (confirmed: every "newsletter" hit in
`server.py` falls within the module docstring, the `import` line, a
changelog-style comment block above the tool definitions, or inside one of
the three functions named above).

---

## 4. `CENSUS_SURFACES` and `test_every_census_surface_prices_itself.py`

**No newsletter surface appears in `CENSUS_SURFACES`.** Directly confirmed by
reading the entire dict body (module-level `dict[str, str]`, 12 keys):
`feed, profile, profile_edit_intro, settings, settings_dark_mode,
post_composer, article_composer, messaging_compose, premium,
search_appearances, groups, events`. A direct `grep -i newsletter` scoped to
just this dict's line range returns zero matches. No key contains the
substring "newsletter" and no value/URL in the dict references a newsletter
address.

This is consistent with the comment trail elsewhere in the same file and in
`readonly.py`: the newsletter surface's census rows were deliberately filed
against a DIFFERENT surface (the profile's Interests tab) rather than given
their own `CENSUS_SURFACES` entry, on the argument (stated, not re-derived
here) that the Interests tab is where LinkedIn draws the newsletters
category control -- even though that same commentary elsewhere notes the
Interests tab is itself dead twice over (a render gate, and a redirect).

**`test_every_census_surface_prices_itself.py` and `newsletter_composer`:**
the name `newsletter_composer` is NOT a real, shipped census surface. It
appears exactly once in this test file, inside
`test_a_new_surface_without_a_cost_is_caught`, as a SYNTHETIC/simulated
addition used only to prove the pricing-guard test itself can fail when it
should:

```python
def test_a_new_surface_without_a_cost_is_caught():
    """SHOWN FAILING, against a simulated addition rather than a real edit.
    ...
    """
    surfaces = set(server.CENSUS_SURFACES) | {"newsletter_composer"}
    priced = set(server.CENSUS_SURFACE_COST)
    unaccounted = surfaces - priced - set(BELIEVED_FREE)
    assert unaccounted == {"newsletter_composer"}, (
        "a newly added surface with no cost and no free-declaration was not "
        "flagged, so this guard would not catch the case it exists for."
    )
```

In words: the test unions the REAL `CENSUS_SURFACES` key set with one fake
key, `"newsletter_composer"`, that exists only in this test's local variable
and nowhere in shipped code; it then asserts that the "unaccounted" set
(surfaces minus priced-in-`CENSUS_SURFACE_COST` minus declared-free-in-
`BELIEVED_FREE`) is EXACTLY that one fake key -- proving the guard notices an
unpriced surface rather than silently passing. It is a control fixture value
chosen to sound like a plausible future tool name, not evidence that a
"newsletter composer" surface or tool exists anywhere in this repository.

---

## 5. Test files under `tests/` mentioning "newsletter" (case-insensitive)

24 files (of the ~172 top-level `test_*.py` files; `tests/` is flat --
`fixtures/` and `__pycache__/` are the only subdirectories, handled in
section 6). For each: file, total test-function count (`grep -c "^def
test_\|^async def test_"`), and the specific test function(s) whose own body
or immediate parametrize data concerns newsletters (attribution done via a
Python `ast` walk per function, not by textual proximity, so a module-level
data table between two functions is correctly reported as module-level
rather than attributed to whichever `def` happens to appear earlier in the
file).

### Files where the word appears ONLY at module level (no test function's own body concerns newsletters)

- **`test_a_correction_is_findable_from_the_claim.py`** (9 tests) -- appears
  once, inside a large module-level tuple of known-true-negative
  correction/evidence pairs, as descriptive prose identifying "Newsletter
  analytics" as a `profile.md` census-slice row while describing an
  unrelated cross-reference; no test function is newsletter-specific.

- **`test_a_sanitiser_earns_its_entry.py`** (8 tests) -- appears four times,
  all inside a module-level enumeration dict of "enrolled sanitiser"
  script/function pairs and its surrounding comments; registers the entry
  `("_probe_newsletter_subscriptions_live.py", "_relation"): TWO_ARG`. The
  actual test functions iterate this whole table generically; none is
  newsletter-specific.

- **`test_blocker_map_is_derived.py`** (7 tests) -- all six hits sit inside a
  long module-level historical/changelog comment reconciling a "blocker map"
  derivation, citing `NEWSLETTER-SURFACE` as one of several census-row
  families whose row counts were reconciled; not inside any test function.

- **`test_company_page_boundary.py`** (15 tests) -- one hit, in the module
  docstring, citing `test_newsletter_route.py` as a precedent file for "the
  widening ships the test asserting its own limits."

- **`test_readers_outside_dom_are_a_pinned_inventory.py`** (6 tests) -- three
  hits, all in the module docstring/comments, historically recording that
  `linkedin_newsletter_subscriptions` was one of three tools once on this
  file's "unwired reader" pinned inventory before being wired on
  2026-09-05; the inventory is now empty and none of the file's 6 test
  functions is newsletter-specific.

- **`test_readonly_boundary_invariant.py`** (9 tests) -- 19 hits, all inside
  module-level comment blocks that mirror `readonly.py`'s own
  `_ALLOWED_URL_PATTERNS` commentary (including a byte-for-byte attribution
  ledger for a shadowed dict); none of the file's 9 test functions
  references "newsletter" in its own body.

- **`test_school_and_collections_boundary.py`** (12 tests) -- one hit, module
  docstring, same precedent-citation pattern as
  `test_company_page_boundary.py`.

- **`test_the_tool_surface_is_pinned_so_a_row_must_move.py`** (3 tests) --
  one hit: the literal string `"linkedin_newsletter_subscriptions"` as one
  entry of a module-level pinned mapping (tool name -> allowed AST node
  types, `()` meaning none) that a test function iterates generically; not
  inside a test function body itself.

### Files with at least one test function that concerns newsletters

- **`test_analytics_creator_boundary.py`** (6 tests) --
  `test_the_address_this_reading_informs_is_still_refused`: asserts that
  `https://www.linkedin.com/analytics/creator/newsletters/` (alongside
  `/search/results/people/`) is NOT accepted by the read boundary, as a
  negative control proving a same-day widening for creator-content analytics
  did not also, by accident, admit the newsletter-analytics page next door.

- **`test_connections_reader.py`** (38 tests) --
  `test_the_pre_fix_badge_aim_finds_nothing_on_the_live_spelling`: rebuilds
  the OLD (pre-2026-09-04) invitation-badge CSS selector and asserts it
  resolves to zero matches against the live-shaped fixture, because the only
  trailing-slash `/mynetwork/` anchor the page actually draws is the
  unlabelled newsletters nav link, not the badge; the newsletters link here
  is purely the confounding control object, not the thing under test.

- **`test_every_census_surface_prices_itself.py`** (6 tests) -- see section 4
  in full for `test_a_new_surface_without_a_cost_is_caught`.

- **`test_every_tool_is_on_the_surface.py`** (4 tests) --
  `test_both_rules_reject_the_registry_that_was_actually_measured`: its real
  assertions concern `linkedin_who_viewed_me` (must be registered) and
  `_attach_recipient_ids` (must NOT be registered as a tool); "newsletter"
  appears only inside an inline historical comment inside this same function
  body, chronicling that `linkedin_newsletter_subscriptions` was one of
  three tools whose wiring moved the pinned tool count from 38 to 41 -- not
  a distinct assertion about newsletters.

- **`test_membership_row.py`** (20 tests) -- this file's subject is GROUPS
  membership rows (`shape.membership_row`), and newsletters appear only as
  sibling/contrast data:
  - `test_an_event_href_is_recognised_as_naming_an_entity`: asserts an EVENT
    href shapes correctly; mentions "newsletter" only in its docstring, as
    historical context (commit `fa1a1ba` added group/newsletter/school
    markers together on 2026-09-04).
  - `test_the_other_four_entity_kinds_still_redact_and_two_controls_survive`:
    asserts six entity-bearing hrefs (event, group, member, company, a
    newsletter href, school) are all recognised as identifying an entity,
    and two ordinary non-entity addresses (feed, jobs search) are not; a
    newsletter href is one of six positive-control inputs, not the subject.
  - `test_a_group_named_after_a_person_SHIPS_ITS_NAME_and_that_is_asserted`:
    asserts a deliberately-recorded GROUP-naming defect; credits "the
    newsletter wave" only as the wave that found this hole (in its own
    surface) on 2026-09-05.
  - `test_redacting_unconditionally_would_blank_the_payload_not_just_the_leak`:
    asserts unconditional redaction would blank legitimate GROUP names;
    contrasts this with `subscription_row`'s (the newsletter shaper's) own
    unconditional redaction being safe, because a newsletter title keeps a
    readable shape afterward.
  - (Module-level, not a test function: the `MUST_REFUSE` data table used by
    a separate, generic parametrised refusal test contains the row
    `("https://www.linkedin.com/newsletters/a-made-up-letter/",
    "href_identifies_another_kind_of_entity", ["/newsletters/<newsletter>"])`
    as one of five foreign-entity-kind refusal fixtures.)

- **`test_newsletter_reader.py`** (15 tests) -- the dedicated end-to-end
  suite for `newsletters.read_newsletter_subscriptions` and
  `title_matches_slug`, run against a real headless Playwright page loaded
  with `tests/fixtures/synthetic/newsletter_subscriptions.html`. All 15:
  1. `test_the_fixture_draws_more_anchors_than_rows_which_is_why_distinct_exists`
     -- independent regex cross-check: the fixture has 11 newsletter-shaped
     hrefs but only 5 distinct ones.
  2. `test_it_publishes_distinct_newsletters_and_not_anchors` -- asserts
     `error is None`, `anchors == 11`, `distinct == 5`,
     `anchors_without_text == 5`, `len(rows) == 5`: the headline assertion
     that the reader answers 5, not 10/11.
  3. `test_the_heading_control_reads_the_word_and_not_the_position` --
     asserts `heading_seen == 1` even though an unrelated advertisement
     section in the fixture also draws its own `h2`.
  4. `test_no_row_publishes_a_title_as_written` -- asserts no published row's
     `name` ever contains the synthetic person's first or last name
     substring.
  5. `test_the_person_shaped_title_comes_back_redacted_with_its_shape_intact`
     -- asserts at least one row is redacted via `shape.CENSUS_REDACTED` and
     that a redacted name can still contain the literal `" by "` substring
     (the redaction keeps its "authored by" shape rather than blanking it).
  6. `test_the_lower_case_title_survives_and_that_is_the_declared_floor` --
     asserts the literal lower-case title `"data weekly"` survives
     unredacted, documenting the known capitalised-run-only limitation.
  7. `test_an_uncertifiable_title_is_opaque_rather_than_emitted` -- asserts
     `shape.CENSUS_OPAQUE` appears among published names (a title the
     charset/length gate cannot certify).
  8. `test_a_members_own_newsletter_tab_is_refused_and_names_what_it_saw` --
     asserts exactly one row is refused with
     `refused == "href_identifies_another_kind_of_entity"`, a non-empty
     `saw`, and `published == 4` (5 minus the refused one).
  9. `test_the_aiming_control_fires_on_the_row_whose_paragraphs_are_swapped`
     -- asserts the title/slug aiming control fails on exactly one
     PUBLISHED row (the one whose paragraphs were deliberately swapped in
     the fixture) and that 2 rows total are "missed" (that one plus the
     already-refused member's-tab row).
  10. `test_the_control_separates_absent_from_false` -- direct unit test of
      `title_matches_slug`: `True` for a match, `False` for a mismatch,
      `None` for an empty title or an empty href.
  11. `test_the_control_returns_a_bit_and_never_a_fragment_of_its_input` --
      asserts the return value is always `True`, `False`, or `None`, never
      any other type.
  12. `test_zero_rows_with_the_heading_present_is_a_fact_about_his_account`
      -- hand-built HTML with the heading but no rows: asserts
      `heading_seen == 1`, `distinct == 0`.
  13. `test_zero_rows_with_no_heading_is_a_fact_about_the_instrument` --
      hand-built HTML with neither heading nor rows: asserts
      `heading_seen == 0`, `distinct == 0` (same numeric zero as #12, opposite
      meaning).
  14. `test_rows_without_the_heading_still_read_because_the_control_is_not_a_gate`
      -- hand-built HTML with a row anchor but no heading: asserts
      `heading_seen == 0` yet `distinct == 1`, `published == 1` (the heading
      check never suppresses a real row).
  15. `test_a_page_that_cannot_be_evaluated_reports_the_class_and_the_message`
      -- a fake `page` whose `.locator()` raises `RuntimeError("frame was
      detached")`; asserts `error == "RuntimeError: frame was detached"` and
      `rows == []`, `distinct == 0`, `heading_seen == 0`.

- **`test_newsletter_route.py`** (8 tests) -- the dedicated boundary-and-page
  test file for the newsletters allowlist entry. All 8:
  1. `test_the_newsletters_root_is_admitted_in_both_slash_forms` (2
     parameters) -- asserts `readonly.assert_read_url` does not raise for
     the root with and without a trailing slash.
  2. `test_the_anchoring_is_the_whole_of_the_permission` (9 parameters, from
     module-level tuple `MUST_STAY_REFUSED`) -- asserts `assert_read_url`
     DOES raise for 9 related addresses: a specific newsletter's own page
     (both slug forms), the bare `/newsletters/` product root, per-newsletter
     analytics, the `/analytics/newsletter/` alias, a query-string variant
     and a sub-path variant of the admitted root, `/mynetwork/` itself, and a
     member's own newsletter-authoring tab.
  3. `test_creating_a_newsletter_is_refused_by_BOTH_gates_and_the_count_matters`
     -- asserts `/newsletters/create/` raises, and that the exception message
     contains both `"/create"` and the literal `"AND NO READ PATTERN"`,
     proving it is refused by two independent gates, not one.
  4. `test_the_admitted_root_carries_NO_forbidden_substring_so_the_pattern_is_alone`
     -- asserts none of `readonly._FORBIDDEN_URL_SUBSTRINGS` match the
     lowercased newsletters root, with a sibling URL used as a control that
     the substring-check mechanism itself still fires on some input.
  5. `test_MUTATION_removing_the_pattern_refuses_the_route` -- removes (via
     monkeypatch) the one `_ALLOWED_URL_PATTERNS` entry whose pattern
     contains the needle `"network-manager/newsletters"`, asserts exactly one
     pattern was removed, and then asserts the root is refused with it gone.
  6. `test_a_page_linkedin_served_carries_exactly_this_address` -- asserts
     the tracked capture `tests/fixtures/connections_list.html` contains the
     literal newsletters-root string, and that `assert_read_url` accepts it.
  7. `test_the_capture_carries_the_link_ONCE_and_as_an_anchor` -- asserts
     that fixture contains exactly one `<a href="...">` for that exact
     address.
  8. `test_the_capture_does_NOT_carry_a_subscription_row_and_that_is_the_finding`
     -- asserts that SAME fixture contains ZERO hrefs shaped like a
     per-newsletter row (`/newsletters/<slug>/`), with a control regex
     proving the zero is real; states explicitly that no test in this file
     may be cited as evidence about what the actual newsletters PAGE
     contains, only that the nav link to it exists.

- **`test_no_committed_document_defers_to_an_ignored_path.py`** (3 tests) --
  `test_the_guard_does_not_fire_on_these` (parametrised over 4 example
  paragraphs): one parameter cites
  `` `_audit/_scratch/_probe_newsletter_refreeze_attribution.py` `` as a
  provenance citation, and the test asserts this "committed document defers
  to an ignored path" guard produces ZERO offenders for all 4 paragraphs --
  i.e. an ordinary citation of a gitignored script must not be flagged as a
  violation.

- **`test_no_committed_identity.py`** (18 tests) --
  `test_every_shape_can_actually_fail` (parametrised over many synthetic
  planted-PII strings): one parameter is the email address
  `"somebody+newsletter@a-real-company.co.uk"`, used purely as a
  plus-tagged-address regression control for the generic email-shape
  detector (guarding against an over-broad exemption for addresses with no
  alphanumeric local part). The word "newsletter" here is incidental filler
  text inside a synthetic email local-part and has no connection to the
  newsletter feature.

- **`test_page_text_is_never_printed.py`** (6 tests) -- both hits are
  module-level: one is descriptive prose ("the exact shape the newsletter
  probe uses to report a title") inside a docstring, the other is a
  module-level comment noting that `newsletters.py` and
  `_probe_newsletter_subscriptions_live.py` are deliberately absent from a
  named list (of files that DO leak page text) -- i.e. cited as a clean
  example, not a violation. No test function itself is newsletter-specific.

- **`test_server_surface.py`** (46 tests) --
  `test_the_surface_is_exactly_the_fortyfive_tools`: its module-level
  `EXPECTED_TOOLS` set (which this test compares the live registry against)
  contains the literal string `"linkedin_newsletter_subscriptions"` as one of
  exactly 45 pinned tool names; the test function's own body/docstring
  additionally carries historical commentary (not a distinct assertion)
  noting this tool arrived as one of three added together on 2026-09-05
  evening.

- **`test_subscription_row.py`** (12 tests) -- the dedicated mutation-testing
  suite for `shape.subscription_row` itself (module docstring: "The
  per-record gate a newsletter reader needs, and the three ways to break
  it"). All 12 test this one function, most directly with newsletter-shaped
  inputs:
  1. `test_a_subscription_row_publishes_a_constant_href_and_never_the_input`
     -- asserts `href_shape == "/newsletters/<newsletter>/"` always, never
     the input slug.
  2. `test_a_title_with_no_capitalised_run_survives_intact` -- control:
     asserts a title with no capitalised run survives unredacted.
  3. `test_a_title_carrying_its_author_is_redacted_and_keeps_its_marker` --
     asserts an author-carrying title is redacted AND still contains
     `shape.CENSUS_REDACTED`.
  4. `test_a_title_the_charset_gate_cannot_certify_comes_back_marked` --
     asserts a 300-character title comes back as `shape.CENSUS_OPAQUE`, with
     a control confirming ordinary titles are unaffected.
  5. `test_a_bare_member_token_in_the_query_never_reaches_the_output` --
     asserts a member token riding in a newsletter href's query string never
     appears in the row's `repr()`.
  6. `test_a_row_with_no_href_is_refused_and_says_so` -- generic (non-
     newsletter-specific input): asserts an empty href is refused with
     `refused == "no_href"`.
  7. `test_a_refusal_reports_the_markers_it_saw_rather_than_a_bare_no` --
     generic: asserts a COMPANY href through the same gate is refused with
     `saw == ["/company/<company>"]`.
  8. `test_MUTATION_publishing_the_shaped_href_ships_the_query_token` --
     plants replacing the constant published href with a shaped copy of the
     input, and asserts a query token would then leak into `href_shape`.
  9. `test_MUTATION_dropping_the_foreign_markers_publishes_a_members_own_tab`
     -- plants emptying the foreign-markers tuple and asserts a member's own
     newsletter-authoring tab then gets published instead of refused.
  10. `test_MUTATION_making_the_redaction_conditional_ships_the_author_verbatim`
      -- plants the sibling `membership_row`'s conditional-redaction rule in
      place of this function's unconditional one, and asserts the author's
      surname then ships verbatim.
  11. `test_MUTATION_a_sixth_entity_marker_becomes_a_refusal_not_a_hole` --
      generic derivation test: adds a synthetic sixth entity marker and
      asserts the foreign-markers set (rebuilt) picks it up automatically
      while still excluding the newsletter marker itself.
  12. `test_the_redactor_is_a_caps_run_rule_and_NOT_a_name_detector` --
      asserts a lower-case author name (`"notes by <person-name>"`) survives
      the redactor unredacted, as a documented, measured, accepted
      limitation.

- **`test_the_events_boundary_is_root_only.py`** (3 tests) --
  `test_the_events_root_is_still_admitted_in_both_slash_forms`: tests the
  EVENTS root, not newsletters; cites "the reason the newsletter guard
  states" in its own docstring as the precedent for asserting both slash
  forms.

- **`test_the_groups_tool_keeps_its_properties.py`** (25 tests) -- 3
  functions cross-check the groups tool (`TOOL = "linkedin_group_memberships"`)
  against the newsletter tool by parsing `server.py`'s AST directly:
  - `test_the_tool_has_no_refusal_branch_and_that_is_deliberate` -- asserts
    (via `ast.walk`) `linkedin_group_memberships` contains no `if` statements
    and calls no `_badge_refusal`; its docstring cites
    `linkedin_newsletter_subscriptions` as the sibling that DOES refuse, and
    explains why the groups tool deliberately does not.
  - `test_the_sibling_that_DOES_refuse_still_does` -- the control for the
    above: directly parses `linkedin_newsletter_subscriptions` and asserts it
    DOES call `_badge_refusal`, proving the contrast is real rather than "the
    helper stopped existing."
  - `test_the_reason_for_the_asymmetry_is_written_where_it_is_made` --
    asserts `linkedin_group_memberships`'s own docstring contains both
    "newsletter" and "mynetwork" (case-insensitive), i.e. the ruling must be
    written where a reader of that tool will actually see it, not only in an
    audit file.

- **`test_the_wired_readers_keep_their_properties.py`** (12 tests) -- 2
  functions parse `linkedin_newsletter_subscriptions` directly via AST:
  - `test_the_newsletter_tool_refuses_on_every_badge_condition` -- asserts
    the function contains EXACTLY 3 `return _badge_refusal(...)` call sites
    (unreadable-before, unreadable-after, moved).
  - `test_the_helper_is_not_on_the_tool_surface` -- asserts `_badge_refusal`
    itself carries no decorator (so it cannot have silently become a tool),
    and that `linkedin_premium_status`, `linkedin_newsletter_subscriptions`,
    and `linkedin_notify_cost_precondition` each still carry their
    `@mcp.tool()` decorator.

- **`test_urn_substitution_covers_the_class.py`** (9 tests) --
  `test_the_consumers_of_this_predicate_are_the_ones_that_were_considered`:
  maintains a pinned enumeration of every consumer of the shared urn/entity
  substitution predicate; `("shape.py", "subscription_row")` is one pinned
  entry (added as a ninth consumer on 2026-09-05). The surrounding comment
  documents that adding this consumer forced a re-audit which caught
  `subscription_row` originally calling the predicate twice, with the second
  call unsafely publishing raw substitution output on a per-record path --
  since fixed to route the title through `census_shape` (the same
  substitutions plus a length/charset gate) instead.

---

## 6. Fixture files under `tests/fixtures/` (including `synthetic/`) whose CONTENT mentions "newsletter"

Exactly 2 of 22 tracked `.html` fixtures (confirmed by `grep -rli` over
`tests/fixtures/`):

### `tests/fixtures/connections_list.html`

- Size: 7727 bytes.
- `href` attributes containing "newsletter": exactly 1.
- Distinct value: `https://www.linkedin.com/mynetwork/network-manager/newsletters/`
- This is a TRACKED CAPTURE (a real page LinkedIn served, per
  `test_newsletter_route.py`'s own docstring), not a synthetic fixture; the
  newsletters link appears on it only because LinkedIn's Manage-my-network
  nav renders on every page in that family, and it is the fixture
  `test_newsletter_route.py` reads to prove the allowlist pattern matches a
  spelling LinkedIn actually serves.

### `tests/fixtures/synthetic/newsletter_subscriptions.html`

- Size: 12234 bytes.
- Its own header comment states plainly: "SYNTHETIC. NOT A CAPTURE" --
  structure measured off a live page on 2026-09-05, content invented.
- `href` attributes containing "newsletter": 13 total, across 6 distinct
  values:
  - `/article/newsletter/new/` -- 2 occurrences (both a "Create a newsletter"
    decoy anchor; see note below)
  - `https://www.linkedin.com/in/&lt;member&gt;/recent-activity/newsletters/&lt;newsletter&gt;/`
    -- 2 occurrences (HTML-entity-escaped verbatim in the file; decodes to
    `https://www.linkedin.com/in/<member>/recent-activity/newsletters/<newsletter>/`)
  - `https://www.linkedin.com/newsletters/branching-out-4824/` -- 2
    occurrences
  - `https://www.linkedin.com/newsletters/data-ops-weekly-4823/` -- 2
    occurrences
  - `https://www.linkedin.com/newsletters/data-weekly-4822/` -- 3 occurrences
  - `https://www.linkedin.com/newsletters/weekly-notes-by-<person-name>-4821/`
    -- 2 occurrences (source text carries a synthetic full person name in
    place of `<person-name>`)
- NOTABLE, VERIFIED FINDING: of the 13 total "newsletter"-containing hrefs,
  only 11 match the shipped reader's actual anchor selector,
  `newsletters.ANCHOR_SELECTOR = 'a[href*="/newsletters/"]'` (which requires
  the PLURAL "newsletters" immediately followed by a slash). The 2
  `/article/newsletter/new/` hrefs use the SINGULAR "newsletter" and do not
  match. The fixture's own header comment confirms this is deliberate: these
  two are a planted DECOY ("Create a newsletter") -- one placed outside the
  `<main>` landmark, one inside it -- specifically so that a document-wide
  anchor counter (rather than one correctly scoped to `<main>`) would report
  2-in-main-and-0-outside and fail a scoping assertion; the comment
  cross-references `scripts/_probe_newsletter_surface_shape.py` as the
  measurement behind the `<main>` wrapper's addition. This reconciles exactly
  with `EXPECTED_ANCHORS = 11` in `tests/test_newsletter_reader.py`
  (13 total minus these 2 decoys = 11).

---

## 7. Scripts under `scripts/` whose NAME or CONTENT mentions "newsletter"

None were run, per instruction; each one-sentence description below is taken
from that script's own module docstring.

### By file name (3)

- **`scripts/_probe_newsletter_routes.py`** -- measures whether
  `readonly.assert_read_url` currently admits each of several candidate
  newsletter-related routes today, as distinct from the census's separate
  question of where LinkedIn merely draws a newsletter control.
- **`scripts/_probe_newsletter_subscriptions_live.py`** -- a live,
  single-page-load probe of `/mynetwork/network-manager/newsletters/`,
  measuring whether LinkedIn serves that address at all (versus redirecting
  it, the way it redirects `/in/me/details/interests/`), whether the account
  subscribes to any newsletter, whether the page also lists newsletters he
  authors, and whether an unsubscribe control is drawn there.
- **`scripts/_probe_newsletter_surface_shape.py`** -- an OFFLINE
  re-measurement (no browser, no network, over the gitignored capture) of
  every control the newsletters-manager page draws, used to decide, per
  remaining NEWSLETTER-SURFACE census row, whether it is missing a
  WriteSpec or missing an address entirely.

### By content only (7 more; name does not contain "newsletter")

- **`scripts/_probe_analytics_controls_live.py`** -- measures, on the
  profile-analytics page `linkedin_who_viewed_me` already opens, whether
  four specific unpressed controls actually exist in the DOM, to distinguish
  "not on the page" from "hidden until pressed"; mentions newsletters only
  in a comment explaining why `/newsletters/` and `/posts/` are deliberately
  excluded from one of its link-tree constants (a newsletter slug can be
  shaped identically to an ordinary lowercase route name).
- **`scripts/_probe_groups_locator_walk.py`** -- measures whether a Groups
  page section-split can be done with Playwright locators alone, with no
  `page.evaluate` call; cites `newsletters.py` (with `premium.py` and
  `notify_cost.py`) as precedent for staying locator-only.
- **`scripts/_probe_interests_entity_shaping.py`** -- measures which entity
  kinds (of five the profile Interests tab enumerates, one of which is
  Newsletters) can carry a real name past the shared census shaping guard,
  as the precondition for a boundary widening.
- **`scripts/_probe_job_collections_live.py`** -- measures whether the
  recommended-jobs collection page renders anything and what shape a row
  takes; credits "the newsletter wave" for having named and refused the trap
  of writing a reader against an imagined, unopened DOM.
- **`scripts/_probe_premium_entitlement.py`** -- measures, from one page load
  of `/premium/my-premium/`, which of three named Premium-entitlement states
  the account is in (to the extent one load can settle it); mentions
  `_probe_newsletter_subscriptions_live.py` once, as a precedent for the same
  door-vs-room framing.
- **`scripts/_probe_unmeasured_surfaces_live.py`** -- measures what three
  specific reachable-but-unmeasured surfaces (a job posting's insight panel,
  the messaging overflow menu, and the profile Interests tab's five entity
  categories including Newsletters) actually draw.
- **`scripts/_sweep_frozen_rows.py`** -- a generic tool measuring which
  UNASSIGNED census rows match a given word, to tell apart "the search
  missed a row" from "no row for that word exists"; its own committed
  `--control` self-test constants happen to be `CONTROL_HIT = "newsletter"`
  (a word guaranteed already present among assigned rows) paired with
  `CONTROL_MISS = "zzzznotacapability"` (guaranteed absent) -- "newsletter"
  here is an arbitrary reliable positive-control word, unrelated to the
  newsletter feature itself.

### Not a script (matched by content, reported for completeness)

- **`scripts/ci_shard_timings.json`** -- a CI test-timing data file (no
  docstring; not a script). It records per-test-file durations used to
  balance parallel CI shards, and lists `"tests/test_newsletter_reader.py":
  9.018` and `"tests/test_newsletter_route.py": 0.17` among its entries.

### Compiled cache artifact (excluded from the counts above)

- `scripts/__pycache__/_probe_newsletter_subscriptions_live.cpython-313.pyc`
  -- a stale compiled bytecode cache of the script above; not source, not
  separately inventoried.

---

## 8. Every URL string containing "newsletter" in tracked files, and its `is_read_url` verdict

Predicate confirmed callable and used exactly as shipped:
`from linkedin_server import readonly; readonly.is_read_url(url)`, run from
this worktree's own venv interpreter (`is_read_url` is a thin non-raising
wrapper around `assert_read_url`, both defined in `linkedin_server/readonly.py`).

### Full URL literals (19 distinct strings; each begins `https://www.linkedin.com`)

Two are the SAME address in two different literal spellings (with/without
trailing slash); both were run through the predicate separately as they
appear.

| `is_read_url` | URL | appears in |
|---|---|---|
| **True** | `https://www.linkedin.com/mynetwork/network-manager/newsletters/` | `linkedin_server/newsletters.py` (`SUBSCRIPTIONS_URL`); `tests/fixtures/connections_list.html`; `tests/test_newsletter_route.py` (`NEWSLETTERS_ROOT`) |
| **True** | `https://www.linkedin.com/mynetwork/network-manager/newsletters` (no trailing slash) | `tests/test_newsletter_route.py` (second parametrize case for the slash-forms test) |
| False | `https://www.linkedin.com/analytics/creator/newsletters/` | `tests/test_analytics_creator_boundary.py` |
| False | `https://www.linkedin.com/newsletters/a-made-up-letter/` | `tests/test_membership_row.py`; `tests/test_newsletter_route.py`; `tests/test_subscription_row.py` (`A_NEWSLETTER_WORDS`) |
| False | `https://www.linkedin.com/newsletters/branching-out-4824/` | `tests/fixtures/synthetic/newsletter_subscriptions.html` |
| False | `https://www.linkedin.com/newsletters/data-ops-weekly-4823/` | `tests/fixtures/synthetic/newsletter_subscriptions.html` |
| False | `https://www.linkedin.com/newsletters/data-weekly-4822/` | `tests/fixtures/synthetic/newsletter_subscriptions.html`; `tests/test_newsletter_reader.py` |
| False | `https://www.linkedin.com/newsletters/weekly-123456/` | `scripts/_probe_newsletter_surface_shape.py`; `tests/test_membership_row.py`; `tests/test_newsletter_route.py`; `tests/test_subscription_row.py` (`A_NEWSLETTER`) |
| False | `https://www.linkedin.com/newsletters/weekly-notes-by-<person-name>-4821/` | `tests/fixtures/synthetic/newsletter_subscriptions.html`; `tests/test_newsletter_reader.py` |
| False | `https://www.linkedin.com/newsletters/` (bare product root) | `tests/test_newsletter_route.py` (`MUST_STAY_REFUSED`) |
| False | `https://www.linkedin.com/newsletters/weekly-123456/analytics/` | `tests/test_newsletter_route.py` (`MUST_STAY_REFUSED`) |
| False | `https://www.linkedin.com/analytics/newsletter/` | `tests/test_newsletter_route.py` (`MUST_STAY_REFUSED`) |
| False | `https://www.linkedin.com/mynetwork/network-manager/newsletters/?filter=subscribed` | `tests/test_newsletter_route.py` (`MUST_STAY_REFUSED`) |
| False | `https://www.linkedin.com/mynetwork/network-manager/newsletters/subscribed/` | `tests/test_newsletter_route.py` (`MUST_STAY_REFUSED`) |
| False | `https://www.linkedin.com/in/<member-slug>/recent-activity/newsletters/` | `tests/test_newsletter_route.py` (`MUST_STAY_REFUSED`; source uses a synthetic member slug in place of `<member-slug>`) |
| False | `https://www.linkedin.com/newsletters/create/` | `tests/test_newsletter_route.py` |
| False | `https://www.linkedin.com/in/<member-slug>/recent-activity/newsletters/weekly-123456/` | `tests/test_subscription_row.py` (`A_MEMBERS_NEWSLETTER_TAB`) |
| False | `https://www.linkedin.com/newsletters/weekly-123456/?authorProfile=<member-token>` | `tests/test_subscription_row.py` (`A_NEWSLETTER_WITH_A_TOKEN`; source carries a literal synthetic token in place of `<member-token>`) |
| False (tested as-written, literal `&lt;`/`&gt;` text, not decoded) | `https://www.linkedin.com/in/&lt;member&gt;/recent-activity/newsletters/&lt;newsletter&gt;/` | `tests/fixtures/synthetic/newsletter_subscriptions.html` (verbatim source text) |
| False (same href, after standard HTML-entity decoding -- i.e. what a browser's `get_attribute()` would actually return) | `https://www.linkedin.com/in/<member>/recent-activity/newsletters/<newsletter>/` | derived from the fixture line above, not separately present as its own literal |

Eleven of the thirteen `f"{BASE}..."`-composed URLs above were not literally
spelled out on one line in their source file; `BASE` is a plain
module-level literal (`BASE = "https://www.linkedin.com"`, confirmed by
direct read in both `tests/test_newsletter_route.py` and
`tests/test_subscription_row.py`) substituted here rather than guessed at.

### Strings that are NOT full URLs (predicate skipped, per instruction, rather than inventing a prefix)

- `/newsletters/<newsletter>` -- `linkedin_server/shape.py`
  (`_SUBSCRIPTION_HREF_MARKER`, and the substitution target of
  `_CENSUS_NEWSLETTER_PATH`); referenced by the same literal string in
  `tests/test_membership_row.py`, `tests/test_urn_substitution_covers_the_class.py`,
  and as an expected `href_shape` value throughout
  `tests/test_subscription_row.py`. A path fragment, not a URL; `assert_read_url`'s
  patterns are anchored on a full `https://www.linkedin.com/...` prefix, so
  running the predicate on a bare path would only ever trivially return
  `False` for lacking that prefix, not for any newsletter-specific reason.
- `/newsletter/new` -- `linkedin_server/press.py` (`_COMPOSER_MARKERS`
  entry). Same reasoning; also not a URL LinkedIn would be navigated to by
  this server, only an address-fragment marker checked by substring
  containment against an address already being pressed.
- `/article/newsletter/new/` -- `tests/fixtures/synthetic/newsletter_subscriptions.html`
  (the two decoy anchor hrefs described in section 6). Page content inside a
  fixture, never passed to the read boundary at all.
- `/search/results/newsletters/` -- `linkedin_server/search_results.py`
  (`control_fixture()`'s fixture HTML) and the corresponding `RESULT_TABLE`
  segment tuple. A path fragment used for segment-equality matching, never
  passed to `is_read_url`.
- `network-manager/newsletters` -- `tests/test_newsletter_route.py`, used
  only as a bare substring ("needle") to locate-and-remove the one admitting
  regex pattern in a mutation test; never itself a candidate URL.
- `/newsletters/` -- used as the substring argument inside
  `newsletters.ANCHOR_SELECTOR = 'a[href*="/newsletters/"]'`; a CSS
  attribute-substring selector, not a URL.

---

## Summary of the most surprising findings

1. `CENSUS_SURFACES` (section 4) has NO newsletter entry at all -- the whole
   newsletter-reading surface was deliberately filed against the profile
   Interests tab instead, and `newsletter_composer` in the pricing test is a
   synthetic fixture value that names no real surface, tool, or file
   anywhere in this repository.
2. Of 19 distinct full-URL literals containing "newsletter" across the
   tracked tree, exactly 2 (both slash-forms of the same
   `.../mynetwork/network-manager/newsletters/` root) pass `is_read_url`;
   every one of the 5 real per-newsletter subscription URLs captured in the
   synthetic fixture returns False, confirming the allowlist admits only the
   list page, never a newsletter's own page.
3. The synthetic fixture's 13 "newsletter"-containing hrefs are not all
   equivalent: 2 are a deliberately planted singular-"newsletter" decoy
   (`/article/newsletter/new/`) that the plural-only anchor selector must
   NOT match, which is what makes `EXPECTED_ANCHORS = 11` (not 13) correct.
4. `press.py`'s composer-refusal marker `/newsletter/new` and the fixture's
   decoy `/article/newsletter/new/` share that substring, though they are
   unrelated code paths built for different purposes (one refuses pressing
   an address; the other tests DOM-scoping of an anchor count).
5. `_sweep_frozen_rows.py` uses `CONTROL_HIT = "newsletter"` purely as an
   arbitrary reliable positive-control word for its own self-test, unrelated
   to the newsletter feature.
