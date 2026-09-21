# Two readers for three rows, on two addresses nothing could navigate to --
# and the accessible copy is what the control convicts.

Wave `three-readers`, 2026-09-21, from master `9dbaad2`.
Scope: census rows `N 33`, `N 54` and `N 175`, the three of the read triage's
nineteen that need a READER over an admitted address rather than a browser slot.
No browser was opened. No LinkedIn page was loaded. No write was fired. Every
number below is offline, against the shipped predicate, committed fixtures and
the shipped in-page script driven under V8.

---

## 0. THE ANSWER, FIRST

All three rows moved **GAP -> COVERED-UNFIRED**. None moved to COVERED-PROVEN
and none should until somebody fires them, because this wave was forbidden the
browser and the census's own definition of PROVEN is *an audit records it firing
live and returning what it claims.*

    N 175   linkedin_group_page(group_id)              group_page.py
    N 33    linkedin_company_page_counts(org_id)       company_root.py
    N 54    the same tool, the same page load          company_root.py

**Three rows, TWO readers, and one page load each.** `N 33` and `N 54` are two
phrases in one closed table on one surface; building two tools for them would
have been two navigations to read two lines off one card.

    census GAP        285 -> 282      scripts/count_census_states.py
    COVERED-UNFIRED    19 ->  22      --expect J=57,P=55,M=82,N=88
    tool surface       47 ->  49      two READS, no write
    tool parameters    64 ->  66      two numeric identifiers, no needle
    evaluate waivers   21 ->  22      ONE, and the group reader spends none

---

## 1. WHAT EACH ROW NEEDED, RE-DERIVED RATHER THAN ACCEPTED

Every address was re-confirmed against the shipped predicate at this tree
before anything was written:

    readonly.is_read_url("https://www.linkedin.com/company/<10 digits>/")  True
    readonly.is_read_url("https://www.linkedin.com/company/<slug>/")       True
    readonly.is_read_url("https://www.linkedin.com/groups/<8 digits>/")    True

and so were the refusals the readers must not reopen:

    .../company/<id>/people/     False      the member roster, J 108 / N 102
    .../groups/<id>/members/     False      the member roster, N 165
    .../company/                 False      the product root, not a Page

Both allowlist entries said, in their own words, that nothing could navigate to
what they had opened. The groups entry:

> CONDITION 4 -- [...] It builds no tool, and **no tool in this package can
> navigate to either** [...] and the one group tool takes no parameter at all.

The company entry:

> No tool in this package navigates to this address today. `company_page.py`
> opens nothing and has no page function.

Both sentences are true as dated measurements and both are now amended IN
PLACE rather than rewritten -- the amendment is a new paragraph beside the
original, because a number corrected in place is a check quietly retired.

---

## 2. `N 175` -- AND THE OBLIGATION WAS PAID BY REUSE, NOT BY A SECOND SHAPER

The `/groups/<id>/` entry attached a price to being first:

> `/groups/<id>/` DRAWS A GROUP FEED -- other members' posts in full. This list
> decides what may be OPENED and the shaper decides what may be SAID [...]
> **Whoever writes the first reader for this address owes it a shaper as strict
> as the search-results one.**

**THE PRICE WAS PAID BY NOT BUILDING A SECOND INSTRUMENT.** What makes
`search_results.py` strict is the vocabulary-in / index-out engine, and
`anchors.py` already ships that engine over a route table carrying
`member_profile` at index 0 and `feed_update` -- the exact two classes a group
feed is made of. So `group_page.read_group_page` calls `anchors.read_anchors`.

    no new script injected
    no new vocabulary shipped into a page
    the evaluate waiver budget does not move for this row
    dom.py gains nothing at all for N 175

That is this repository's own law -- *import the shipped instrument* -- applied
where the pull to rewrite was strongest, and it lands on the sharper side of
the trade as well as the cheaper one: the shipped classifier already refuses
the thing a fresh one would have had to be told about, because a raw href on
this page carries `/in/<slug>` and a slug is a name.

### What the row actually asks, and why the answer is a verdict

*Reach a private unlisted group through a direct link or an invitation.* The
question is whether the link REACHES, not what the group says. `reachability`
answers it from integers:

    feed_drawn      feed permalinks rendered -> the link reached a group this
                    account can see
    reader_blind    the page drew no anchor at all -> a fact about the READER
    off_group       the navigation did not stay on the group it was sent to
    ambiguous       rendered, and no feed permalink

**`ambiguous` IS THE HONEST BRANCH AND IT IS NOT A HEDGE.** A membership gate,
an empty group and a restyle that moved the permalink each produce a rendered
page with no permalink on it, and nothing in this process can separate them --
there is no known-gated group id in this repository to calibrate against.
`groups_page.interpret_zero` refuses the identical branch on the identical
grounds. *A reading no instrument can fail is not a reading*, and the flattering
branch here would assert that a private group was reached on the evidence that
nothing was.

### The invitation half is the same address

A direct link to a group carries its token in the query --
`/groups/<id>/?invitedBy=<token>` -- and `groups.group_identifier` discards the
query **before any marker is looked for**, so no branch below it can read one.
`tests/test_group_page.py` drives exactly that url and asserts the landing
comparison still answers True.

---

## 3. `N 33` AND `N 54` -- A COUNT, NEVER A LIST, AND THE NUMBER IS READ IN THE
## PAGE

`linkedin_company_page_counts(organisation_id)` builds `/company/<digits>/`
through `company_page.company_page_url` -- which assembles the NUMERIC form
only, because *a slug is a name* -- opens it, and runs one script that answers
with positions and integers.

The caller never has to type an id: `linkedin_job_detail` already publishes
`company_page_url`, built from a numeric organisation id read off the posting's
insights panel.

### Why a new script, when the group reader needed none

The group reader classifies ANCHORS, and a classifier for those already ships.
These two rows are a NUMBER BESIDE A PHRASE, and nothing in the package reads
that shape. The three candidate routes, and why two were refused:

    a locator chain (no waiver)        REFUSED. get_by_text(...).count() can
                                      say the line was drawn; it cannot say
                                      what number is in it.
    inner_text into Python             REFUSED. This is the burned route: the
                                      same line renders twice, an aria-hidden
                                      visible copy beside a screen-reader copy
                                      that carries a person's name, and
                                      innerText was already proven to leak the
                                      clip-style pattern on this repository.
                                      Pulling the line out to parse it in
                                      Python puts the name in the process.
    one script, integers out           TAKEN. The comparison happens where the
                                      strings are; a POSITION and a NUMBER
                                      come back.

`dom.COUNT_LINES_JS`, run once from `dom.read_count_lines`. Declared in
`tests/test_readonly.py`'s `INJECTED_SCRIPTS`, scanned for mutating tokens like
every other, and the waiver budget moved 21 -> 22 in the same edit.

### THE ACCESSIBLE COPY IS STEPPED OVER, AND COUNTED

`dom.CARD_HIDDEN_SELECTOR` is the selector this package already knows
screen-reader spans by, and **it had never been wired to a reader that
assembles text.** `COUNT_LINES_JS` is the first one. It does not clone the node
and take the copies out; it WALKS and steps over any subtree matching that
selector, and returns `hidden_skipped` so the exclusion is an integer a caller
reads rather than an assurance a docstring makes.

Nothing on the page is changed and nothing is detached. The obvious
implementation builds a copy and removes nodes from it; this one never builds a
copy, because a walk that skips is the same answer with no shape for a future
edit to turn into a real page mutation.

### A phrase that did not render is NOT a count of zero

    reader_blind       the walk visited no element -> about the READER
    phrase_not_drawn   the walk ran and no shipped phrase matched
    numeral_refused    the line rendered and the number was unusable
    disagreement       two phrases of one kind, two different numbers
    count_read         the integer

`phrase_not_drawn` never carries a value and says so in its own `why`. That
matters more here than anywhere else in this wave, because of section 5.

### An abbreviation is refused, never rounded

`2K connections` is not two thousand as far as this reader is concerned; it is
`abbreviated_refused`, with no value. `1.5` is `decimal_refused` and not
fifteen. **A wrong number that looks right is worse than no number**, and a
decimal read as a grouped run is exactly that shape.

---

## 4. NAME-FREE BY CONSTRUCTION, ARGUED PER READER

### The return values

Both readers return integers, lists of integers, booleans, and literals drawn
from closed tuples declared in their own modules. There is no path by which a
document string becomes a return value: the group reader's document contact is
`anchors.read_anchors`, whose script answers with a POSITION in a table
`anchors.py` defines; the company reader's document contact is
`COUNT_LINES_JS`, which answers with a POSITION in a table `company_root.py`
defines plus a number.

### The exceptions

**AN EXCEPTION IS NOT A RETURN VALUE.** Nothing in either module calls `int()`
on anything the page chose. Every field arrives through `coerce.as_int` /
`as_count` / `counts_only` / `scalars_only`, none of which raise and none of
which quote their input. Both modules are in the standing subject set of
`tests/test_readers_emit_no_page_string.py` -- which DISCOVERS readers rather
than listing them, so they were enrolled the moment they were written -- and
both measure **clean** in `tests/reader_leak_baseline.json`:

    company_root:read_company_root   clean
    group_page:read_group_page       clean

Each test file also drives its module with the planted page that answers every
key with a person-shaped name and asserts the plant reaches no field, in a
value or in a raise. Beside it sits the control that the hazard is real: `int()`
on the same input raises quoting it, and `coerce.as_int` on the same input
returns `None`.

### The refusals

The one function in each module that takes an identifier reports a SHAPE and
never the value, through `jobfilter.describe_shape`. That is the rule
`jobfilter.py` set and `company_page.py` restated, and the reason imports
unchanged: the single most probable wrong value on both surfaces is a SLUG, so
a rule-following `got {candidate!r}` would publish a third party's name on the
commonest mistake.

    group_page.group_page_url("<a person-shaped slug>")
      -> refused identifier_is_not_numeric,
         saw "38 characters, containing letters + hyphen-or-underscore"

### The parameters

Asserted on `inspect.signature` in both test files, the way `groups.py`,
`search_results.py` and `company_page.py` assert it: exactly one coroutine per
module, no parameter named `name`, `url`, `href`, `slug`, `query`, `keywords`,
`text` or `label`, and no `confirm_token` anywhere.

---

## 5. WHAT IS STILL A GUESS, AND IT IS ONE CONSTANT

`company_root.COUNT_PHRASES`. **Nobody in this repository has ever opened a
company Page** -- `company_page.py` says so in its own last line -- so the exact
words LinkedIn draws beside these two numbers are unmeasured. Six phrases ship,
singular and plural, and the first live fire of this tool is two measurements at
once: whether the count is there, and whether these are its words.

**A WRONG PHRASE COSTS A MISSING READING AND NOTHING ELSE.** It cannot produce a
wrong number, because a number is published only when a phrase this package
shipped was found word-bounded in a short line; and it cannot produce a name,
because no string from the document crosses the boundary at all. The reading
comes back `phrase_not_drawn` with `elements` and `chunks` beside it, so "the
line was not drawn" and "the reader saw nothing" stay different answers.

That is the honest shape of this half of the wave and it is why the census cell
says it too rather than only this document. It is also why these rows are
UNFIRED: the first fire is the measurement.

`N 175`'s reading rests on no invented vocabulary at all. It is anchors.

---

## 6. THE GUARD, SHOWN FAILING, AND WHAT THE FAILURE ACTUALLY PROVES

`dom.COUNT_LINES_JS` is the only thing that runs in the page, so a Python
re-implementation of its rules would be the second disagreeing copy this
repository already has a scar for. `tests/test_company_root.py` therefore runs
**the shipped constant itself, under V8**, over a synthetic node tree built from
`company_root.control_tree()` -- node has no DOM, so the tree is supplied and
the script is untouched.

The fixture's first group is the whole point and its shape is deliberate: the
screen-reader copy is SHORTER than the visible line and carries a DIFFERENT
number. Because the tightest phrase-bearing container wins, a walk that does not
step over that copy reads the wrong one.

    shipped script                      connections_at_organisation = 11
    one line replaced, skip removed     connections_at_organisation = 41
    hidden_skipped                      2  ->  0

**AND THE HONEST HALF: NEITHER BUILD LEAKS.** The planted name does not reach
the output in either run, because the return value is integers by construction.
The exclusion buys a CORRECT NUMBER; name-freedom is bought one layer down and
does not depend on it. That is asserted as its own test, so nobody removes the
skip believing they have only loosened an accuracy check.

Three other controls in the same file are shown failing by construction rather
than by narration: the numeral shapes are driven under V8 over an abbreviation
and a decimal and both come back refused; the phrase table is asserted
self-normalised and mutually non-containing; and
`test_the_planted_defect_anchor_is_still_in_the_shipped_script` fails loudly if
the line the defect is planted into ever moves, so the control cannot silently
become a control of nothing.

`tests/test_a_covered_row_names_the_artifact_that_covers_it.py` gains the three
rows and a chain test binding them to the code, plus a control that drives the
same predicate over a renamed copy of each module and asserts it convicts.

---

## 6b. AN EXPOSURE THIS SURFACE MAKES REACHABLE, FOUND AFTER THE READERS WERE
## WRITTEN, AND CLOSED LOCALLY

`auth.assert_not_authwall` interpolates the FINAL url into its refusal. That
message reaches `server._error`; `config.scrub` substitutes THIS SERVER'S OWN
FILESYSTEM PATHS and nothing else. It is the coercion-leak class one layer
over: the value does not leave in a return field, it leaves in an exception.

**LINKEDIN'S AUTHWALL CARRIES THE ADDRESS IT BOUNCED INSIDE ITS OWN QUERY**,
and the canonical form of an ORGANISATION address is a SLUG. A slug is a name.
So a signed-out load of a Page root can put a third party's name into a
refusal, on the ordinary path, every time.

Measured, with the shipped function and with the helper the two new tools call,
over the same synthetic authwall url:

    auth.assert_not_authwall        -> message carries the slug verbatim
    _authwall_refusal_without_the_landing -> message carries no address at all

Both are asserted in `tests/test_company_root.py`, and **the first one is the
control**: it drives the SHIPPED function and asserts the slug IS published.
The day that stops being true, the divergence is buying nothing and the test
says so in its own failure message.

`from None` is part of the fix rather than punctuation: it suppresses the
original exception whose message holds the url, so a traceback rendered
anywhere cannot walk back to it. Asserted.

**THE GENERAL CASE IS NAMED AND NOT FIXED.** Every other tool in `server.py`
still publishes its landing in this refusal. Most of their addresses carry a
numeric id, which is why this has not been worth a divergence before; repairing
it properly is a decision about a function twenty-odd tools share, and this
wave is three census rows. It is written down here rather than quietly widened.

**CORRECTED BY:** `_audit/2026-09-21-the-landed-url.md` -- the paragraph above is superseded the same day: the general case IS repaired, in `auth.assert_not_authwall` itself, so no tool in this package publishes its landing any more.

The divergence above is therefore no longer a divergence. It is kept anyway, as
a second independent refusal built from constants alone. That
document also MEASURES the premise this section asserted from url shape: the
authwall does carry the bounced address, in `sessionRedirect`, agreeing with
Chrome's recorded predecessor 14 times of 14 -- and **no measured landing has
ever carried an `/in/<member>/` path or an organisation slug**, so the half of
the claim that makes the leak severe remains DERIVED rather than verified. The
paragraph is left standing rather than rewritten, which is this document's own
rule two sections up.

---

## 6c. TWO SHIPPED GUARDS FIRED ON THIS WAVE'S OWN OUTPUT, AND BOTH WERE RIGHT

Neither was defused.

**1. `test_navigation_is_never_derived` -- AND IT WAS A NAME COLLISION.** Both
tools bound their assembled address to a local called `built` and navigated to
`built["url"]`. The engine collects taint PER MODULE BY NAME, deliberately --
a closure reading a landed url out of an enclosing scope is the shape it was
written for -- and `linkedin_job_detail` already binds `built` to a url
assembled from a company id it read OFF THE PAGE.

    'built' in _tainted_names(ast.parse(server.py))   ->  True

That site is genuinely derived and navigates to nothing; its own comment says
so. Mine are not derived at all: the url is a template this repository authored,
filled from a value the CALLER supplied and this package has already proven is
ten-ASCII-digit only. **The fix is a rename to `address`, with the collision
written at the call site**, so nobody later reads the name as a dodge.
`KNOWN_DERIVED_NAVIGATIONS` stays EMPTY, which its own comment asks for.

**2. `test_no_committed_identity` -- a urn-shaped literal in a test.**
`tests/test_group_page.py` drives the builder over every spelling that is not a
bounded digit run, and `urn:li:group:<digits>` is one of them -- the spelling
the allowlist entry names in its own list of what stays refused. **DECLARED,
NOT ASSEMBLED AT RUNTIME**, which is the remedy that file's own two prior urn
entries argue for: hiding a shape from the scanner blinds it to a real value
pasted in later. The value is the suite's own synthetic group id, already in
twenty-one other places under `tests/`, and it names a GROUP -- a group id is
numeric, which is the whole reason that address was admitted.

**AND A THIRD THING THAT DID NOT FIRE AND SHOULD BE SAID.** The identity gate
`scripts/pre_commit_identity_gate.py` runs ARMED in this worktree, not
disarmed: `tests/repo_paths.sanitisation_key_path` reaches across to the main
checkout when a worktree has no local copy of the gitignored wordlist. That is
a repair already shipped for the worktree hazard, and it was verified here
rather than assumed -- the gate printed no "wordlist absent; ALLOWING" line.

---

## 6d. A COLD REVIEW CONVICTED THIS READER OF A WRONG NUMBER, AND THAT IS THE
## MOST USEFUL THING IN THIS DOCUMENT

An independent reviewer -- no part in writing any of it -- was pointed at the
two modules with the bar written out and told to try to break each claim. It
drove the SHIPPED script under node, fuzzed both verdict functions, and planted
each of the three named couplings' defect to check the guard bit.

**IT FOUND A WRONG NUMBER, IN THE ONE PLACE THE MODULE CLAIMED THERE COULD NOT
BE ONE.** `company_root.py`'s docstring said, unconditionally:

> it cannot produce a wrong number, because a number is only published when a
> phrase this package shipped was found word-bounded in a short line

The reviewer's reproduction, against the shipped constant:

    ("", [("card", ["50 people viewed, 11 connections work here"])])
      -> {"phrase": 0, "shape": 1, "value": 50}   FIFTY

Word-bounded, short line, shipped phrase -- every precondition the sentence
named -- and the answer is wrong. `numeralOf` scanned for the FIRST digit run
in the candidate and had no relationship to where the phrase sat.

**FIVE FINDINGS, FIVE FIXES, AND EACH FIX SHIPS WITH A CONTROL THAT CONVICTS
THE OLD RULE.**

    1  WRONG NUMBER    the first digit run, not the one near the phrase
                       -> numeralNear(), bounded at COUNT_LINES_MAX_NUMERAL_GAP
                       -> the defect is re-planted and reads FIFTY again
    2  MISSING READING tightest-container-wins preferred a span holding the
                       phrase ALONE over the parent holding phrase AND count,
                       so an ordinary stat line read numeral_refused
                       -> a match CARRYING a number beats one that does not;
                          length is the tie-break, not the rule
                       -> the old preference is re-planted and loses the count
    3  RAISE           dict(reading or {}) raises on a bare int, bool or
                       string, in two functions whose docstrings say a needle
                       cannot reach them. Every FIELD was coerced and the
                       ARGUMENT was not
                       -> isinstance before dict(), in BOTH modules
    4  ASYMMETRY       "%" fell through the suffix check while k/m/b did not
                       -> percent_refused, APPENDED to NUMERAL_SHAPES so no
                          reading ever taken is renamed
    5  NARROWER THAN   the walk read script/style/template/svg/iframe and
       CLAIMED         [hidden] nodes as if they were lines
                       -> stepped over and counted as non_content_skipped

**AND ARIA-HIDDEN IS STILL NOT SKIPPED, WHICH IS THE ONE THE REVIEW MIGHT HAVE
TALKED SOMEBODY INTO.** On the search card the VISIBLE span is the one wearing
`aria-hidden="true"` and the screen-reader duplicate is the one carrying a
name. Skipping aria-hidden would step over exactly the copy this reader wants
and keep exactly the copy it defends against. There is now a test asserting
the skip is absent, so an "improvement" in that direction goes red.

`display:none` is still not handled and is named rather than implied: it needs
a computed style, which is a per-node layout read on a page with thousands.

### AND A CLAIM THAT WAS FALSE ACROSS FOUR SHIPPED MODULES, NOT ONE

`read_company_root`'s docstring said `html` is the control path "so
`control_fixture()` can PROVE the matcher works". **Nothing has ever run that
branch.** `DOMParser` is undefined under plain node, so the offline driver
always passes `html=""` and supplies a synthetic tree; production never passes
`html` at all; and the two tests touching `control_fixture()` check the markup
STRING.

Measured further, and this is the part that outlives this wave: **the same is
true of every sibling**. `anchors.control_fixture`, `search_results.control_fixture`
and `collections_page.control_fixture` are each read by tests that inspect the
string, and none is driven through a browser by anything in the suite. The
docstring here is corrected to say what is true; the house-wide gap is recorded
rather than fixed, because closing it needs a real engine and this wave had no
browser.

---

## 7. WHAT THIS WAVE DID NOT DO, AND WHY

### The second route for `N 33` is REFUSED on this bar, and that is a finding

`_audit/2026-09-19-the-read-rows.md` calls it *"the cheapest genuine BUILD left
in this set: the data is already returned, only the aggregation is missing"* --
`linkedin_connections` returns one row per connection over an admitted address,
so counting how many work at an organisation looks like a pure aggregation.

**IT IS NOT NAME-FREE AND IT CANNOT BE MADE SO.** Two independent reasons:

1. The rows carry a connection's NAME, PROFILE URL and HEADLINE on purpose --
   `linkedin_connections` publishes `rows_are_not_redacted` beside them saying
   so. An employer is not a field on those rows; it is inside a headline, which
   is free text a third party wrote.
2. To count "how many work at organisation X" the caller must supply X, and X
   is an employer NAME matched against third-party text. A company name is
   routinely a person's name -- the argument `company_page.py` makes with a
   live example from this repository's own corpus. That is a needle handed to a
   matcher over a page of other people, which is the shape decision `D1` in
   `_audit/2026-09-21-the-read-triage.md` is about and which nobody has ruled.

So the route is left where it is, named rather than quietly not taken. The Page
root serves the row with a COUNT and no needle, which is why it is the one that
was built.

### The traversal limit in the group reader, named rather than left

`dom.ANCHOR_CLASSIFY_JS` has no dot-segment rule -- that is the closure
`search_results.py` added and called *"not a refinement, it is the defect the
condition-2 amendment measured"*. An href whose leading segments say `groups`
and whose browser-normalised form is some other page is counted under what its
leading segments claim.

**WHAT THAT COSTS HERE IS A MISCOUNTED BUCKET AND NOTHING ELSE**, and the reason
is structural rather than lucky: no href read on that page is returned,
navigated to, or built into a url. The only address the module produces comes
from its own builder, filled from a value already proven ten-ASCII-digit only.
A traversal on the page can move one integer; it cannot move this process
anywhere. Closing it properly means a dot rule in a script three other readers
run, which is not this row's edit to make.

### Nothing was fired, and no ruling was invented

No write was added. `J 86` ("I'm interested"), `N 47`, `N 163` and `N 164` each
still need their own url, their own sanction entry and their own ruling. No
decision in section 4 of the read triage was resolved, relied on or nudged --
including the open `set_input_files` question, which this wave did not touch at
any point.

---

## 8. EVERY NUMBER HERE IS RE-DERIVABLE FROM A CLONE

    venv/Scripts/python -m pytest tests/test_group_page.py tests/test_company_root.py -q
      -> 32 passed, 52 passed

    venv/Scripts/python scripts/count_census_states.py --expect J=57,P=55,M=82,N=88
      -> GAP control: expected 282, measured 282 -- MATCH

    venv/Scripts/python scripts/check_gap_rows_on_refused_addresses.py --expect-gap 5
      -> PASS, unchanged: none of the three sits on a refused address

    venv/Scripts/python -m pytest tests/test_readonly.py -q
      -> 289 passed. EXECUTED_SCRIPTS 22, dom.py waivers 22.

    venv/Scripts/python -m tests.test_readers_emit_no_page_string --write-baseline
      -> 118 readers: clean 57, returns_text 40, not_driven 21

The V8 controls SKIP LOUDLY when `node` is not on PATH, naming what did not run,
rather than passing on a no-op. They ran here: node v25.2.1.

---

## 9. THE LEDGER LINE

Two readers, three rows, one page load each, zero fires. Both addresses were
admitted days ago and neither had a tool; both do now. The group reader spends
no new page contact at all. The company reader spends one, on the one question
a locator chain cannot answer, and the control that justifies it convicts a
one-line defect by reading FORTY-ONE where the page says ELEVEN.

What the next wave with a browser owes these rows is one fire each, and for
`N 33` / `N 54` that fire is also the measurement of `COUNT_PHRASES`.
