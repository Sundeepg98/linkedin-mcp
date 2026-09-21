<!-- secret-scan-allow: public-digests -->
<!-- The block in section 0 is a git commit id and three sha256 content digests
     of tracked source files. They are this document's PROVENANCE. No
     credential appears in this file, and no name, employer, campus, member id
     or profile slug appears in it either. -->

# THE `All filters` PRESS: REFUSED AT CONDITION 2, AND THE GATE WOULD HAVE PRESSED FIRST

**CORRECTS:** `_audit/2026-09-21-the-fourteen-fired.md` -- its section 5 and its row table say opening the panel *"is a press, and condition 5 of the admitting ruling is that nothing is fired from this surface"*, and its section 8 records the press as the *"one action that would settle twelve rows"*. **The press is not blocked by condition 5 and it would not settle them.** The disclosing press was RULED on 2026-09-19, and the `All filters` control fails that ruling's condition 2 TERMINALLY: measured live twice, it declares neither `aria-expanded` nor `aria-haspopup`, so no caller naming a sanctioned shape can reach it. That document's readings are not disturbed -- every count in it that this wave re-took reproduced -- and its verdicts on all fourteen rows stand.

**CORRECTS:** `_audit/_census/network.md` -- rows `80`, `81`, `84`-`93` each name the blocker as a press nobody has ruled on. The press IS ruled and the control fails it, which is the opposite kind of blocker: a deferral that resolves, replaced by one that does not. **NO ROW CHANGES STATE** -- twelve evidence cells are corrected in place, the state column is untouched on every one, and the slice's counts stand exactly as the preceding wave left them.

**2026-09-21. Read-only. Nothing was pressed, clicked, typed, submitted or
scrolled. `writes_enabled` stays False. The browser was attached to, never
launched, and it is still up.**

Twelve census rows -- `N 80`, `N 81`, `N 84`-`N 92`, `N 93` -- sit behind
LinkedIn's `All filters` control on people search. This wave was sent to run the
four conditions of `_audit/2026-09-19-the-disclosing-press-ruling.md` against
that control and, if all four held, to press it.

**THEY DO NOT HOLD. TWO OF THE FOUR FAIL, AND ONE OF THEM FAILS TERMINALLY.**

> **`All filters` declares NEITHER `aria-expanded` NOR `aria-haspopup`.** It is
> not a member of either sanctioned node set, so no caller naming a sanctioned
> shape can reach it and no future measurement will change that. Condition 2 is
> refused, `reachable_by_this_route` is False, and the ruling's own words for
> this case are already written: a control that declares neither attribute *"can
> only be matched by its LABEL, which is why it is refused here and why a
> listener-presence matcher is not the remedy."*

And the more useful sentence is not about the twelve rows:

> **HAD THIS WAVE FIRED THROUGH THE SHIPPED GATE, THE PAGE WOULD HAVE BEEN
> CLICKED BEFORE THE REFUSAL ARRIVED.** `press.evaluate`'s pre-press branch does
> not consult `press.sensitivity_basis`, and `/search/results/people/` declares
> no basis. So `press.disclose` returns `permitted_to_attempt: True`, clicks,
> presses Escape, and only then refuses with `no_sensitivity_basis`. Reproduced
> against the repository's own `FakePage`. Section 3.

---

## 0. PROVENANCE -- WHICH CODE RAN, AND HOW

The `linkedin` MCP server is not connected in this session, so nothing was fired
through it. Both scripts print their own provenance before reading anything:

    head                     73cd137db1c34f97cbfe861c1f28616e4d13766d
    sha256_press             a7a38ec488fd5e099d3369ecb969b62675079df9b0367656c2f5737c95ec8a8a
    sha256_search_results    f9d8fce47ca46f24085cd3be8d0a203794e52fe04ca943b7f45f17ff09e547b0
    sha256_dom               cca717f6fe4e37830c65645ebeaa24982e5220472b44111300e4000c2370c83f
    mode                     attach

**ATTACH, NEVER LAUNCH.** The probe refuses to run unless `LINKEDIN_CDP_ATTACH`
is set and opens a tab of its own, closed in a `finally`. No browser was
started, none was killed, and the CDP target inventory afterwards reads
`page 2, iframe 6, browser_ui 2, worker 9` -- reported as a count because whose
tab is whose is not something this wave can tell, and closing a tab it cannot
attribute is how an earlier wave took a browser down.

| file | what it is |
|---|---|
| `scripts/_probe_all_filters_disclosure_shape.py` | reads the sanctioned ATTRIBUTES of the control, plus the payload question. Contains no `click`, no `keyboard`, no `fill` and no `press` |
| `scripts/_check_the_disclosure_shape_reader_can_fail.py` | that probe's controls, SHOWN FAILING on a fixture built in the file |
| `tests/test_press.py` | one added case, section 3 |

**THE MATCHER IS LIFTED, NOT REWRITTEN.** `normaliseLabel` and `matchPhrase`
come out of the shipped `dom.FILTER_PANEL_JS` through
`search_results.filter_normaliser_source()` and `filter_matcher_source()`, so a
match here is a match by the shipped rule character for character. Writing a
second copy of a check this repository already ships is a scar it has paid for.

---

## 1. THE RULING THIS WAVE WAS GIVEN, RESTATED SO IT CAN BE REVIEWED

The brief carried a lead ruling and it is recorded here verbatim in substance so
a later reader can disagree with it:

> Condition 5 of the people-search admitting ruling -- *"NOTHING IS FIRED FROM
> THAT SURFACE. No connect, no follow, no message, no invitation"* -- governs
> firing AT A PERSON. It enumerates four acts that reach a person and states its
> own basis as *"Reading a result page invites nobody and messages nobody"*.
> Opening a filter panel is none of those, so condition 5 does not reach a
> disclosing press on page chrome.

**THIS WAVE DID NOT NEED TO RELY ON THAT RULING AND DOES NOT REST ON IT.** The
press was refused by the disclosing-press ruling's own conditions 2 and 3, which
bind whatever condition 5 means. The reading is recorded because it was given
and because it is reviewable, not because it carried any weight here.

**One thing about it is worth flagging in the other direction.** The admitting
ruling's bound says *"This admits a READ of a page listing other people"*, and
its reopeners include *"a control on that page that addresses a person and is
reachable by a read."* A press is not a read. Nothing in this wave turns on the
difference, but a future wave that wants to press here should notice that the
admission it would be standing on was written about reading.

---

## 2. THE FOUR CONDITIONS, ONE BY ONE

### CONDITION 1 -- THE PAGE MUST ALREADY BE ADMITTED. **PASS.**

Machine-checked, no browser:

    readonly.is_read_url(search_results.PEOPLE_SEARCH_URL)   True
    press.check_address(...)   {'pressed': False, 'admitted': True}

`check_address` is the stronger of the two: beyond the allowlist it clears the
composer markers and the third-party `/in/<someone>` refusal on their own
merits. The address carries neither.

### CONDITION 2 -- THE CONTROL MUST MATCH AN ENUMERATED DISCLOSURE SHAPE, BY ATTRIBUTE. **FAIL, TERMINAL.**

`press.SANCTIONED_SHAPES` is exactly `('[aria-expanded]', '[aria-haspopup]')`,
matched by exact membership. A caller naming either one passes `check_shape`.
**The binding question is not what the caller names -- it is whether the control
is a member of that node set**, because `disclose` presses
`page.locator(shape).nth(index)` and nothing else.

Measured live, twice, on two separate loads, byte-identical for the control
under test:

    people search, settled panel, 83 controls seen, values_refused 0

    phrase          matched   matched      matched     carries       carries       position in
                    (shipped   (hidden-    (aria-      aria-         aria-         [aria-expanded]
                     label)    excluded)   label)      expanded      haspopup
    ------------------------------------------------------------------------------------------
    all filters        1          1           0            0             0              -1
    locations          1          1           0            1             0               4
    actively hiring    2          2           1            1             0               3
    next               1          1           0            0             0              -1
    school anise       0          0           0            0             0              -1
    show results       0          0           0            0             0              -1

    page-wide:  [aria-expanded] 8   [aria-haspopup] 0   dialogs 0   menus 0
                menuitems 0   listboxes 0

**`all filters` matched exactly one control and that control carries neither
sanctioned attribute.** `-1` in the last column means it is not a member of the
`[aria-expanded]` node list at all.

**THE READING DISCRIMINATES FIVE WAYS, WHICH IS WHY IT IS EVIDENCE RATHER THAN A
ZERO.**

1. **The attribute half can say PRESENT.** On the same reading, `locations`
   reports `aria-expanded` at position 4 and `actively hiring` at position 3 of
   an 8-node list. A column that only ever reads absent certifies nothing; this
   one read present twice on the same page and absent for the control under
   test.
2. **The match half is live.** `next` = 1 is the whole-label equality path
   firing on real DOM, reproducing a prior wave's positive control.
3. **It is not saluting.** The synthetic `school anise` = 0.
4. **The panel is SHUT, not open.** `show results` -- the panel's submit -- reads
   0, and page-wide `dialogs` is 0.
5. **Cross-page.** Every one of the eighteen phrases reads 0 on the feed while
   the same reader sees 90-127 controls and 20-25 `[aria-expanded]` nodes. The
   number is about the page, not about the reader.

**AND THE HIDDEN-TEXT HAZARD WAS PRICED RATHER THAN ASSUMED AWAY.** The shipped
label source is `getAttribute("aria-label") || textContent`, and `textContent`
folds in `aria-hidden` and clip-styled screen-reader copies -- on this very page
the screen-reader copy of a result card carries an employer name the visible copy
hides. So every phrase was matched a second time under a label source that walks
text nodes and skips any whose ancestor chain is `aria-hidden`, `display:none`,
`visibility:hidden` or clip-styled. `all filters` matched **1 under both**, and
its `aria-label` column reads **0**, which means the visible-text path was
genuinely exercised rather than short-circuited by an explicit label. The control
is real.

**WHY THIS IS TERMINAL AND NOT NOT-YET.** `press.check_shape`'s own refusal text
answers it: a control that declares neither attribute can only be matched by its
LABEL, condition 2 forbids label matching, and a listener-presence matcher *"would
admit nearly every interactive node on the page -- the family wildcard condition
2 exists to forbid."* Widening the shape list is a RULING REQUEST with a measured
blast radius, not an edit. This is the same finding the read-triage already
recorded for a different control at `P A25`: *"entry control declares neither
aria-expanded nor aria-haspopup, so it is OFF press.SANCTIONED_SHAPES."*

**A SIDE-FINDING ABOUT THE MECHANISM, worth more than this one control.**
`disclose` takes an INDEX into an attribute-selected node list and condition 2
forbids identifying a control by label. **So the mechanism can only ever press a
control it is not allowed to identify.** On his own analytics page that was
tolerable and was argued for. On a surface listing other people, "press node 5 of
8 and find out what it was" is a different act, and nothing in the ruling
contemplates it.

### CONDITION 3 -- THE PRESS MUST BE SHOWN NOT TO MOVE AN OUTWARD COUNTER. **FAIL, INDEPENDENTLY.**

    press.sensitivity_basis("https://www.linkedin.com/search/results/people/")  ->  None
    declared basis markers                                                     ->  ['/feed/', '/analytics/profile-views/']

The table is CLOSED and keyed by surface, deliberately: *"a basis a caller can
assert is a basis a caller can invent."* With no entry, `check_counters` refuses
`no_sensitivity_basis` however many counters were read, because the 2026-09-19
amendment settled that **a merely readable counter prices nothing**.

**NEITHER ROUTE IS HONESTLY AVAILABLE ON THIS SURFACE, and that is a finding
rather than an omission.**

**Route (a), a counter shown SENSITIVE to this press class.** The only outward
counter readable here is the invitation badge, which read **0** on both surfaces.
It counts invitations WAITING -- received, not sent -- so the outward act this
surface actually offers, Connect, does not move it. And `shape.invitation_badge`
says in its own docstring that a badge at zero *"cannot distinguish 'the page
consumed nothing' from 'there was nothing to consume'"*, so at its current value
it is the least informative it can be. Nothing else on this page is a counter of
outward state: `search_results` publishes control counts, route-class counts and
filter-term counts, and none of them moves when anything is sent to anyone.

**Route (b), a structural argument that no outward effect is possible.** The only
structural argument on the record opens with *"THE SURFACE ADDRESSES NO ONE"* and
closes with a bound that decides this case: *"Anyone using this argument for a
surface where that distinction does not hold is misusing it."* A people-search
results page is made of other people -- this wave's own reading counted 18
`person_result` anchors on it in a sibling probe's run, and the admitting ruling
calls it *"the first admission granted on a THIRD-PARTY-DENSE surface."* Writing
a structural basis for it would be the misuse that entry names in advance.

So condition 3 resolves exactly as the ruling says it must: *"Where no counter
can price a given press, the press is NOT PERMITTED -- unmeasurable resolves
against the press, not for it."*

### CONDITION 4 -- IT MUST BE CLOSED, AND THE CLOSURE VERIFIED. **NOT REACHED.**

Recorded as unreached, never as passed. Closure is a property of a press that
happened; there was none. Reporting it as satisfied would be the same error as a
counter that was never read being filed as a zero.

### THE `REFUSED REGARDLESS` SECTION

Read, and `All filters` is not in it. It is not a composer or editor; it does not
navigate or submit; it is not on a third party's own surface -- it is page
chrome; and no typing is involved. **The refusal is at conditions 2 and 3, not
here.** Said plainly because "it was refused" and "it was refused for the worst
reason on the list" are different findings.

---

## 3. THE GATE PRESSES BEFORE IT REFUSES, AND THIS WAVE WAS THE CASE THAT WOULD HAVE PROVEN IT

`press.py`'s docstring says: *"THE PRE-PRESS GATE RUNS FIRST AND RETURNS BEFORE
ANY CONTROL IS TOUCHED. That ordering is the difference between a guard and a
report."*

**For every surface with no declared sensitivity basis, that is false.**
Reproduced against the repository's own `FakePage`:

    surface has a declared basis : None
    PRE-PRESS verdict            : {'pressed': False, 'permitted_to_attempt': True,
                                    'still_to_show': ['counters_unmoved', 'closure_verified']}
    POST verdict refused         : no_sensitivity_basis
    reachable_by_this_route      : True
    CLICKS THE PAGE RECEIVED     : ['[aria-expanded]']
    KEYS THE PAGE RECEIVED       : ['Escape']

The refusal is **derivable before the press** -- `sensitivity_basis` is a pure
function of the url -- and is **taken after it**. `evaluate`'s pre-press branch
returns on `before is None and after is None` without consulting the basis table.

**THIS IS NOT ACADEMIC. IT IS EXACTLY THIS WAVE.** Had the instruction to "fire
it" been carried out through the shipped mechanism, a live page listing other
people would have received a real click and a real Escape, and the gate would
have said no afterwards. The wave that reports this is the wave it would have
happened to.

**WHY THE ORDERING TEST DID NOT CATCH IT.**
`test_a_refused_press_never_touches_the_page` asserts precisely this property --
and every case it checks refuses at condition 1 or condition 2, both evaluated
before anything is touched. **No case exercised a surface that passes 1 and 2 and
fails 3.** A guard whose cases all take the same branch is a guard for that
branch.

**WHY IT IS REPORTED RATHER THAN REPAIRED.** The fix is four lines, and it
changes a contract a committed test relies on:
`test_his_own_profile_is_permitted_and_a_third_party_is_not` asserts
`permitted_to_attempt is True` for `/in/me/`, which declares no basis either. So
the correction is a decision about what a pre-press verdict MEANS for every
no-basis surface, and it belongs to whoever owns `press.py` -- not to a wave that
arrived to measure one control. The fourteen-fired wave set the same precedent
for the read-too-early race: measure it and hand it over.

**WHAT LANDED INSTEAD** is a characterisation test,
`test_a_surface_with_no_declared_basis_is_pressed_before_it_is_refused`, which
pins the behaviour with the inversion written into its docstring so the fixer
knows what to do with it. **SHOWN FAILING IN BOTH DIRECTIONS BY MUTATION** --
green at HEAD, red when a basis is planted for the people surface, red when the
pre-press branch is patched to consult the basis table, green again on restore:

    BASELINE, unmutated                                     GREEN
    MUTATION 1 -- declare a structural basis for the surface  RED
    MUTATION 2 -- pre-press consults the basis table          RED
    RESTORED                                                GREEN

---

## 4. DID THIS WAVE PRESS? NO. WHICH CONDITION STOPPED IT?

**NOTHING WAS PRESSED.** Condition 2 stopped it, and it is checked first. Condition
3 would have stopped it independently.

**AND THE PRESS WAS NOT ROUTED AROUND THE GATE.** Under
`tests/test_probe_interaction_budget.py` a probe may click freely -- `click` is an
OPEN class -- so this file could lawfully have clicked `All filters` and reported
what opened. It did not, and the reason is the ruling's own last line: *"a ruling
is not a permission to act ahead of the guard that bounds it -- that inversion is
how a narrow ruling becomes a wide practice."* A precondition answered by taking
the act is not an answer.

---

## 5. WHAT THE PANEL REVEALED

**Nothing. It was never opened.** The page was read shut, and this is what a shut
page says, in counts and closed-vocabulary positions:

    people search       83 controls   8 [aria-expanded]   0 [aria-haspopup]
                        0 dialogs     0 menus   0 menuitems   0 listboxes
                        panel settled True, 3 polls, 83 -> 83
                        matched 3, unmatched 79, empty 1, values_refused 0

    feed (control)      90-127 controls   20-25 [aria-expanded]   5-10 [aria-haspopup]
                        0-2 dialogs   3-4 menus
                        all eighteen phrases 0

The `0 dialogs / 0 menus / 0 menuitems / 0 listboxes` line is worth its own
sentence: **this page, shut, offers no open disclosure of any kind** -- so the
witness set `press.py` would have read at the open moment had a press been
permitted starts from a clean zero on every field. That is recorded for whoever
presses here next.

---

## 6. THE PAYLOAD QUESTION: THE VOCABULARY IS IN THE BYTES, AND THAT IS NOT THE SAME AS BEING READABLE

The brief asked whether the filter vocabulary ships in the hydrated payload even
where the DOM draws no control, because if it does the rows might need no press.
**The answer has two halves and they point opposite ways.**

**HALF ONE -- IT IS NOT IN THE RENDERED DOCUMENT.** Counting each phrase in
`page.content()`, 174,394 bytes:

    current company 0   past company 0   profile language 0   connections of 0
    followers of 0      open to volunteering 0                service categories 0
    all filters 4       locations 2      actively hiring 2    school anise 0

**AND THAT FIRST MEASUREMENT WAS INCOMPLETE, WHICH ITS OWN OUTPUT SAID.**
`code_blocks` read **0** on both surfaces -- the serialized post-hydration
document carries no hydration payload block at all -- so "not in the page" was a
claim about the DOM and not about the bytes. The probe was extended to count
across RESPONSE BODIES before the second firing.

**HALF TWO -- IT IS IN THE WIRE.** Per-phrase totals over the bodies delivered
during one navigation, counted and dropped inside the handler, nothing stored:

    people search:  7 document bodies  2,651,511 bytes
                   85 data bodies     13,359,746 bytes   0 unreadable
    feed        : 10 document bodies  6,650,981 bytes
                   91 data bodies      5,038,886 bytes  26 unreadable

    phrase                  people(doc)  people(data)  feed(doc)  feed(data)
    ---------------------------------------------------------------------------
    all filters                   9           76           0          1
    show results                  1           31           7          0
    current company               7           78           0          1
    past company                  7           59           0          0
    profile language              7          233           0          3
    connections of                0            2           0          0
    followers of                  0            2           0          0
    open to volunteering          0            4           0          0
    service categories            0            2           0          0
    school anise                  0            0           0          0

**THE CROSS-PAGE CONTROL IS WHAT MAKES THIS A READING.** Every term serving the
twelve rows reads higher on people search than on the feed, four of them read
exactly 0 on the feed, and the synthetic negative reads 0 in 13.36 MB.

**BUT IT DOES NOT BANK A ROW, AND THREE THINGS STOP IT.**

1. **A SUBSTRING COUNTER CANNOT TELL A FILTER FROM A FIELD.** `profile language`
   at 233 is almost certainly a per-entity key on each person record, not a
   filter. This is `N 82`'s disease one layer out -- a present token is not a
   meaningful one -- and it is the reason the small counts (`connections of` 2,
   `service categories` 2) are the interesting ones rather than the large.
2. **NO SHIPPED READER CONSUMES A RESPONSE BODY.** Every reader in this package
   reaches the page through `evaluate`. A census row is about what this server
   can reach, and this server cannot reach a response body at all.
3. **AND BUILDING ONE WOULD BE A HEAVIER ADMISSION THAN THE PRESS.** A raw
   response body on this surface is the UNSHAPED form of exactly the data the
   shaper exists to shape, and the admitting ruling made that shaper *"the
   condition of"* the admission rather than a courtesy attached to it. **A wire
   reader on a third-party-dense surface is a ruling request, and a larger one
   than the press this wave was sent to take.**

**SO THE PAYLOAD ANSWER IS: the vocabulary is there, the press is not the only
conceivable route, and the alternative route needs a bigger decision than the one
that was blocked.** The brief's hope -- *"if the payload carries it, those rows
are readable with no press at all"* -- does not follow. What changes is the
blocker, not the state.

---

## 7. THE ROWS

**`R` throughout. NO ROW CHANGES STATE. All twelve stay GAP** -- this wave
measured a blocker, not a capability, and a blocker measurement moves no verdict.

**WHAT CHANGES IS THE STATED BLOCKER**, and the change matters because the
current one is now known to be wrong in a way that would consume a future wave.
Seven rows say *"OPENING IT IS A PRESS, and condition 5 of the admitting ruling
is that nothing is fired from this surface [...] The expired `/search/results/`
blocker is replaced by a live one: A PRESS NOBODY HAS RULED ON."*

**A press nobody has ruled on is a deferral that resolves.** The measured blocker
does not: the press was ruled on, on 2026-09-19, and the control fails that
ruling's condition 2 terminally. A wave reading the old cell would go and ask for
a ruling that already exists.

| row | capability | before | after | what its cell now says |
|---|---|---|---|---|
| N 80 | Narrow search results to People | GAP | **GAP** | blocker restated: the `all filters` route is closed terminally, not pending a ruling |
| N 81 | Degree of connections | GAP | **GAP** | same, plus the single-word ambiguity it already carried |
| N 84 | Current company | GAP | **GAP** | **BLOCKER CORRECTED.** Not "a press nobody has ruled on" -- the press IS ruled, and the control fails condition 2 |
| N 85 | Connections of | GAP | **GAP** | same |
| N 86 | Followers of | GAP | **GAP** | same |
| N 87 | Past company | GAP | **GAP** | same |
| N 88 | School | GAP | **GAP** | same, plus the single-word ambiguity |
| N 89 | Industry | GAP | **GAP** | same, plus the single-word ambiguity |
| N 90 | Profile language | GAP | **GAP** | same |
| N 91 | Open to volunteering | GAP | **GAP** | same |
| N 92 | Service categories | GAP | **GAP** | same |
| N 93 | Keywords (decorated) | GAP | **GAP** | same; also still waits on the keyword ruling `N 79` names |

**ROWS TOUCHED IN `_audit/_census/network.md`, BY ID:**
`80`, `81`, `84`, `85`, `86`, `87`, `88`, `89`, `90`, `91`, `92`, `93` -- twelve
rows, evidence cell only, **state column untouched on every one.**

**`N 82` AND `N 83` ARE NOT TOUCHED**, and one of them nearly was. This wave
reproduced `actively hiring` = 2 and `locations` = 1 on two fresh loads, and its
hidden-excluded column read the same 2 and 1 -- which refutes ONE of the three
facts that convicted `N 82`, namely that hidden text supplied the phrase. **It
does not bank the row and the row is left alone**: the other two convicting facts
stand untouched (an unscoped whole-document selector, and a jobs-side phrase
nothing here can tell from a people filter without reading a label), and
`actively hiring` is the one match on this page carrying an explicit `aria-label`,
so its hidden-excluded reading was never the discriminating one anyway. Re-pricing
a refusal on a half-refutation is how a careful "no" becomes a careless "yes".

**COUNTS: UNCHANGED.** No state moved, so every census total stands as the
preceding wave left it. This document deliberately prints no `--expect` line: the
slice is being edited concurrently by another wave for write-direction rows, and
a total measured here would be a reading of a tree neither of us controls.

---

## 8. THE IMPACT GATE

Run on the staged change, twice -- once on the code and once on the documents.
Quoted with its own NOT CHECKED line, verbatim, because a gate that claims more
than it ran destroys the trust that made it useful.

**THE CODE COMMIT** (`scripts/` x2, `tests/test_press.py`):

    PASS over the 27 file(s) above (1696 tests) -- AND OVER NOTHING ELSE.

    NOT CHECKED: 177 of 204 test files (86.8% of the suite by file).
    The corpus-wide guards DID run, so the identity, credential and page-text
    sweeps cover the whole tree. Everything else above is unexamined.
    That is roughly 4398 of 6094 tests unrun (72.2%), against a suite count taken 2026-09-20 at 970a276.
    Wall clock: 75.4s.
    THIS IS A LOCAL, WINDOWS-ONLY SIGNAL. CI runs three platforms and is the
    certifier; a green gate here is not a reason to shrink that matrix.

**THE DOCUMENT COMMIT** (this file, the census slice, the corrected document,
the derived index, one triage entry):

    PASS over the 37 file(s) above (1683 tests) -- AND OVER NOTHING ELSE.

    NOT CHECKED: 167 of 204 test files (81.9% of the suite by file).
    The corpus-wide guards DID run, so the identity, credential and page-text
    sweeps cover the whole tree. Everything else above is unexamined.
    That is roughly 4411 of 6094 tests unrun (72.4%), against a suite count taken 2026-09-20 at 970a276.
    Wall clock: 223.3s.
    THIS IS A LOCAL, WINDOWS-ONLY SIGNAL. CI runs three platforms and is the
    certifier; a green gate here is not a reason to shrink that matrix.

**IT WENT RED TWICE FIRST, AND BOTH REDS WERE REAL.**

1. `test_probe_navigation_budget.py::test_no_new_probe_navigates_without_a_guard_or_a_declaration`
   caught the controls script navigating to a `data:` url with a raw
   `page.goto`. Its remedy list offers a `KNOWN_UNGUARDED` declaration -- which
   would have been the **first entry in a table that is empty on purpose**. The
   cheaper answer was not to navigate: `set_content` is this repository's
   established fixture path and is honestly what the script wanted, since a
   fixture is a string and not an address.
2. `test_a_correction_is_findable_from_the_claim.py::test_every_candidate_pair_is_declared_or_triaged`
   caught census row 80 citing this document with correction vocabulary in an
   undeclared pair. **The arrow points the wrong way** -- the row is reporting
   what this document measured, not withdrawing anything in it -- so it is
   triaged onto `NOT_A_CORRECTION` with that reason and with what would make the
   entry wrong, beside the entry the fourteen-fired wave wrote for the same row
   one document earlier.

**A third guard fired silently and was obeyed.** `scripts/build_audit_index.py`
reported `malformed markers 1` / `half-joined edges 1` after the first attempt at
the back-pointer, because that marker line named TWO documents and the parser
takes one. Rewording it to name a single document cleared both, and the index was
rebuilt with `--write`.

---

## 9. WHERE DISK DISAGREED WITH THE BRIEF

Four things, all in the brief's favour on the facts it could check and against it
on two it could not.

1. **"Run those four conditions and, if they all hold, fire it."** They do not
   hold. Two fail. The brief anticipated this and called a refusal a complete
   outcome, which it is.
2. **"`press.disclose` is built and has zero callers among the shipped tools."**
   Confirmed -- `menus.py` records it as deliberately kept off the tool surface.
   **But "built" does not mean "safe to call on any admitted page."** On a surface
   with no declared basis it presses before it refuses, so calling it to "let the
   gate decide" hands the page a click. Section 3.
3. **"Does the vocabulary ship in the hydrated PAYLOAD -- if it does, those rows
   are readable with no press at all."** The first half is yes on a weak
   instrument; the second half does not follow. Reading a response body is a
   capability this server does not have and a larger admission than the press.
   Section 6.
4. **"A prior wave measured them not among the 83 drawn controls [...] Opening the
   panel is the measurement that settles whether they are absent or merely
   undrawn."** Opening the panel is not available, so that question stays open by
   this route -- but it is no longer the only route, and the wire reading says the
   vocabulary exists. **Absent-from-the-DOM is now measured on two independent
   corpora rather than one.**

**And one thing the brief said that this wave initially doubted and now
confirms.** `textContent` is unconditional and merges hidden copies -- the
controls script planted that exact trap and it fired, twice, but **only once a
separating space was added to the markup.** Without whitespace beside it, hidden
text FUSES with the adjacent token (`Reset` + `Current company` normalises to
`resetcurrent company`) and matches nothing. The hazard is real and it is
narrower than it sounds: hidden text inflates a containment match only where the
markup leaves whitespace beside it. Real markup does; a hand-written fixture
forgets, and the first draft of the control silently disarmed itself and read
clean.

---

## 10. WHAT THIS WAVE DID NOT DO

* **Did not press anything**, including the two controls on this page that DO
  carry `aria-expanded`. Pressing `locations` would serve a row already banked,
  and would still be refused at condition 3.
* **Did not fix the pre-press ordering.** It changes a pinned contract on a
  module this wave does not own. Section 3.
* **Did not read a single label out of the page.** Every match was made in the
  page against a vocabulary shipped in, and only integers crossed. The probe's
  own gate re-derives that claim over the finished payload and was shown raising
  on three planted strings.
* **Did not write a capture of this surface to disk.** The `how you match`
  precedent puts captures under gitignored `_state/`, and a people-search body is
  denser in third-party identity than a job posting. Counting in memory and
  dropping the bytes costs nothing and leaves nothing.
* **Did not add a shape to `press.SANCTIONED_SHAPES`.** That is a ruling request
  with a measured blast radius, and the one shape that would reach this control --
  presence of a click listener -- is refused by name in `press.py` for admitting
  nearly every interactive node on the page.
* **Did not re-price `N 82` or `N 83`**, although it took fresh readings of both.
  Section 7.
* **Did not close any browser tab it could not attribute**, and did not stop the
  browser it attached to.

---

## 11. WHAT WOULD MOVE THESE TWELVE ROWS

Stated so the next wave does not re-derive it, in increasing order of cost.

1. **A SHIPPED READER OVER RESPONSE BODIES**, with a name-free shaper in front of
   it, on a ruling that admits reading a body at all. The evidence that it would
   find something is in section 6. **This is the route with the measurement
   already done.**
2. **A LABEL-SHAPE READER** -- word counts and no label text -- which would settle
   whether the five single-word zeros (`N 80`, `N 81`, `N 88`, `N 89`, `N 93`) are
   absent or merely decorated. The fourteen-fired wave named this and declined it
   because it is a new in-page reader and `dom.py` is where a script is declared
   and scanned. Still true; still the smallest unbuilt instrument here.
3. **A THIRD SANCTIONED SHAPE**, which is a ruling request with a measured blast
   radius and which `press.py` argues against in advance.

**What would NOT move them: asking for a ruling on the press.** That ruling
exists, the control fails it, and the failure is terminal.
