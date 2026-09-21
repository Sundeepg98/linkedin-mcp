# A LANDING IS A STRING THE SITE CHOSE, AND THIS PROCESS HAD NO ALLOWLIST FOR IT

Wave `landed-url`, 2026-09-21, from master `762ec23`. Register section 51.

**CORRECTS:** `_audit/2026-09-21-the-three-readers.md` -- its section 6b says "THE GENERAL CASE IS NAMED AND NOT FIXED. Every other tool in `server.py` still publishes its landing in this refusal", which was true when written and is false now.

The general case is repaired in `auth.assert_not_authwall` itself and every
tool in the package withholds its landing. The same section's premise about
LinkedIn's authwall
query was asserted from url shape; it is MEASURED here, and the half of it that
makes the leak severe -- that the bounced address can be a NAME -- is still
DERIVED and is labelled so in section 1.3.
No browser was opened. No LinkedIn page was loaded. No write was fired. Every
number below is offline, from shipped code, the committed tree, and Chrome's
own history databases in the gitignored `_state/`.

---

## 0. THE ANSWER, FIRST

**The leak is real, the convention behind it is now MEASURED rather than
inferred, and the specific claim that made it severe is still DERIVED.**

    auth.assert_not_authwall        28 call sites in linkedin_server/
                                    (27 in server.py, 1 in writes.py; 27 are
                                     tool-facing, one is inside server.py's own
                                     local helper). 7 more in scripts/.
                                    Counted by AST. The brief's "30" is the
                                    grep count and includes the two `import`
                                    lines.

    message sites examined          21, across 10 modules
    repaired                         7
    named, not repaired             13, each with its reason in section 5
    not an address at all            1 -- a regex that spells `href`

**AND THE QUESTION THE LEAD ASKED PLAINLY. Can a name still reach a caller
through an error message anywhere in this package? YES.** Not through this
class -- through the FIELD beside it, and it is section 6.1:

> `ExtractionFailedError.url` is published by `server._error` with **NO
> SCRUBBER AT ALL**. 20 sites feed it; 12 hand it `page.url` read at the
> moment of the raise, with no authwall gate in between.

**MEASURED: 12 of the 12 `dom.py` sites were DRIVEN TO THEIR OWN RAISE, and all
12 published the planted slug verbatim at `$.url`.** Reachability is not a
question there -- it is structural, and section 6.1 explains why. A declared
contract whose success-path twin has a standing per-site ruling and whose
failure-path self has none. It needs a ruling and a measurement against a real
browser, not an edit, and this wave had none.

**AND `out["url"]` IS NOT THE ONLY UNSCRUBBED CHANNEL ON THOSE TWELVE.** Every
one of their messages is `f"...: {type(exc).__name__}: {exc}"`, so whatever the
BROWSER put in its own exception is interpolated into `out["message"]` and
scrubbed for paths only. A second needle, planted only inside the exception
`page.evaluate` raised, landed at `$.message` in all 12 drives.

Two smaller ones: a `hint` MEASURED publishing the page's own section headings
at `$.hint` (6.4), and slugs in `out["profile"]` / `out["company_url"]` (5.2).

---

## 1. WHAT AN AUTHWALL LANDING ACTUALLY CARRIES -- MEASURED

The claim this repository has been carrying, in two identically worded and
uncited places (`_audit/2026-09-21-the-three-readers.md` section 6b, and the
`#:` comment over `tests/test_company_root.AUTHWALL_CARRYING_A_SLUG`):

> LINKEDIN'S AUTHWALL CARRIES THE ADDRESS IT BOUNCED INSIDE ITS OWN QUERY.

Both were assertions about LinkedIn resting on a measurement of OUR OWN
refusal over a SYNTHETIC url. The evidence for the real claim was on this disk
the whole time, in a place nobody had looked: **the browser's own history
databases**, not the project's capture files.

### 1.1 THE COUNT, FROM CHROME'S `visits` TABLE

Landing events matching `config.AUTHWALL_MARKERS`, deduplicated across five
generations of the persistent profile by `(visit_time, hash(url))`:

| marker family | landing events | with a recorded predecessor |
|---|---:|---:|
| `/authwall` | **1** | 1 |
| `/uas/login` (also matches `/login`) | 13 | 13 |
| `/login` (bare) | 17 | 0 |
| `/checkpoint/` | **0** | 0 |
| total | **31** | **14** |

A raw byte scan finds 508 marker-bearing occurrences under `_state/`; they
collapse to 49 distinct strings and 31 distinct events, because Chrome keeps
the same database under `Default/` and under `Snapshots/<version>/Default/`
and the profile has been copied four times. **A naive occurrence count
overstates this evidence by roughly 16x**, which is why the honest number is
31 and not 508.

### 1.2 THE PARAMETER, AND THE CLOSED LOOP THAT PROVES IT

The single `/authwall` event, 2026-08-24 18:06:50, corroborated across nine
files by four different Chrome subsystems:

    marker matched        /authwall
    total length          280 characters
    Chrome transition     LINK + CHAIN_END  -- a chain terminus, not a typed url
    predecessor           a /jobs/view/<numeric id>/ navigation ONE SECOND
                          earlier, resolved through `visits.from_visit`
    parameters, in order  trk, trkInfo, original_referer, sessionRedirect

**THE PARAMETER IS `sessionRedirect`, camelCase.** Its value, described and
not reproduced: 60 characters percent-encoded, decoding to a 46-character
ABSOLUTE url with host `www.linkedin.com` and inner path shape
`/jobs/<4-char segment>/<10-digit run>`.

The predecessor Chrome recorded and the address inside the parameter are the
same address, established two independent ways one second apart. That is a
closed loop rather than an inference from url shape.

    /uas/login landings    parameter is `session_redirect`, SNAKE case
    predecessor agreement  14 of 14, no exceptions
                           /feed/ -> /feed (11), /messaging/ -> /messaging (2),
                           /jobs/view/<id>/ -> /jobs/... (1)

**Evidence class: VERIFIED-BY-INSTRUMENT.** n=1 for the literal `/authwall`
path, n=13 for the other spelling.

### 1.3 AND THE HALF THAT REFUTES THE SEVERITY ARGUMENT

**NOT ONE MEASURED LANDING CARRIES AN `/in/<member>/` PATH OR AN ORGANISATION
SLUG.** Every observed inner address is `/feed`, `/messaging` or
`/jobs/view/<numeric id>`. The identifying segment in the one jobs case is a
ten-digit run.

So the two halves of the claim have different evidence classes and the
repository was spelling them as one sentence:

| claim | class |
|---|---|
| the authwall carries the address it bounced | **VERIFIED** |
| therefore that address can be a person's or an organisation's slug | **DERIVED** -- from LinkedIn's url grammar, from nothing on this disk |

`_audit/_slice-editor-fields.md` already said the observational half correctly
-- *"no marker in AUTHWALL_MARKERS has been observed on a url carrying an
`/in/<member>/` path"* -- and **that sentence holds against the whole disk.**
`_audit/2026-08-30-linkedin-nine.md` labelled its `/checkpoint/` claim DERIVED
and was right to: that marker has still never fired.

**WHY THE REPAIR DOES NOT REST ON ANY OF THIS.** The defect is not the
parameter. It is that a landing is a string LinkedIn chose and this process has
no allowlist for it, published into text a scrubber cannot clean. The
`sessionRedirect` convention is the strongest known instance, not the premise.
Had the measurement come back empty the repair would be unchanged and only this
section would read differently -- which is the test of whether a fix rests on
an inference.

### 1.4 A DIVERGENCE BETWEEN THE FIXTURES AND THE WORLD, WORTH CARRYING

Three committed fixtures spell the parameter value as a RELATIVE path --
`login?session_redirect=%2Ffeed`, 7 characters. Every real `/feed` landing
encodes an ABSOLUTE url, 40 characters. **Nothing measured shows LinkedIn
emitting the relative form**, so anything calibrated on those fixtures -- a
truncation bound, a message-length estimate, what a scrubber would have to
match -- is calibrated about six times short. Named, not changed: those
fixtures are other tests' inputs.

---

## 2. THE DECISION: `scrub()` OR THE RAISE SITE

This is the part the brief asked for an argument on rather than a coin toss.

### 2.1 IT IS NOT `scrub()`, FOR FOUR REASONS

**1. ITS ENGINE REFUSES THIS JOB IN WRITING, AND THE FILE MAY NOT BE EDITED.**
`config.scrub` is `paths.relativise_known`, a VENDORED copy carrying a
DO-NOT-EDIT header and a test that fails on a single differing byte. That
function says, in shipped text:

> SUBSTITUTION IS EXACT, NEVER HEURISTIC. [...] A regex that hunted for
> path-shaped text in arbitrary prose would eventually eat a Naukri API route,
> **A URL**, or a Windows drive letter inside quoted user content -- which is
> how a scrubber does more damage than the leak it was written for.

A url is named there as the COLLATERAL. Doing the opposite inside the same
call is not an extension of that reasoning; it is its refutation.

**2. THERE IS NOTHING TO PUT ON THE ALLOWLIST.** `scrub` substitutes values
the server already KNOWS it may have emitted -- five of its own directories,
read fresh so an environment override is covered. The leaking value here is
chosen by LinkedIn at the instant of the bounce. Inverting the list does not
help either: this package assembles addresses at runtime from caller-supplied
numeric ids, so "known good" is a PATTERN SET, which is a heuristic wearing an
allowlist's clothes.

**3. PROVENANCE DECIDES PUBLISHABILITY AND THE SINK CANNOT SEE PROVENANCE.**

    https://www.linkedin.com/company/5417062/       assembled by this package,
                                                    published on purpose as
                                                    company_page_url
    https://www.linkedin.com/authwall?sessionRe...  chosen by LinkedIn

Same shape, opposite verdicts, and only the raise site knows which one it is
holding. **A path is different in exactly the way that makes `scrub` correct
FOR PATHS**: this machine's absolute layout may never be published whatever its
provenance, so a sink-side exact substitution is right there. What transfers
from the coercion finding is the OBSERVATION -- a value reaches a caller
through error text -- and never the REMEDY.

**4. BLAST RADIUS, FROM A WAVE THAT CANNOT RUN THE BROWSER.** `scrub` is
applied to `str(exc)` for every exception this server reports, including
Playwright's and the standard library's, whose messages carry addresses that
ARE the diagnosis. Rewriting all of them is the highest-blast-radius edit
available here, and it is the edit the coercion wave refused on the same
grounds when it declined to sweep 42 write-gate sites it could not exercise.

### 2.2 AND THE HONEST COST OF THE OTHER SIDE

A raise-site repair leaves the next interpolation free to repeat the defect.
That is real. It is paid the way `coerce.py` paid it:

* **ONE IMPORTABLE HOME** -- `linkedin_server/landing.py` -- so the class
  closes for functions nobody has written yet, rather than a 28th local fix;
* **A STANDING GUARD THAT DISCOVERS ITS SUBJECTS**, walking the package's AST
  for message-bearing interpolations of address-named expressions, with a
  baseline that refuses to record a hazard -- built on
  `scripts/_census_message_interpolations.py`.

One local fix would have closed one site. This closes 28 and goes red on the
29th.

---

## 3. THE REPAIR

### 3.1 `linkedin_server/landing.py`

Every string it can emit is a literal it declares, an integer, or a boolean --
the property `anchors.py` states about its route classifier and `coerce.py`
about its return values.

| field | what it says | alphabet |
|---|---|---|
| `marker` | which `AUTHWALL_MARKERS` entry matched | that tuple, or `none` |
| `host` | where it landed | `HOSTS`, or `another_host` / `no_host` / `unparseable` |
| `route` | the landing's own route class | `ROUTE_CLASSES` |
| **`bounced_from`** | **the route class of the address the landing says it bounced from** | `ROUTE_CLASSES` |
| `path_segments`, `query_params`, `params_with_an_address`, `unnamed_address_params` | integers | -- |
| `named_address_params` | parameter NAMES, only from the closed `ADDRESS_PARAMS` | that tuple |
| `shape` | `jobfilter.describe_shape` -- a length and a set of character classes | the shipped instrument, imported |

**`bounced_from` IS THE FIELD THAT MAKES THIS A REPAIR RATHER THAN A DELETION.**
*You were bounced off a company page* is the diagnosis a debugger needs; WHICH
company page is the leak. The first is a literal from a closed table.

Two disciplines are copied rather than invented. The parameter NAME may be
repeated and only from a closed set -- vocabulary-in / index-out, as
`search_results.py` and `anchors.py` do it -- so a parameter LinkedIn invents
tomorrow is COUNTED, never quoted. And the route table follows `anchors.py`'s
scar: **a route term must be a whole path segment at a fixed position**, never
a substring, because `in` is a substring of `linkedin`.

**THE ROUTE TABLE IS A CHECKED COPY, NOT AN IMPORT.** `anchors` imports `dom`,
and `auth` deliberately keeps its module-level package imports to `config` and
`errors` so the authentication path does not drag the page-reading machinery
behind it. `tests/test_landing.py` asserts every row here is a row there and
every class token is one `anchors.ROUTE_CLASSES` ships, so the copy cannot
drift.

### 3.2 `auth.assert_not_authwall` -- 27 tool-facing call sites, unchanged

The signature and the exception type do not move. Twenty-seven call sites is
the whole reason the repair is inside the function. Nothing is attached to the
exception either, and that is deliberate: `server._error` publishes
`getattr(exc, "url", "")` into the payload **unscrubbed**, so a `url`
attribute here would put the landing back on the wire past every argument
above. `tests/test_landing.py` asserts it is absent.

### 3.3 THE SIBLING IN THE SAME FILE, REACHED BY A DIFFERENT PATH

`auth._maybe_corroborate` had **both halves leaking and only one was obvious**:

* `result["reason"]` quoted the landing -- and `require_auth` raises
  `NotAuthenticatedError(status["reason"])`, so it is the same defect arriving
  as an exception by a second route;
* `result["corroborated_with"]` quoted the same landing on the same branch as
  a plain published FIELD, with no exception involved at all.

The rule adopted is provenance rather than branch: **an address is repeated
only when it is the one this server ASKED FOR.** `_corroboration_note` says so
in code. A query string counts as elsewhere -- `/feed/?highlightedUpdateUrn=
urn:li:activity:<digits>` is the same path and carries an identifier this
repository's own identity gate refuses in a commit.

### 3.4 `writes._assert_landed_on_target` -- 4 sites

Four refusals said `landed on {landed!r}`. **Each is reached exactly when the
landing is NOT what was asked for**, which is the one case where the string is
certainly not ours. A signed-out bounce arrives here as an authwall url
carrying the address it bounced.

`expected`, `want` and `got` are still quoted, deliberately: `expected` is
assembled by this package from a template and a grant target, and `want`/`got`
are the path AFTER the member segment -- route tails that cannot be the member,
and the actual diagnosis of the one failure that branch describes.

**THE MESSAGE IS ALL THAT CHANGED.** No branch, no comparison and no refusal
moved. That is why this was safe to make in a wave that cannot drive a write
gate, and it is the distinction the coercion wave drew when it refused to turn
a gate's `raise` into a substituted zero.

### 3.5 THE LOCAL DIVERGENCE IS KEPT, AND SAID TO BE NO LONGER A DIVERGENCE

`server._authwall_refusal_without_the_landing` now sits on top of a repaired
general case. Its docstring is AMENDED IN PLACE -- a new paragraph above the
original, which is left standing, because a number corrected in place is a
check quietly retired.

It survives rather than being unwound because it is a SECOND, INDEPENDENT
refusal whose message is built from constants alone: it takes no url into its
text at all, where `assert_not_authwall` takes one and describes it. On the two
surfaces where a landing is canonically a name, that independence is worth
keeping.

---

## 4. SHOWN FAILING

### 4.1 THE CONTROL WAS INVERTED, NOT DELETED

`tests/test_company_root.py` shipped
`test_the_shipped_authwall_refusal_publishes_the_slug_it_bounced`, which drove
the SHIPPED function and asserted the slug DID reach the caller. **It went red
on the first run of this repair, which is the leak-closed proof arriving as a
failure.** Its own message said what to do:

> the shipped refusal no longer publishes its landing, so the divergence below
> is buying nothing and should be removed

It stopped being true because the general case was repaired, not because the
divergence was removed -- so it is inverted. Deleting it would have removed the
only test that ever demonstrated the defect.

**AND THE INVERTED ASSERTION MUST NOT BE SATISFIABLE BY AN EMPTY RESULT.**
`_assert_the_landing_did_not_reach_the_caller` checks the absence AND requires
the refusal to still do its job: name its surface, say an authwall happened,
and carry `bounced from company_page`. Beside it,
`test_that_assertion_convicts_the_refusal_that_actually_shipped` hands the same
assertion the pre-repair message, verbatim, and requires it to convict.

**ONE ASSERTION IN THE FIRST DRAFT WAS WRONG AND THE TEST CAUGHT IT.** It
forbade the string `sessionRedirect` outright. The descriptor names that
parameter on purpose -- it is in the declared `ADDRESS_PARAMS`, a parameter
name is LinkedIn's vocabulary and not a third party's text. The assertion is
now `sessionRedirect=` -- the ASSIGNMENT, because a value follows it.

### 4.1a AND THERE WAS A SECOND CONTROL, IN A FILE NOBODY HAD MENTIONED

`tests/test_tools.py::test_an_auth_wall_bounce_is_not_authenticated_not_an_empty_list`
asserted `AUTHWALL_URL in result["message"]` **across six tools**. It was
correct and load-bearing for three weeks -- it held the refusal to naming the
address so a caller could open it -- and it is the same claim as the
`test_company_root.py` control, made about six different surfaces, found only
by running a wider slice of the suite than the wave's own files.

Inverted the same way, and with the same anti-vacuity requirement: the refusal
must still say `signed-out wall`, still name the matched marker `/login`, and
still carry the `describe_shape` reading. **An absence assertion on its own
passes on a refusal that says nothing**, and flipping an assertion to an
absence is exactly where that trap is set.

Its fixture is also the one section 1.4 is about: `AUTHWALL_URL` spells the
redirect as a RELATIVE path, and every real landing measured today spells it
absolute.

### 4.2 `scripts/_check_the_landing_guard_can_fail.py`

Restores the refusal that ACTUALLY SHIPPED at `762ec23`, character for
character, at every binding of the name, and prints how many it replaced. A
control whose defect is the real previous state needs no argument that the
mutation is representative.

    the planted message matches the copy in tests/test_company_root.py

    1. THE TREE AS IT STANDS -- every guard must be GREEN       3 PASS

    2. THE PLANT -- rebound in place
       linkedin_server.auth       DEFINITION
       linkedin_server.server     MODULE_LEVEL
       linkedin_server.writes     FUNCTION_LOCAL
       module attributes replaced: 2

    3. WHAT THE PLANT PUBLISHES, per binding
       linkedin_server.auth       LEAKS the slug
       linkedin_server.server     LEAKS the slug

    4. bindings driven 2, bindings that LEAKED 2                PASS

**THE THIRD LINE OF SECTION 2 IS THE PART WORTH KEEPING.** A control that
counted only module attributes would have reported `writes.py` as a binding it
failed to reach, which reads exactly like a hole. It is a FUNCTION-LOCAL
import, which re-resolves from `auth` on every call and is therefore covered by
the first rebinding -- parsed, not guessed. The count of two is correct and the
script says why.

### 4.3 A SHIPPED GUARD FIRED ON THIS WAVE'S OWN OUTPUT AND WAS NOT DEFUSED

The first version of the repair logged the descriptor as well as raising it.
`test_no_navigation_derived_value_reaches_an_output_sink[auth.py]` went red:
`described` is assigned from `final_url`, the taint walk follows the binding,
and a logger call is one of that rule's output sinks.

**THE GUARD IS RIGHT ABOUT THE TAINT AND THE VALUE IS STILL SAFE.** Four
responses were available and three are dodges:

| response | verdict |
|---|---|
| declare the site in `KNOWN_TAINTED_OUTPUT` | REFUSED -- a false claim in a safety ledger |
| move the log into `landing.py` | REFUSED -- the same value, invisible to a per-module engine |
| rename the variable | REFUSED -- it IS derived; the three-readers rename was legitimate because its value was not |
| **log the surface and nothing derived** | TAKEN |

The log now records THAT an authwall fired and on WHICH surface; the descriptor
is in the refusal, which is what reaches the caller. **Nothing a debugger needs
is lost.** The sanctioned route -- an entry in that file's `_SANITISERS` -- is
left as a measured, named next step; see 6.3 for what it would cost and for the
defect this wave found in the certifier that would have to grant it.

---

### 4.4 AND A SECOND SHIPPED GUARD FIRED ON THIS WAVE'S OWN PROSE

`test_no_committed_identity::test_no_tracked_file_carries_a_real_identifier`
refused three files -- `landing.py`, this document and the register -- for one
made-up four-digit company id used to illustrate the provenance argument in
2.1. It is now the suite's invented `5417062`, already in that file's
`SYNTHETIC_IDS`.

**THE GUARD WAS RIGHT AND THE RULE IS THE POINT: it is on the SHAPE, because a
reviewer cannot tell an invented id from a real one.** That is the same
reasoning `tests/test_group_page.py`'s urn literal met yesterday. The gate was
verified ARMED in this worktree as well -- it printed no
`wordlist absent; ALLOWING` line, which is what a disarmed run says.

**ONE HONEST GAP: the exact-value gate was not shown failing by this wave.**
Constructing a positive control for it means putting a value from the
operator's real gitignored wordlist into a staged file, which is the thing the
gate exists to stop. The SHAPE half above was shown failing, on this wave's own
files, without anybody arranging it.

---

## 5. THE SIBLING SWEEP

`scripts/_census_message_interpolations.py` (AST, not grep) over
`linkedin_server/`: **292 message-bearing sites in 24 modules, carrying 539
interpolated sub-expressions** -- 114 RAISE, 88 LOG, 90 FIELD. Hazard bucket
**69 sub-expressions across 61 sites in 9 modules**; `UNCLASSIFIED` is 158 and
was not forced empty, because a residual bucket of zero would mean this file
had solved static analysis.

**THE INSTRUMENT PRINTS A SUBJECT DIGEST, AND THE REASON IS THIS WAVE.** Its
first run reported 76 hazard sub-expressions and a 19-row shortlist; every run
after it reported different figures from a byte-identical instrument. Nothing
was nondeterministic -- **this repair was landing in the same worktree while
the census ran, and the denominator moved.**

> A COUNT OVER A TREE SOMEBODY ELSE IS EDITING IS A READING WITH A TIMESTAMP,
> NOT A FACT ABOUT THE CODEBASE.

So it counts HEAD and the working tree separately and prints both. The figures
above are the working tree with the repair in it. At `762ec23` the hazard
bucket is 75.

### 5.1 THE UNDERCOUNT IS THE HALF THAT MATTERS

| | grep lines | AST sites |
|---|---:|---:|
| whole package | **18** | **292** |

The naive search is "a raise or a logger call with an f-string in it".
**All 88 LOG sites have no f-string anywhere**: the format string is a plain
constant and `logging` does the interpolation, so `logger.info("landed on %s",
final_url)` reaches a log record with the url in it and a grep for `f"` cannot
see one of them. Multi-line `raise` calls -- the dominant spelling here -- are
invisible to the same search for the same reason.

**AND THE TABLE PRINTING THAT CONTRAST DID NOT RECONCILE, WHICH I FOUND BY
RUNNING THE GREP MYSELF.** An independent ripgrep returned 18, agreeing with
the TOTAL -- and four of those lines were in three modules the table never
mentioned. The rows summed to 288 against a printed 292. The cause is benign
(the table shows DISAGREEMENTS only, which is the useful view) and the defect
is not: **a printed total that the visible rows do not reach invites a reader
to trust a row that is not there.** The suppression is now stated and counted
in the table's own output.

> RUNNING THE CHEAP DISAGREEING CHECK IS HOW TWO OF THIS INSTRUMENT'S THREE
> DEFECTS WERE FOUND -- a grep against its shortlist, and a grep against its
> own grep. The third was found by a shipped guard, and it is the worst of
> them.

### 5.1a AND THE CONTRAST COULD HAVE BEEN MANUFACTURED FROM NOTHING

`test_an_outage_is_never_filed_as_an_absence` refused this wave's own new
script:

    _census_message_interpolations.py:1225
    A zero from a failed read and a zero from an empty surface are the same
    number and different findings.

Two handlers answered an unreachable version-control tool with `""` and `{}`.
**That turns an OUTAGE into an ABSENCE, and here it does so in the direction
that flatters this census's own thesis:** with the tool gone, the contrast
table prints a naive-search count of ZERO beside 292 AST sites, which is the
strongest possible evidence for *"a text search cannot see this class"*,
measured from nothing at all. The number this whole section rests on was one
missing binary away from being fabricated by its own error handling.

Both handlers now raise `CensusOutage`. Shown failing, by running the census
with the tool off `PATH`:

    CensusOutage: the version-control tool could not be run
    (FileNotFoundError); this census cannot report a HEAD comparison or a
    contrast it did not measure

The search-tool handler separates the two cases by RETURN CODE rather than
flattening them -- exit 1 means "matched nothing", which is a real reading;
anything else is an outage.

### 5.2 THE ADJUDICATION -- 21 ADDRESS-BEARING SITES

| site | verdict |
|---|---|
| `auth.assert_not_authwall` raise | **REPAIRED** |
| `auth._maybe_corroborate` `reason` | **REPAIRED** -- becomes an exception via `require_auth` |
| `auth._corroboration_note` (`corroborated_with`) | **REPAIRED** |
| `writes._assert_landed_on_target` x4 | **REPAIRED** |
| `readonly.assert_read_url` x3 | NAMED -- refuses the url it was HANDED; `test_navigation_is_never_derived` is the standing proof that no navigation target is page-derived, so the quoted value is one this package or its caller composed |
| `writes.assert_write_url` x3 | NAMED -- same, and `assert_write_url` REBUILDS the url from the grant |
| `writes._render` `where["url"]` | NAMED -- `spec.url_template.format(target=url_target_of(...))`, assembled from a template this package authored |
| `browser.goto` raise | NAMED -- the url it was asked to open, not a landing |
| `auth.login_via_browser` log | NAMED -- `LOGIN_URL`, a config constant |
| `transport._serve` log | NAMED -- this server's own bind address |
| `server.linkedin_job_detail` `out["url"]` | NAMED -- `f"{BASE_URL}/jobs/view/{digits}"`, assembled from a caller value already proven digit-only |
| `server._read_tracker` note | **NOT AN ADDRESS** -- it matches the source-text rule through exactly one substring, the `href` inside `href_pattern=dom.JOB_HREF`, and `JOB_HREF` is a REGEX. There is no landing here to withhold |
| `dom.read_job_identity` `out["company_url"]` | NAMED -- published by contract on the success path |
| `shape.parse_person_card` `out["profile"]` | NAMED -- `linkedin_connections` publishes `rows_are_not_redacted` beside it |

**21 SITES EXAMINED. 7 REPAIRED, 13 NAMED, 1 NOT AN ADDRESS AT ALL.**

The census's own shortlist is **19** -- 14 raw and 5 it recognises as routed
through `landing.withheld()`. **THE TWO IT CANNOT SEE ARE BOTH MINE, AND THEY
NAME ITS TWO BLIND SPOTS:**

* `assert_not_authwall`'s raise interpolates `described`, a name that carries
  no address token, so a SOURCE-TEXT rule over expression names cannot reach
  it. That limit is real and is stated in the guard's own docstring rather
  than left for somebody to discover.
* `_corroboration_note` BUILDS the message and RETURNS it; the field
  assignment that publishes it is `result[...] = _corroboration_note(...)`,
  whose value is a Call and not a built string. **A message built in a helper
  is invisible to a walk that looks at assignment sites** -- the same
  crosses-a-function-boundary shape as 6.2.

### 5.3 THE LAW THAT DECIDES EVERY "NAMED" ROW

It is the coercion wave's, one class over:

> RETURNING PAGE TEXT CAN BE A CONTRACT. RAISING A `ValueError` THAT QUOTES
> PAGE TEXT IS NOBODY'S CONTRACT.

Restated for this class: **a message is never a contract; a field can be.** No
tool in this package declares "my refusal names the landing" -- that string was
nobody's promise, which is why it had no defenders. `out["profile"]`,
`out["company_url"]` and `source_url` are declared publications with readers
who depend on them, and `tests/test_the_source_url_split_was_never_ruled.py`
already governs the last of those per site while explicitly forbidding a
reflexive wrap:

> Wrapping a deliberate publication is as much a defect as leaking an
> accidental one: it silently breaks a tool's contract, and the next reader
> cannot tell which shapers were reasoned and which were reflexive.

### 5.4 MY OWN CENSUS MISSED ONE, AND GREP FOUND IT

The shortlist reported 3 sites in `writes._assert_landed_on_target`. There are
**four** `{landed!r}` interpolations; the fourth `raise`'s argument is a BinOp
of a JoinedStr and an IfExp, and the walk attributed it elsewhere. It was found
by a `grep -n "{landed"` cross-check against the instrument's own output.

**AN AST CENSUS IS NOT AUTOMATICALLY THE COMPLETE ONE.** It is a better
instrument than grep in both directions, and it is still an instrument, and
running the cheap disagreeing check is what caught this. The instrument was
repaired and now reports all four; **the number moved because the instrument
got better, which is the only honest reason a number may move.**

---

### 5.5 THE STANDING GUARD, AND ITS FIVE VERDICTS

`tests/test_no_message_publishes_a_landing.py` walks the package through the
census -- **imported, never re-implemented, because two copies of one walk
drift and the drift is invisible** -- and holds a verdict for every discovered
address-naming site in `tests/landing_interpolation_baseline.json`:

    WITHHELD               5   routed through landing.*()   MEASURED
    SERVER_CONSTRUCTED     4   a constant or this package's own template
    ASKED_FOR              7   the address REQUESTED, not one landed on   RULED
    PUBLISHED_BY_CONTRACT  2   a field the success path publishes too     RULED
    NAMES_NO_ADDRESS       1   dom.JOB_HREF -- a regex that spells `href`

**`NAMES_NO_ADDRESS` WAS DECLARED AND UNUSED IN THE FIRST DRAFT**, because its
one real site had been filed under the less accurate
`PUBLISHED_BY_CONTRACT` -- a safety class -- when it is not an address at all.
The guard now asserts that every declared verdict is assigned somewhere:

> A CATEGORY THAT NEVER FIRES HAS NOT BEEN TESTED, IT HAS BEEN ASSUMED.

and an unused escape hatch in a file whose central claim is *there is no
verdict meaning "allowed to publish a landing"* is exactly the thing that
claim cannot afford.

**THERE IS DELIBERATELY NO VERDICT MEANING "THIS PUBLISHES A LANDING", AND THE
WRITER REFUSES TO EMIT A FILE CONTAINING AN UNRULED SITE.** A baseline that can
record a permitted leak becomes a list of permitted leaks within one commit of
somebody being in a hurry -- `tests/reader_leak_baseline.json`'s own reasoning,
applied to a second class. `UNRULED` is a failure, not a bucket, so a new
address-naming message goes red on arrival.

Two controls, both planting a synthetic module source parsed by the census and
never written into `linkedin_server/`: a new unruled site must be reported as
NEW, and a `WITHHELD` site reverted to the bare value must be reported as
CHANGED. A third asserts the two planted subjects really differ, so the first
two cannot both be passing on the same input.

**AND IT STATES WHAT IT DOES NOT COVER**, in its own docstring: it is a
SOURCE-TEXT rule over expression names, so a landing bound to `destination` or
`target` is invisible to it; it reads names, not values; it does not run the
code, so reachability is a different question; and the census behind it does
not see a message assembled across a function boundary by a helper.

---

## 6. WHAT IS STILL OPEN, MEASURED AND NAMED

### 6.1 `ExtractionFailedError.url` -- THE LARGEST OPEN DOOR, AND IT NEEDS A RULING

`server._error` builds the failure envelope:

    out = {"error": exc.kind, "message": scrub(str(exc))}
    url = getattr(exc, "url", "")
    if url: out["url"] = url                 # <-- NOT SCRUBBED. Not at all.
    hint = getattr(exc, "hint", "")
    if hint: out["hint"] = scrub(hint)

**`url` is the one field in the error envelope that passes through with no
scrubber.** Scrubbing it would achieve nothing anyway -- scrub knows only paths
-- so "not scrubbed" is not the defect. The question is whether the value may
be published. Measured by AST over `linkedin_server/`:

| what feeds it | sites | where |
|---|---:|---|
| `_url_of(page)` -- **the live page url read at the moment of the raise** | 12 | `dom.py` |
| the `url` parameter of `dom.require_rows` | 1 | `dom.py` |
| `final_url` / `last_url` | 7 | `server.py` (2 of them via `require_rows`) |
| **total** | **20** | |

Its own docstring declares the contract: *"Carries the url so the operator can
open the same page by hand and see what this server saw."*

**THE MECHANISM IS MEASURED, NOT READ.** Driven offline against the SHIPPED
code with a synthetic name-bearing authwall landing:

    dom.require_rows([], url=<a /company/<slug>/ authwall landing>, ...)
      -> ExtractionFailedError
      -> server._error(exc)["url"] CARRIES THE SLUG VERBATIM

**AND SO IS REACHABILITY, FOR ALL TWELVE `dom.py` SITES: 12 DRIVEN, 0 NOT
DRIVEN, 12 PUBLISHING THE PLANT AT `$.url`.** `reached` is asserted from the
TRACEBACK -- the deepest `dom.py` frame must be the target function at the
expected line -- because three of these readers can raise the same class from a
neighbour's site, so "the right exception came out" is not the measurement.
The envelope is byte-for-byte: no shaping, no substitution, no truncation.

### AND MY OWN FIRST ATTEMPT MEASURED NOTHING, WHICH IS THE LESSON

I drove eight of them with a page double that answers empty; not one reached
its raise, and I was one step from recording them UNMEASURED. **That was a fact
about the double.** Every one of the twelve has the same shape:

    try:
        data = await page.evaluate(<one module-level script constant>, cfg)
    except Exception as exc:
        raise ExtractionFailedError(..., url=_url_of(page)) from exc

> **THE GUARD IS ON THE CALL, NOT ON THE ANSWER.** A page that answers empty
> has RETURNED; it walks past the `except` and down the normal path. **No empty
> answer of any shape can reach any of these twelve raises.**

So reachability reduces to one question -- can `page.evaluate` raise for that
script -- and `except Exception` catches every class, which makes each site
reachable BY CONSTRUCTION. The probe drives it by making `evaluate` raise for
exactly one script object, chosen by identity against the `dom` constant. That
per-script selectivity is load-bearing rather than tidy: `read_job_insight_panels`
opens by awaiting `read_profile_fields`, so a double that raised for every
script would send the job reader out through line 803 and record the wrong site.

**THE HONEST LIMIT.** This is CODE-LEVEL reachability. It does not prove that a
live authwall bounce makes `page.evaluate` raise on these surfaces -- in
production the raising classes are Playwright's `Error` (execution context
destroyed by a navigation mid-evaluate) and `TimeoutError`, and whether the
bounce produces one on each surface is a browser measurement this wave could
not take.

### A REMEDY SCOPED TO `_url_of(page)` WOULD MISS SEVEN MORE SITES

All twelve are `_url_of(page)` -- confirmed by unparsing the argument from the
AST, so a keyword split across lines cannot fake it. But the same unscrubbed
field is fed a landed url from seven sites that are NOT that expression:
`dom.require_rows` (from `server.py:1074` and `server.py:5327`, both
`url=final_url`) and five `server.py` raises -- `_read_tracker`,
`linkedin_who_viewed_me`, `linkedin_job_detail`, `linkedin_followed_companies`
and `linkedin_my_profile`.

### AND A SECOND CHANNEL ON THE SAME TWELVE

Every one of their messages is built `f"...: {type(exc).__name__}: {exc}"`, so
whatever the BROWSER put in its own exception reaches `out["message"]`,
scrubbed for paths only. A second needle planted ONLY inside the exception
`page.evaluate` raised landed at `$.message` in all 12 drives. That is the
`EXCEPTION_TEXT:arbitrary` bucket of 6.5, measured to carry a value through
rather than argued about.

**THE FINDING IS AN ASYMMETRY, AND IT IS NEW.** The SUCCESS-path twin of this
value has a standing, per-site, fourteen-row ruling in
`tests/test_the_source_url_split_was_never_ruled.py`, which declares most rows
UNMEASURED and says closing one means MEASURING it. **The FAILURE-path field
has no such ruling at all** -- same value, same variable, same function -- and
it is reached exactly when the page was NOT what was expected, which is when
the landing is least likely to be the address we asked for. The twelve
`dom.py` sites are the sharpest: `page.url` at raise time can differ from the
`final_url` the authwall gate saw.

NOT REPAIRED, and reflexively wrapping it would be the defect that file exists
to refuse. What it needs is the same treatment: a per-site declaration, and a
measurement to close a row.

### 6.2 A SHIPPED TAINT GUARD HAS TWO LAUNDERING CONSTRUCTS, AND ONE IS NEW

`scripts/_probe_file_inputs_live.py` prints a landed url and is NOT in
`KNOWN_TAINTED_OUTPUT`. Measured: it is in the scanned set,
`output_violations` returns `[]` for it, and the declared set is `[]`.

Isolated with synthetic modules against the shipped `output_violations`:

| construct | caught |
|---|---|
| `print(landed)` | YES |
| `lines.append("..." + landed)` then `print(join(lines))` | **NO** |
| `lines = lines + ["..." + landed]` then `print(join(lines))` | YES |
| returned in a dict, printed by subscript in another function | **NO** |
| returned in a dict, printed by BARE NAME in another function | YES |

The dict-subscript row is already recorded in
`scripts/_probe_compose_file_inputs.py`'s own comment. **The `.append` row is
not recorded anywhere**, and the rebinding form being CAUGHT is what localises
it: the gap is precisely that **mutation is not assignment**. That is the same
shape as the hole `_bindings` records learning once already -- *"ITERATION IS A
BINDING, AND THIS ENGINE DID NOT KNOW THAT UNTIL 2026-09-20"*.

**AND THE LEDGER CANNOT RECORD WHAT THE ENGINE CANNOT SEE.** The guard asserts
`found == declared` by equality, so declaring the probe's site without first
teaching the engine `.append` makes the test RED with a declaration it cannot
match. The undeclared site cannot be declared; it can only be fixed.

NOT FIXED. Modelling `.append` in `_bindings` changes the verdict for every
scanned file, including `scripts/` files other waves are writing right now, and
the drift test `test_the_two_walkers_bind_the_same_forms` means the page-text
walker has to move with it. That is a wave, not a line.

### 6.3 THE SANITISER ENROLMENT, AND A DEFECT IN THE CERTIFIER THAT WOULD GRANT IT

`landing.withheld` is a genuine `_SANITISERS` candidate: it takes a landing and
returns literals, and it ships with the test that proves the contract, which is
the bar `tests/test_a_sanitiser_earns_its_entry.py` sets. Enrolling it would
let the log carry the descriptor again.

**IT CANNOT BE ENROLLED TODAY, AND THE REASON IS A MEASURED DEFECT IN THE
CERTIFIER.** That file's `_module(filename)` resolves every claimant as
`REPO / "scripts" / filename`, while its `_claimants()` scans
`_python_files()` -- which includes **46 files in `linkedin_server/`**.
Measured:

    _module("landing.py")  ->  FileNotFoundError

So a claimant in `linkedin_server/` is DISCOVERABLE by the enumeration guard
and UNLOADABLE by the demonstration guard. No such claimant exists yet, which
is the only reason nobody has met it. A `linkedin_server/` function named
`_redact`, `_shape_of` or `_relation` -- three very ordinary names -- would fail
the enumeration half and crash the demonstration half, and the fix for the
first would trip the second.

Left for its owner. Enrolling would also mean widening `_SANITISERS` and the
name pin, on two shared guard files, from a wave whose subject is a different
thing.

### 6.4 THE `hint` THAT CARRIES PAGE HEADINGS -- MEASURED

`linkedin_my_profile` raises with
`hint=f"headings seen: {[s.get('heading') for s in sections]}"`, where
`sections` comes from `dom.read_profile_fields(page)`. Driven, not read: that
exception through `server._error` yields `out["hint"] = "headings seen:
['<needle>']"` with the needle intact at `$.hint`. `scrub` substitutes this
server's filesystem paths and nothing else, so page text passes through it
untouched -- the same property that lets the url through.

It is the ONLY page-derived `hint` in the package. The other `hint=` values are
two fixed English sentences.

**NAMED, not a defect of this class**: the same list is published on the
SUCCESS path as `headings_seen`, so it is the tool's own contract, which is
exactly the distinction 5.3 draws. Its being the tool's contract is why it is
not repaired here; its being MEASURED is why it is not merely asserted.

### 6.5 THE 89 `{exc}` SUB-EXPRESSIONS, AND THE ONE I COULD MEASURE OFFLINE

The census's largest non-safe bucket is `EXCEPTION_TEXT:arbitrary` -- **89
sub-expressions**, and it resolved the enclosing handler rather than guessing:

    'except Exception'              86
    'except OSError'                 3
    'except ExtractionFailedError'   1

So essentially every `{exc}` in this package is rendered under a handler that
catches ANYTHING, and whatever Playwright or the standard library put in that
message is what gets interpolated. `config.scrub` removes only the paths. **A
THIRD PARTY COMPOSES THAT TEXT, WHICH IS THE ONE CASE WHERE THIS PACKAGE HAS NO
SAY IN WHAT IT SAYS.**

`browser.goto` is the site where it matters most:

    raise BrowserUnavailableError(
        f"navigation to {url} failed: {type(exc).__name__}: {exc}"
    ) from exc

The `{url}` half is `ASKED_FOR` and is in the baseline. The `{exc}` half is
Playwright's. **Measured offline, from the shipped driver source** -- the only
route available to a wave with no browser -- both navigation-failure templates
interpolate the REQUESTED url and not the landing:

    playwright/driver/package/lib/coreBundle.js

      progress2.log(`navigating to "${url3}", waiting until "${waitUntil}"`)
      throw new NavigationAbortedError(loaderId, `${errorText} at ${url3}`)

`url3` is `goto`'s own argument. So for the navigation case the provenance of
the embedded address is the same as `{url}`'s, and the bucket is narrower than
it looks.

**THAT IS A SOURCE READING, NOT A DRIVEN ONE, AND IT COVERS TWO TEMPLATES OUT OF
A BUNDLE.** It does not clear the other 87 sub-expressions, and it cannot: a
Playwright selector error quotes a selector, a redirect-chain diagnostic could
in principle name a hop. Closing that properly means driving a real failure
against a real browser, which this wave was forbidden.

**AND THE CHANNEL ITSELF IS MEASURED TO CARRY A VALUE THROUGH**, which is the
half that does not need a browser: a needle planted only inside the exception
`page.evaluate` raised reached `out["message"]` in all 12 drives of 6.1. So the
question is never *can this channel carry a name* -- it can, demonstrably --
only *does anything put one in it*. That is the right shape for the open item,
and it is narrower and sharper than "89 unclassified sites".

### 6.6 CALLER-SUPPLIED NEEDLES

9 sub-expressions across the package interpolate a tool argument back into a
refusal. That is the caller's own string returning to the caller, which is a
different question -- **and not a clean bill: a caller-supplied needle can
still be a third party's name.** Untouched here; it is decision `D1` in
`_audit/2026-09-21-the-read-triage.md`, which nobody has ruled.

---

## 7. EVERY NUMBER HERE IS RE-DERIVABLE

    venv/Scripts/python -m pytest tests/test_landing.py -q
      -> 60 passed

    venv/Scripts/python -m pytest tests/test_company_root.py tests/test_auth.py \
        tests/test_navigation_is_never_derived.py tests/test_page_text_is_never_printed.py -q
      -> 596 passed

    venv/Scripts/python -m pytest tests/test_tools.py -q
      -> 124 passed  (6 were RED before the control was inverted, section 4.1a)

    venv/Scripts/python scripts/_check_the_landing_guard_can_fail.py
      -> PASS, 2 bindings driven, 2 LEAK under the plant

    venv/Scripts/python scripts/_census_message_interpolations.py
      -> 292 sites / 24 modules / 539 sub-expressions; grep contrast 18;
         shortlist 19 = 14 raw + 5 routed through landing.withheld()

The interpreter is the one in the MAIN checkout; a worktree carries no
gitignored files and therefore no `venv/`. **No script here resolves an
interpreter as `REPO / "venv" / ...`** -- that construction is absent in every
worktree and has been repaired four times in two days.

---

## 8. INSTRUMENTS

| path | disposable? |
|---|---|
| `linkedin_server/landing.py` | shipped code |
| `tests/test_landing.py` | **REGISTER** -- the alphabet proof and its two red controls |
| `scripts/_check_the_landing_guard_can_fail.py` | **REGISTER** -- shows the guard failing on the state that shipped |
| `scripts/_census_message_interpolations.py` | **REGISTER** -- the enumeration, with the grep contrast printed |
| `tests/test_no_message_publishes_a_landing.py` | **REGISTER** -- the discovering guard |
| `tests/landing_interpolation_baseline.json` | **REGISTER** -- the coverage record; refuses to hold a hazard |

---

## 9. THE LEDGER LINE

One function, 27 tool-facing call sites, one message. The convention everybody
had been asserting about LinkedIn's authwall turned out to be true and to have
been sitting unmeasured in a browser profile for four weeks; the part that made
it severe is still derived and is now labelled as such. Seven sites repaired,
thirteen named, and the biggest remaining door is a FIELD with a contract --
which is why it gets a ruling rather than an edit.
