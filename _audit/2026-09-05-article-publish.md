# The publishing surfaces: one ruling was already made, in code, by the operator

**CORRECTS:** `_audit/2026-09-03-linkedin-gap-blockers.md` -- blocker 51 `COLLABORATIVE-CONTENT` is filed as one blocker and is two under that document's own merge rule, so three of its four rows are costed higher than they are; detail in section 4.

Wave `article-publish`, 2026-09-05, 18:46 to 19:1x by the box (`date`, stamps in
section 8). Six blockers, 17 rows. Three commits. Nothing pushed.

Numbers RECOMPUTED at freeze rather than re-read: `_ALLOWED_URL_PATTERNS` **29**,
unchanged by this wave; the two instruments **18 passed, 1 skipped**; the shipped
identity sweep **PASS, 0 hits across 335 tracked files**, taken at the gate and
not at the start; **0 AI attribution across all three commits**, verified per
commit rather than as a habit.

## 1. THE HEADLINE, AND IT IS NOT THE RULING I WAS HANDED

The lead's ruling for `MENTION-COMPOSITION-RULING` was: build the mechanism if
the surface supports it, but *the composed mention must never be assembled from
a name this server READ off a page*.

**That ruling was already made, by the operator, and it is already asserted in
code.** `tests/test_typed_bytes.py` opens by naming its source:

> THE OPERATOR'S TYPING RULING CARRIED THREE CONDITIONS, and two of them are
> structural -- a named-and-measured control, and **text the caller supplied
> rather than this server composing it.**

and enforces it off the AST: the one `page.fill` site in the package must take
its text from `_text_component_of(spec, grant.target)` **and from nowhere
else**, so that "a future edit that interpolates, truncates, strips or
decorates the string fails here rather than typing something he never read".

**A MENTION IS THAT EDIT WEARING A FEATURE'S NAME.** Typing the characters
`@Name` into a LinkedIn composer produces no mention; the platform requires a
typeahead commit. So a mention is bytes the SERVER inserts into his post at a
position the SERVER chooses. Census row `C10` records the collision from the
other end without naming it as one: *"the suite actively guards against the
server adding anything to his text"*, citing the mutation that appended a
hashtag and passed the substring version.

**Two rulings, derived independently, agree.** The lead's forbids assembling a
mention from a name read off a page. The operator's forbids the server
composing any of his text at all -- which is strictly wider, and it is the one
already shipped with an assertion behind it.

### The distinction that makes this a ruling and not a refusal to try

A needle is NOT forbidden and must not be. `send_message` and
`send_invitation` both take one, and this repository ruled on 2026-08-31 that a
needle is his own word going INTO the page with integers coming back -- so
`writes.py:4774` can say "exactly one of nine controls carries the word you
gave, at position 3" and cannot say who.

**The line is DESTINATION, not presence.** A needle selects a control and is
discarded; the name it matched reaches a confirm block he reads and explicitly
never reaches `grant.target`, `grant.preview` or the `Observation`. A mention
sends that same name the opposite way -- outward, permanent, third-party
visible, and it notifies the person named.

So "does this server touch a third party's name" is the wrong question and
would refuse two shipped tools. The right one is **where the name goes**, and
that question has a different answer for a mention than for every write already
sanctioned here.

## 2. VERDICTS, row by row

| # | blocker | rows | verdict |
|---|---|---:|---|
| 16 | `MENTION-COMPOSITION-RULING` | 2W | **EXCLUDED-RULED** -- the operator's typing ruling, already asserted |
| 64 | `MENTION-TAG-CONTROLS` | 3W | **EXCLUDED-RULED** for the composition half; see the caveat below |
| 77 | `CELEBRATION-COMPOSER` | 1W | **EXCLUDED-RULED, CONDITIONALLY** -- one read settles it, not taken |
| 51 | `COLLABORATIVE-CONTENT` | 4W | **RE-FILE as two blockers.** 3 composer-side, 1 needs an address |
| 37 | `ARTICLE-SURFACE` | 6 | boundary measured, not closed. Section 5 |
| 59 | `PUBLISH-POST-AUDIENCE-PARAM` | 1W | fork already decided in A9; one measurement remains, NOT taken |

**THE CAVEAT ON 64, and it is a real limit on this document.** I could not
locate the row-to-blocker map, so I cannot name which three census rows blocker
64 holds. The mention rows I did find and read are `C10` (mention in a post),
`C28` (mention in a comment), `M23` (mention in a group chat) and `C66` (mention
group members in a conversation) -- four, where blockers 16 and 64 together hold
five, and `M23`/`C66` may sit under `GROUPS-SURFACE` instead. **The ruling
reaches the ACTION CLASS -- compose a mention or a tag into published content --
and whoever holds the map should apply it row by row rather than take my count.**

**AND THE HALF THE RULING DOES NOT REACH.** Blocker 64 is
`MENTION-TAG-CONTROLS`, and LinkedIn's mention/tag *privacy* controls
(`a522861`, `a524212`, `a524346`, recorded in the census's help-index walk) are
settings on HIS OWN account governing who may tag HIM. Those are self-scoped and
nothing above touches them. If any of blocker 64's three rows is a privacy
control rather than a composition, that row is NOT excluded by this ruling and
stays open. I did not establish which.

## 3. `C9` -- why celebration is conditional and not ruled outright

A LinkedIn celebration post is templated and the template names the person
celebrated ("Congratulate X on their new role"). If that holds, `C9` is the same
action class as a mention and retires with it.

**I did not verify it.** It needs one read of the celebration template on the
post composer, and the composer is the thing this wave declined to open --
section 6. Recorded as conditional rather than asserted, because the difference
between "the template names a third party" and "I expect it does" is the whole
of the ruling.

## 4. `COLLABORATIVE-CONTENT` is two blockers, by the ledger's own rule

Section 3 of the blockers document states the merge rule: *"two blockers merge
only when THE SAME SINGLE ACTION closes both. Different surfaces stay different
blockers."*

The four rows are not one surface:

* `C54` create a collaborative post, `C55` manage its collaborators, `C56`
  remove yourself from one -- **the post composer**, an address already loaded.
  No new allowlist pattern is needed for any of them.
* `C76` contribute to a collaborative article -- **a different LinkedIn product
  entirely**, AI-seeded articles members add sections to. The census says so
  itself: *"Absent from the Share Content and Post topic trees entirely."*

Measured, offline, against `readonly.is_read_url` at the current tree:

    /collaborative-articles/               False
    /pulse/collaborative-articles/         False

So the blocker's single "allowlist +1" is owed by exactly ONE of its four rows,
and three rows carry a cost they do not incur. **Re-file as
`COLLABORATIVE-POST` (3W, no boundary) and `COLLABORATIVE-ARTICLES` (1W,
allowlist +1).** I am not editing the ledger; the row-by-row edit belongs with
whoever holds the map, and this document corrects a cost without spending one.

**Note which way this cuts.** It does not retire a row. It makes three rows
CHEAPER than filed and one row correctly costed -- the opposite direction from
the flattering error, which is the class I would not have caught by re-reading.

`C54`/`C55` are also *partly* reached by section 1: inviting a named
collaborator is a third party's identity entering published content. The
"create" half is not -- a collaborative post can be created before anybody is
invited. I am splitting no further without the composer read.

## 5. `ARTICLE-SURFACE` -- the boundary, measured rather than assumed

Ten candidate addresses through the shipped `readonly.is_read_url`, offline, at
the current working tree:

    /article/new/                          True
    /feed/                                 True      (control, known allowed)
    /article/newsletter/new/               False     (control, known refused)
    /pulse/                                False
    /in/me/recent-activity/articles/       False
    /in/me/recent-activity/all/            False
    /pulse/collaborative-articles/         False
    /collaborative-articles/               False
    /posts/                                False
    /article/edit/                         False

    _ALLOWED_URL_PATTERNS                  29 patterns

**One article address is admitted and it is the composer.** Every read address
an article capability would need -- list your articles (`C48`), manage comments
on them (`C49`) -- is refused, and `/pulse/` is refused as a prefix, so the
blocker's "allowlist +1" holds only if one pattern serves both. I did not
establish that it does.

**`C44` write-and-publish-an-article is already EXCLUDED-RULED and the reason is
measured, not preferential:** `writes.py:926-929` records that `/article/new/`'s
publish control comes back `<redacted>`, blanked as a singleton, *"so that route
has no measured anchor where this one does"*. That is the same count-1 redaction
defect the newsletter and groups waves each hit today, arriving on a third
surface. I did not attempt to fix it -- it is `writes.py`, contended, and it is
the audience-control problem in section 6 wearing different clothes.

**Two controls behaved**, both in the same run: a known-allowed address returned
True and a known-refused one returned False. Without those the ten readings
would be a fact about my import path.

## 6. `PUBLISH-POST-AUDIENCE-PARAM` -- decided in A9, and I did not take the read

Amendment A3 files this NOT CLOSED, and A9 then decides the fork: admit the
post-audience option set as a **closed vocabulary**, on the precedent of
`dom.MESSAGING_FILTERS`, which is matched by name before any locator is built so
"an arbitrary string can never become a click target".

A9 also names what must happen first: **the audience option set has never been
written down in this repository**, and a closed vocabulary is admitted by name
or not at all. That is one read on the composer.

**I DID NOT TAKE IT, and the reason is a cost, not a scruple.** `/article/new/`
and the post composer are COMPOSERS: opening one may autosave a draft this
server has no reachable surface to detect. With roughly twenty minutes left I
could open a composer or I could write down a ruling that was already made and
not being applied -- not both, and only one of those is recoverable if I am
wrong about it.

**What I may have spent: nothing.** No page was opened, no browser attached, no
composer touched. Every measurement in this document is an offline import of
`readonly` and an AST parse of `server.py`. The live read remains owed and it is
still one page load.

The tool meanwhile **refuses outright** -- `linkedin_publish_post`'s docstring
opens *"REFUSES: the audience is unread"* and *"it loads nothing and costs
nothing"*. So row `M C2` is not one missing parameter on a working tool; it is
the gate holding the only publish capability shut. Its ledger ratio of 0.50
prices the row and not the leverage, and a planner reading the ranked table
alone would not see that.

## 6b. THE BUILD SPEC FOR ROW 59 IS ALREADY IN THE CODE -- AND IT CARRIES A HAZARD

Found after section 6 was written, which is why it sits beside it rather than
inside it. `server.py:6400` and the twelve lines above it hold the whole
remaining design:

    _COMPOSER_AUDIENCE_READER = "read_post_composer_audience"

    def _composer_audience_is_readable() -> bool:
        return callable(getattr(dom, _COMPOSER_AUDIENCE_READER, None))

**The refusal lifts by FEATURE DETECTION**, and the comment beside it argues the
choice well: a boolean "would have to be flipped by hand and would go stale
exactly the way the seven spec sentences corrected on 2026-09-03 did". That
reasoning is right and I am not disputing it.

**THE PROPERTY THAT FOLLOWS FROM IT, WHICH NOBODY WROTE DOWN.** The act that
re-arms `linkedin_publish_post` is *defining a function with a particular name
on `dom`*. Not landing a reader. Not proving it reads anything. A stub written
to sketch an interface satisfies `callable(...)` and lifts the gate on an action
this server declares IRREVERSIBLE and whose outcome it declares UNVERIFIABLE.

**This is a measured defect class in this repository, arriving in the most
expensive possible place.** `_redact` was admitted to `readonly._SANITISERS`
"on the strength of its NAME and turned out to carry no slug rule at all" --
and the remedy adopted then, `_relation` admitted *with the test that proves its
contract*, is the remedy available here. The difference is that `_SANITISERS`
learned it after the fact and this can be written before the reader exists, at
which point it costs nothing.

So `PUBLISH-POST-AUDIENCE-PARAM` is better understood than its ledger row says:

| | ledger | measured here |
|---|---|---|
| what remains | 1 ruling + 1 tool | the ruling is A9 and is DONE; the tool has a NAME, a call site and a live consumer already waiting on it |
| what is missing | a parameter | the **audience option set**, which one page load establishes |
| the risk | none recorded | defining the name alone lifts an irreversible-action refusal |

**I did not build the reader and should not have.** Its contract cannot be
written until the option set is measured (A9), and inventing the vocabulary from
a sibling control's options is the thing A9 explicitly forbids.

## 7. THE INSTRUMENTS -- two, and both shown failing

`tests/test_no_write_tool_names_a_third_party.py`, 15 tests, 1.21s.

Parses `linkedin_server/server.py` with `ast`, enumerates every `linkedin_*`
function and its parameter names, and refuses a parameter whose VALUE would be
another member carried into published content -- `mention(s)`, `tag(s)`,
`tagged`, `collaborator(s)`, `invitee(s)`, `celebrant`, `honoree`.

**SHOWN FAILING, with the detector factored out of its assertion.** The
mutation `mentions: list[str] = []` was applied to a COPY of `server.py` in a
temp directory and the SHIPPED test function was pointed at it -- the contended
real file was never edited, so the demonstration cost no staging window:

    control (corpus still readable)     PASS
    param mentions                      RED   ['linkedin_publish_post(mentions=...)']
    param tag                           PASS (not killed)

The third line is the discrimination proof and matters as much as the second: a
`mentions` mutation does not turn the `tag` case red, so the parametrisation is
naming distinct properties rather than one assertion repeated thirteen times.

**It carries a control that fails loudly if the corpus empties.** A rename of
the `linkedin_` prefix would leave every forbidden-name case passing over zero
tools; `test_the_tool_surface_is_readable_at_all` pins >= 30 tools parsed and
`publish_post`'s first parameter. A guard that enumerates nothing refuses
nothing.

**AND `audience`/`visibility` ARE EXEMPTED BY NAME, not by silence** -- with A9
cited in the file -- so this guard cannot be read later as forbidding the very
parameter A9 rules admissible. A third test asserts the exemption set and the
forbidden set stay disjoint, so a future editor cannot quietly move one across.

**WHAT IT IS NOT.** It guards the SURFACE -- the promise a caller reads. It
does not and cannot prove no mention is composed inside the package;
`test_typed_bytes.py` guards the mechanism, off the same AST, and neither is the
claim alone.

### `tests/test_the_audience_reader_arrives_with_its_contract.py`, 3 passed 1 skipped, 3.73s

The hazard in 6b, turned into an assertion. If `dom.read_post_composer_audience`
exists, a contract test for it must exist too -- so the reader cannot arrive
alone and re-arm publishing on the strength of its name.

**It carries two controls and they are the load-bearing part.** One pins the
exact string the refusal is keyed on, so a rename fails HERE with a reason
rather than leaving the guard watching an attribute nothing consults. The other
asserts the live refusal still returns `audience_unread`, so the guard cannot
outlive the thing it protects.

**SHOWN FAILING IN-SUITE, not in a side script.** `test_this_guard_can_fail`
monkeypatches the name onto `dom`, asserts the server's OWN feature detection
then returns True, and asserts the guard turns red with `pytest.raises`. The
mutation is a monkeypatch, so no contended file was edited. It also branches: if
a contract test IS on disk by then it asserts the guard PASSES instead, and says
which branch it took -- a guard whose failure demo silently inverts later is
worse than no demo.

**The skip is deliberate and is the current state, stated:** the reader does not
exist, so the assertion cannot fire yet and says so in its skip reason rather
than passing vacuously. A test that passes because its subject is absent is the
green this repository distrusts most.

### And the correction guard fired on ME, which is worth one line

My first `CORRECTS:`/`CORRECTED BY:` pair was MALFORMED -- I wrapped the reason
onto a second line and `test_every_marker_names_one_document_and_carries_a_reason`
refused both halves with the exact reason. **I would not have caught it by
reading**; the markers looked right. It also could not fire until the file was
STAGED, because the corpus is `git ls-files -- _audit` -- which is today's
~16:57 scar exactly: *after staging new files, RE-RUN the tracked-file guards.*
I ran them before staging first, and they were green on a corpus that did not
contain my document.

## 8. WHAT I DID NOT DO

Said plainly, because the wave was 45 minutes and six blockers is not a
45-minute list.

* **No live read of any kind.** No browser attached, no composer opened, no page
  loaded. The two reads this surface owes -- the audience option set (section 6)
  and the celebration template (section 3) -- are both still owed.
* **I went as far as the census tool and stopped there.** `linkedin_server_info`
  reports the running process **STALE** -- loaded `1b940ff99ffc`, disk
  `825543dbbaf8` -- so a census taken through it would be a measurement by older
  code, reported without that sentence attached. **I did not restart the
  server**: it is `transport`'s artifact, a dozen waves are attached to it, and
  restarting a shared process to take my own reading is the shared-state move
  this tree has been burned by. The probe route reads current code and was the
  right answer; I chose section 6b over it with the clock I had, and 6b needed
  no page at all.
* **No boundary change.** `_ALLOWED_URL_PATTERNS` is 29 at this tree and I added
  nothing. The digest chain is contended and re-freezing it for a pattern I have
  no reader behind would be A10's "a boundary opened with nothing behind it".
* **No ledger edit.** Sections 2 and 4 specify moves; none is applied. Anyone
  quoting a new row count off this document is quoting an intention.
* **No `writes.py` or `server.py` edit.** Both contended all afternoon. The one
  mutation this wave performed went to a temp copy.
* **The fifth mention row was never located.** Section 2's caveat.
* **`C49` (manage comments on your articles) was not analysed at all.** It is a
  W row on a surface with no admitted address, and I ran out of clock before
  asking whether the comment-gate work in `writes.py` already reaches it.

Verified by the box, not estimated:

    Sat, Sep  5, 2026  6:46:51 PM     wave start
    Sat, Sep  5, 2026  6:55:30 PM     back-pointer written, guards re-run

**AND THE CLOCK LAW FIRED ON ME, mid-wave, which is worth one line because it
is the third instance today.** At the point the box read **18:54** I had
written "19:16" into my own working notes and was cutting scope to fit fourteen
remaining minutes that were actually thirty-six. **My sense of elapsed time ran
~20 minutes fast** -- the lead's was ~25, an earlier wave's ~113. Same
direction, same class, and it was caught only by running `date` rather than by
noticing anything felt wrong. Section 6's decision not to open a composer was
taken under the WRONG number and I am letting it stand on its own merits, not
re-deciding it because the clock turned out kinder.

## 9. THE ONE THING I WOULD TELL THE NEXT WAVE

Four of the six blockers here were answerable from documents already in this
tree -- the operator's typing ruling in a test docstring, A9's closed-vocabulary
decision, the merge rule in section 3 of the blockers document, and `C44`'s
existing EXCLUDED-RULED note. **Nobody had joined them to the rows they
settle.** The census and the ledger both describe capabilities; the rulings live
in test docstrings and amendments, and there is no index from one to the other.

That is the same shape as the day's other findings and it is cheap to say: **a
ruling that is not attached to the row it decides gets re-derived by whoever
opens the row next**, and re-derivation is where a wave spends its hour.

## 10. THE REGISTER ENTRY, AND WHY IT IS HERE INSTEAD OF IN THE REGISTER

This is written as section 14 of `_audit/INSTRUMENTS.md` and is NOT in that
file. I appended it, staged it, and the staged diff carried **118 lines of
which 49 were another wave's section 12.11** -- appended in the seconds
between my read of the file and my `git add`. Git reported ONE hunk: my
block and theirs are contiguous, so there is no staging flag that separates
them, which is the register's own recorded law about append-only shared
files.

**I backed my 69 lines out and left their 49 byte-identical** (`git diff`
reports 49 insertions, 0 deletions, so nothing of theirs was altered), and
moved my entry here -- the freeze file's own first recommendation: *append
to your own file and let the lead merge*. Whoever holds `INSTRUMENTS.md`
can lift the block below verbatim; it is written as a register section and
needs no editing. **Its number will be wrong** -- another wave was mid-write
and 14 may be taken by the time it lands.

This is the sixth instance today of the staging window, and the first I
know of where it was caught BEFORE the commit rather than after. What
caught it was not `--numstat`: that read `118 0` and looked like mine.
**It was grepping the added lines for headings**, which took one command
and named a section number I had never typed.

---

## 14. The article-publish wave, 2026-09-05

Two instruments, and the second is a NEW INSTANCE OF SECTION 3'S OWN LAW found
in the most expensive place available.

### 14.1 `tests/test_no_write_tool_names_a_third_party.py`

Parses `server.py` with `ast`, enumerates every `linkedin_*` function, and
refuses a parameter whose VALUE would be another member carried into published
content -- `mention(s)`, `tag(s)`, `collaborator(s)`, `invitee(s)`, `celebrant`,
`honoree`. Shown failing under a planted `mentions` parameter; a `tag` case
stays green under that mutation, which is the discrimination proof. Carries a
control pinning >= 30 tools parsed, because a rename of the `linkedin_` prefix
would otherwise leave every case passing over an empty corpus.

**THE PATTERN WORTH REUSING: EXEMPT BY NAME, NEVER BY SILENCE.**
`audience`/`visibility` are ADMISSIBLE under Amendment A9's closed-vocabulary
ruling and are listed in a `RULED_ADMISSIBLE` constant with A9 cited, plus a
third test asserting the two sets stay disjoint. A guard that forbade them by
omission would read, six weeks from now, as forbidding the very parameter a
written ruling permits -- and nobody would be able to tell the omission from a
decision.

### 14.2 `tests/test_the_audience_reader_arrives_with_its_contract.py`

`server._composer_audience_is_readable()` lifts `linkedin_publish_post`'s
refusal by FEATURE DETECTION -- `callable(getattr(dom, _COMPOSER_AUDIENCE_READER,
None))`. The reasoning beside it is sound: keying on the capability beats a
boolean that must be flipped by hand and goes stale.

**THE PROPERTY NOBODY WROTE DOWN: the act that re-arms an IRREVERSIBLE broadcast
under his own name is DEFINING A FUNCTION WITH THAT NAME.** A stub sketching the
interface satisfies `callable()` and opens the gate.

**That is section 3 of this register, arriving where it costs the most.**
`_redact` entered `_SANITISERS` on the strength of its name and carried no slug
rule at all; `_relation` was later admitted WITH the test that proves its
contract. This writes the same requirement BEFORE the reader exists, which is
the only order in which it is free.

The guard: if `dom.read_post_composer_audience` exists, a contract test for it
must exist too. Two controls -- the exact keyed string, and that the live
refusal still returns `audience_unread` -- so a rename fails there with a reason
instead of leaving the guard watching an attribute nothing consults.

**SHOWN FAILING IN-SUITE RATHER THAN IN A SIDE SCRIPT**, by monkeypatching the
name onto `dom` and asserting the guard turns red. Two details worth copying:
the demo **branches** and states which branch it took, so it cannot silently
invert into a vacuous pass once a contract test lands; and the main assertion
**skips** today with its reason rather than passing, because a test that passes
because its subject is absent is the worst green available.

### 14.3 The two laws this wave paid for

**A RULING NOT ATTACHED TO THE ROW IT DECIDES GETS RE-DERIVED.** Four of this
wave's six blockers were answerable from documents already in the tree -- the
operator's typing ruling living in a TEST DOCSTRING, A9's closed-vocabulary
decision, the ledger's own merge rule, and an existing EXCLUDED-RULED note.
Nobody had joined any of them to the rows they settle. The census describes
capabilities and the rulings live in docstrings and amendments, with no index
between them.

**A MARKER GUARD CAN ONLY SEE A STAGED FILE.** The correction machinery's corpus
is `git ls-files -- _audit`. Guards run BEFORE staging were green on a corpus
that did not contain this wave's document; run after staging, they caught a
malformed `CORRECTS:`/`CORRECTED BY:` pair (the reason wrapped onto a second
line) that reading would not have caught. Same shape as the ~16:57 sweep scar,
on a different guard.
