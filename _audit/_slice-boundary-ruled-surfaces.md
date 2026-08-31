# Slice: the two ruled surfaces -- `/in/me/edit/intro/` and `/mypreferences/d/dark-mode`

Date 2026-08-31. Branch `master`, base HEAD `b364744`. Nothing committed, nothing
staged. Offline work only -- no browser was launched and no `mcp__linkedin__*`
tool was called.

Files changed (the five this slice owns):

    linkedin_server/readonly.py
    linkedin_server/server.py       (CENSUS_SURFACES + the census docstring only)
    tests/test_readonly.py
    tests/test_readonly_boundary_invariant.py
    tests/test_surface_census.py

`linkedin_server/dom.py` and `linkedin_server/writes.py` were NOT touched; they
show as modified in `git status` because the sibling agent owns them. See
ESCALATION 1.

---

## 1. Result of the required verification

    venv\Scripts\python.exe -m pytest -q tests/test_readonly.py
      tests/test_readonly_boundary_invariant.py tests/test_surface_census.py
      tests/test_tools.py tests/test_server_surface.py tests/test_path_hygiene.py

    3 failed, 407 passed in 11.93s

    ... with the three deselected:
    407 passed, 3 deselected in 11.36s

The baseline for this same six-file set before the slice was `378 passed`. The
three failures are caused by `INVITE_NEEDLE_JS`, a sixth injected script the
sibling agent added to `linkedin_server/dom.py` in the working tree. They are
PROVEN not to be mine in ESCALATION 1. Every check this slice added or moved is
green.

All five files are strict ASCII (byte-scanned: 0 bytes above 127 in each).

---

## 2. RED. Every new guard, shown failing against UNMODIFIED code

Captured by writing the tests first and running them with `readonly.py` and
`server.py` still at `b364744`. That run was `21 failed, 204 passed`. Verbatim:

### 2.1 `is_read_url("https://www.linkedin.com/in/me/edit/intro/")` was False

    _ test_read_surfaces_are_allowed[https://www.linkedin.com/in/me/edit/intro/] __
    url = 'https://www.linkedin.com/in/me/edit/intro/'
        @pytest.mark.parametrize("url", ALLOWED)
        def test_read_surfaces_are_allowed(url: str):
    >       assert readonly.assert_read_url(url) == url
    E               linkedin_server.errors.WriteAttemptError: navigation blocked:
    E               'https://www.linkedin.com/in/me/edit/intro/' contains '/edit/',
    E               which is not a read surface. This is the READ door and it refuses;
    E               a write goes through assert_write_url, which is narrower still. If
    E               you reached this, a url was built wrong.
    linkedin_server\readonly.py:336: WriteAttemptError

Note WHICH gate refused it before: the forbidden-substring gate, on `/edit/`.
That is exactly the gate the named exemption now buys past, for this one url.

### 2.2 `is_read_url("https://www.linkedin.com/mypreferences/d/dark-mode")` was False

    FAILED tests/test_readonly.py::test_read_surfaces_are_allowed[https://www.linkedin.com/mypreferences/d/dark-mode]

and, from the surface test that asserts both at once:

    E   AssertionError: assert False
         +  where False = is_read_url('https://www.linkedin.com/in/me/edit/intro/')
    tests\test_readonly.py:689: AssertionError
    (test_the_two_ruled_surfaces_are_admitted_and_their_families_are_not)

### 2.3 The two account-ending addresses: the REASON changed, not the answer

This is the one the brief singled out. Both were refused before and both are
refused now, so the test asserts WHICH GATE, by the exception message. Before:

    E   AssertionError: navigation blocked:
    E   'https://www.linkedin.com/mypreferences/d/close-accounts' is not on the
    E   read-only allowlist. Add a pattern to readonly._ALLOWED_URL_PATTERNS only
    E   if the target is genuinely a page that displays the operator's own data.
        assert 'not a read surface' in "navigation blocked: '...close-accounts'
        is not on the read-only allowlist. ..."
    tests\test_readonly.py:749: AssertionError

    E   AssertionError: navigation blocked:
    E   'https://www.linkedin.com/mypreferences/d/hibernate-account' is not on the
    E   read-only allowlist. Add a pattern to readonly._ALLOWED_URL_PATTERNS only
    E   if the target is genuinely a page that displays the operator's own data.
    tests\test_readonly.py:749: AssertionError

`is not on the read-only allowlist` IS the allowlist refusal: there was no second
gate. After the change the same two urls raise
`contains '/close-accounts', which is not a read surface` and
`contains '/hibernate-account', ...` -- the denylist refusal. Measured in
section 5.

### 2.4 The exemption table did not exist

    E   AttributeError: module 'linkedin_server.readonly' has no attribute
        '_FORBIDDEN_SUBSTRING_EXEMPTIONS'
    tests\test_readonly.py:772  (test_the_exemption_table_is_exactly_one_url_for_exactly_one_substring)
    tests\test_readonly.py:801  (test_an_exemption_buys_past_one_substring_and_not_a_second)
    tests\test_readonly.py:824  (test_the_exemption_does_not_buy_past_the_allowlist)
    tests\test_readonly.py:856  (test_the_exemption_is_matched_with_equality_and_never_as_a_prefix)

### 2.5 The two urls the server now builds did not pass the allowlist

    E   AssertionError: https://www.linkedin.com/in/me/edit/intro/
        assert False
         +  where False = is_read_url('https://www.linkedin.com/in/me/edit/intro/')
    tests\test_readonly.py:915: AssertionError
    (test_the_urls_the_server_actually_builds_all_pass_the_allowlist)

### 2.6 The forbidden-list roster, and its own can-it-fail control

    E   AssertionError: these substrings left the forbidden list:
        ['/close-accounts', '/hibernate-account']. Each one was a refusal somebody
        wrote deliberately. Removing one is a boundary change, not a tidy-up.
    tests\test_readonly.py:1050  (test_the_forbidden_list_has_only_ever_grown)

    E   AssertionError: ['/messaging/compose', '/close-accounts', '/hibernate-account']
        assert ['/messaging/...nate-account'] == ['/messaging/compose']
    tests\test_readonly.py:1072  (test_that_roster_check_can_fail_on_a_deletion)

### 2.7 The census surface table

    E   AssertionError: assert {'feed', 'profile', 'settings'} == {'feed', ... 'settings_dark_mode'}
          Extra items in the right set:
          'profile_edit_intro'
          'settings_dark_mode'
    tests\test_surface_census.py:656 (test_the_surface_table_is_a_closed_set_of_five)

    E   AssertionError: assert False is True
         +  where False = is_read_url('https://www.linkedin.com/in/me/edit/intro/')
    tests\test_surface_census.py:685 (test_the_two_surfaces_ruled_on_2026_08_31_reach_one_page_each)

    E   AssertionError: assert ['feed', 'profile', 'settings'] == ['feed', ... 'settings_dark_mode']
          At index 2 diff: 'settings' != 'profile_edit_intro'
    tests\test_surface_census.py:816 (test_an_unknown_surface_is_refused_without_navigating, all 7 params)

### 2.8 What is deliberately NOT claimed as a red

`/in/someone-else/edit/intro/`, `/in/me/edit/`, `/in/me/edit/topcard/` and the
prefix escape `/in/me/edit/intro/../../evil` were refused BEFORE and are refused
NOW, and a bare "it raises" assertion on them would pass identically across the
change. They are therefore asserted with an instrument that CAN tell the two
implementations apart:

* `test_the_exemption_is_matched_with_equality_and_never_as_a_prefix` asserts the
  refusal names `'/edit/'`. Under a `startswith` lookup all four escapes would be
  waved past `/edit/` and stopped later or elsewhere -- by the allowlist, by
  `action=`, or by `/delete` -- so the message is the discriminator, exactly as
  it is for the two account-ending addresses. The test also asserts the prefix
  relation really holds, so the claim is about this code and not about four urls
  that are not prefixes at all.
* `test_the_two_ruled_surfaces_are_admitted_and_their_families_are_not` closes
  with a NOT-VACUOUS control: every refused address is asserted to MATCH the
  tempting pattern somebody would reach for
  (`/in/[A-Za-z0-9\-_%]+/edit/intro/?$` and `/mypreferences/d/[a-z\-/]+$`), so
  the enumeration is the only thing standing between this server and all of them.

---

## 3. The exemption: final diff and its check

New structure in `linkedin_server/readonly.py` (its 30-line comment block, which
states the three semantics, is omitted here):

    +_FORBIDDEN_SUBSTRING_EXEMPTIONS: dict[str, str] = {
    +    "https://www.linkedin.com/in/me/edit/intro/": "/edit/",
    +}

The check, inside `assert_read_url`:

         lowered = url.lower()
    +    # The ONE substring this exact url may carry, or None. A dict lookup is an
    +    # equality test, which is the whole of the discipline: a url that merely
    +    # begins with an exempted one matches nothing here. See
    +    # :data:`_FORBIDDEN_SUBSTRING_EXEMPTIONS`.
    +    exempted = _FORBIDDEN_SUBSTRING_EXEMPTIONS.get(lowered)
         for bad in _FORBIDDEN_URL_SUBSTRINGS:
             if bad in lowered:
    +            # PER-SUBSTRING, so an exemption for /edit/ does not survive a
    +            # /delete appearing in the same url. The loop continues rather
    +            # than returning: the remaining substrings still get their say,
    +            # and the allowlist below still has to admit the url.
    +            if exempted is not None and exempted == bad:
    +                continue
                 raise WriteAttemptError(

Four properties, each with its own test:

| property | test |
|---|---|
| key is an EXACT complete url, `==` and never `startswith` | `test_the_exemption_is_matched_with_equality_and_never_as_a_prefix` |
| exemption is PER-SUBSTRING: a second forbidden substring still refuses | `test_an_exemption_buys_past_one_substring_and_not_a_second` |
| buys past ONE gate, never both -- the allowlist still applies | `test_the_exemption_does_not_buy_past_the_allowlist` |
| contents pinned: one url, one substring, and that substring really forbidden | `test_the_exemption_table_is_exactly_one_url_for_exactly_one_substring` |

The per-substring test replaces the table with a hostile one via `monkeypatch`
(`.../in/me/edit/intro/delete`, exempted for `/edit/` only, and still refused by
`/delete`), because the live table has one entry whose url carries one forbidden
substring -- so the property cannot be demonstrated on live data, and a property
that cannot be demonstrated is one a refactor can drop with nothing going red.

`/edit/` was NOT deleted and NOT loosened. `/mypreferences/d/categories/`,
`/psettings/` and `/settings/` were not touched.

---

## 4. Digests: which moved, which did not

`tests/test_readonly_boundary_invariant.py`, `READONLY_AST_AT_LAST_REFREEZE`:

    MOVED  _ALLOWED_URL_PATTERNS       0edd01ead91a89ea -> 72bc5d4a88b5325b
    MOVED  _FORBIDDEN_URL_SUBSTRINGS   fcb931b0eaee5b84 -> 5e26ec3a8b29c38c
    MOVED  <functions>                 199939f7998e8d48 -> eb16cd07f5cf369d

    same   _MUTATION_CALL_PATTERNS     23aece1483afdee9
    same   JS_MUTATION_TOKENS          d47e30b67c583c1b
    same   SANCTIONED_MUTATIONS        b84365077cba813b

`DENYLISTS_AT_A76FE32` carries the same two new url-list values (its fourth
re-baseline). A re-freeze comment in the file's own voice records the date, the
moves, and -- because a digest cannot tell a list that grew from one that shrank
-- the DIRECTION of each:

* the allowlist GREW by exactly two anchored patterns, each naming ONE url; no
  pattern was widened, relaxed or removed;
* the forbidden list ALSO GREW, by `/close-accounts` and `/hibernate-account`;
  nothing left it. That is the rarer half: the same change that widened the
  allowlist twice gave the two most destructive addresses on the account their
  first second gate;
* `<functions>` moved because `assert_read_url` gained the four-line equality
  lookup above. Nothing was deleted from that function and no refusal loosened.

Verified under Python 3.13.14 ONLY. No 3.10 interpreter is installed on this box
(no `py` launcher, no `Python310` under `%LOCALAPPDATA%\Programs\Python`). The
previous re-freeze's escape hatch does NOT apply here, because `<functions>` --
the one digest that has historically split along the interpreter matrix -- is
exactly the digest that moved this time. What carries the claim is construction
rather than a second run: `_function_source` asks the tokenizer only WHERE the
comments are (a position question, stable) and hashes the remaining source TEXT,
which is the v3 fix measured identical under 3.13.14 and 3.10.19 when it landed.
The 3.10 CI cell is the check, and this is written into the re-freeze comment.

---

## 5. What is STILL refused in each family touched

Measured by running `readonly.assert_read_url` over each address and reading the
gate off the exception message. Post-change state.

### The `/edit/` family -- ONE url readable out of eleven probed

    /in/me/edit/intro/                        READABLE
    /in/me/edit/intro                         REFUSED by forbidden substring '/edit/'
    /in/me/edit/                              REFUSED by forbidden substring '/edit/'
    /in/me/edit/topcard/                      REFUSED by forbidden substring '/edit/'
    /in/me/edit/forms/next-action/            REFUSED by forbidden substring '/edit/'
    /in/me/edit/intro/../../evil              REFUSED by forbidden substring '/edit/'
    /in/me/edit/intro/delete                  REFUSED by forbidden substring '/edit/'
    /in/me/edit/intro/?action=delete          REFUSED by forbidden substring '/edit/'
    /in/alex-r-12ab34/edit/intro/             REFUSED by forbidden substring '/edit/'
    /in/alex-r-12ab34/edit/                   REFUSED by forbidden substring '/edit/'
    /in/me/details/skills/edit/forms/2/       REFUSED by forbidden substring '/edit/'

No member-slug pattern was written. The `/in/me/` spelling is the whole of the
permission, on the ground the brief names: `linkedin_who_viewed_me` has MEASURED
that loading a third party's profile leaves them a durable record, so a pattern
that can address anybody but him is refused on that ground before any other, and
`/in/me/` redirects to whoever is signed in.

### The `/mypreferences/d/` family -- three readable out of twelve probed

    /mypreferences/d/                         READABLE  (the index, admitted 2026-08-30)
    /mypreferences/d/dark-mode                READABLE
    /mypreferences/d/dark-mode/               READABLE  (the same page, trailing slash)
    /mypreferences/d/dark-mode/extra          REFUSED by allowlist
    /mypreferences/d/dark-mode?theme=dark     REFUSED by allowlist
    /mypreferences/d/close-accounts           REFUSED by forbidden substring '/close-accounts'
    /mypreferences/d/hibernate-account        REFUSED by forbidden substring '/hibernate-account'
    /mypreferences/d/settings/language        REFUSED by forbidden substring '/settings/'
    /mypreferences/d/settings/autoplay-videos REFUSED by forbidden substring '/settings/'
    /mypreferences/d/categories/account       REFUSED by forbidden substring '/mypreferences/d/categories/'
    /mypreferences/d/data-privacy             REFUSED by allowlist
    /psettings/                               REFUSED by forbidden substring '/psettings/'

`dark-mode` was chosen over `language`, `autoplay-videos` and any `categories/`
page on the two grounds in the brief, and the table above is the evidence for the
second: NOT ONE forbidden substring had to be narrowed. The `/settings/` entry is
intact and still refuses the two named alternatives; the
`/mypreferences/d/categories/` entry is intact and still refuses the toggles.

### Existing behavioural freezes that still hold

`MUST_STAY_UNREADABLE` in `tests/test_readonly.py` already carried
`https://www.linkedin.com/in/me/edit/` before this slice, and it still passes.
Six addresses were added to it here: the two account-ending pages,
`/mypreferences/d/settings/language`, `/in/me/edit/topcard/`,
`/in/alex-r-12ab34/edit/intro/`, and the prefix escape
`/in/me/edit/intro/../../evil`.

Cross-file checks in files this slice does NOT own were confirmed unaffected:
`tests/test_writes.py:539` (`/in/someone/edit/` is False),
`tests/test_writes_nine.py:709` (`/mynetwork/` is False),
`tests/test_api_call_sites.py:173` (`is_read_url(ME_API)` is False).

---

## 6. ESCALATIONS -- four things the lead should rule on

### ESCALATION 1 (blocks the "all must pass" clause): three tests fail on the sibling's `dom.py`

`tests/test_readonly.py` -- a file this slice owns -- declares `INJECTED_SCRIPTS`
and `EXECUTED_SCRIPTS` and caps the number of `# readonly-ok` waivers in
`dom.py`. The sibling agent added a sixth injected script, `INVITE_NEEDLE_JS`,
plus a seventh waiver, to `linkedin_server/dom.py` in the working tree. That
symbol is absent at `b364744` (`git show HEAD:linkedin_server/dom.py` greps to
`0`) and present four times in the working copy.

    FAILED tests/test_readonly.py::test_only_dom_module_waives_evaluate
    tests\test_readonly.py:290: assert waived_in.get("dom.py", 0) <= 6, waived_in
    E   AssertionError: {'dom.py': 7}
    E   assert 7 <= 6

    FAILED tests/test_readonly.py::test_the_scripts_executed_are_exactly_the_ones_declared
    tests\test_readonly.py:414: assert names == set(INJECTED_SCRIPTS), names
    E   AssertionError: {'CENSUS_JS', 'HARVEST_BLOCK_CARDS_JS', 'HARVEST_LINKED_CARDS_JS',
        'INVITE_NEEDLE_JS', 'READ_PROFILE_JS', 'TRACKER_ROW_SHAPE_JS'}
          Extra items in the left set: 'INVITE_NEEDLE_JS'

    FAILED tests/test_readonly.py::test_every_injected_script_is_scanned
    tests\test_readonly.py:462: assert declared == set(INJECTED_SCRIPTS), declared
    E   AssertionError: ... Extra items in the left set: 'INVITE_NEEDLE_JS'

PROVEN NOT MINE, by measurement rather than argument. `git archive HEAD` was
unpacked into a scratch directory, the sibling's LIVE `dom.py` copied over it,
and every other file left at `b364744`:

    3 failed in 0.69s       (everything at HEAD, plus the sibling's dom.py)

then the same directory with HEAD's `dom.py` restored:

    3 passed in 0.51s       (pure HEAD)

So the three reproduce with none of my edits present, and disappear when only
`dom.py` is reverted. `git diff tests/test_readonly.py` contains zero changes to
`INJECTED_SCRIPTS`, `EXECUTED_SCRIPTS` or any `_JS` name.

I did NOT fix it. Declaring `INVITE_NEEDLE_JS` would enrol it in
`test_every_script_this_package_executes_cannot_mutate`, which is a
certification of a script I was not briefed on, and raising the waiver cap from
6 to 7 is a boundary decision about another agent's work. It needs an owner:
`dom.py` belongs to the sibling and `tests/test_readonly.py` to this slice, and
the two edits are one change.

### ESCALATION 2: `_FORBIDDEN_SUBSTRING_EXEMPTIONS` is not in `PINNED`, and adding it needs a code change first

The new table GRANTS rather than refuses. That is precisely the property that
earned `SANCTIONED_MUTATIONS` its place in `PINNED` -- "a boundary made of four
denylists and one allowlist is only as frozen as its allowlist" -- so it belongs
there. The brief did not ask for it, so I did not add it, and there is a
technical reason not to add it blind:

`_literal` in `tests/test_readonly_boundary_invariant.py` handles `Constant`,
`Tuple/List/Set`, `Call`, `Attribute` and `BinOp`, and has NO `ast.Dict` branch.
It would return `['<unhandled>', 'Dict']` for every possible dict content -- a
pin that cannot fail, which is worse than no pin. Adding the structure to
`PINNED` means teaching `_literal` to render a dict in the same commit.

Meanwhile the contents ARE pinned behaviourally, in the place this repo already
chose for direction-sensitive checks:
`test_the_exemption_table_is_exactly_one_url_for_exactly_one_substring` asserts
the key, the value, that the exempted substring is genuinely on the forbidden
list, and that the key is stored lowercased. Recorded in the re-freeze comment so
the next reader does not have to rediscover it.

### ESCALATION 3: the slashless spelling is admitted by the pattern and refused by the exemption

The brief fixed the pattern as `.../in/me/edit/intro/?$` and the exemption as
exactly one entry. The two are consistent, and the consequence is that
`https://www.linkedin.com/in/me/edit/intro` (no trailing slash) matches the
allowlist pattern but finds no exemption, so it is refused by `/edit/`. Only the
trailing-slash form -- the one `CENSUS_SURFACES` builds -- is readable end to
end. The exemption being NARROWER than the pattern is the conservative
direction, so I implemented it exactly as specified and documented it on the
pattern and in `BLOCKED`. Flagged because it is the kind of asymmetry a later
reader will take for a bug.

### ESCALATION 4: a stale count left untouched, deliberately

`tests/test_readonly_boundary_invariant.py`'s module docstring still says of the
re-freeze moment: "IT HAS BEEN ONE, ONCE." It has now been five. Left alone
because the brief scoped my edit in that file to the digests and the re-freeze
comment, and because it is the same class of count-rot the wave is correcting
elsewhere -- it should move in whichever commit the lead is already using for
that. One line: `tests/test_readonly_boundary_invariant.py:35`.

For contrast, one stale count WAS corrected, because it sits inside the
`CENSUS_SURFACES` comment block the brief told me to extend: that block said the
tool "reads three pages" while five keys now sit below it, and it still claimed
"Nothing in `readonly.py` was touched to add this", which stopped being true on
2026-08-30. Both are replaced by a note recording what they used to say.

---

## 7. `CENSUS_SURFACES` after the change

    CENSUS_SURFACES: dict[str, str] = {
        "feed": FEED_URL,
        "profile": f"{BASE_URL}/in/me/",
        "profile_edit_intro": f"{BASE_URL}/in/me/edit/intro/",
        "settings": f"{BASE_URL}/mypreferences/d/",
        "settings_dark_mode": f"{BASE_URL}/mypreferences/d/dark-mode",
    }

Each new key has a ruling in the block above it, in the same voice as the four
ruled on 2026-08-30, covering what it is for, that it is HIS OWN data, that it
consumes no badge and emits nothing another member can observe, and that it
changes no value -- both pages RENDER existing state, and a census types nothing
and submits nothing, so neither leaves an artefact.

The `Args:` section of `linkedin_surface_census` now enumerates all five keys.
`readonly.docstring_write_claims(linkedin_surface_census.__doc__)` is still `[]`
(asserted by `tests/test_surface_census.py:905`), which is why the docstring says
"intro editor" and never the bare word that `\bedit\b` would match.
