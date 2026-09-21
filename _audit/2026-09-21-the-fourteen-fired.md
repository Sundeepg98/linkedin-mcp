<!-- secret-scan-allow: public-digests -->
<!-- The block in section 1 is a git commit id and two sha256 content digests of
     tracked source files. They are this document's PROVENANCE -- the whole
     point of section 1 is that a firing which cannot name its own bytes has
     proven nothing -- and they are derivable by anyone with a clone. No
     credential appears in this file. -->

# THE FOURTEEN FIRED: one banked, one refused, twelve behind a press

**CORRECTS:** `_audit/_census/network.md` -- rows 80 through 93 each carried an EMPTY evidence cell and a blocker that expired 2026-09-20; all fourteen are re-priced here from a live firing, row 83 moves GAP to COVERED-PROVEN, and the slice's GAP count moves 91 to 90.

**CORRECTS:** `_audit/2026-09-21-the-read-triage.md` -- its re-measure command `--expect J=57,P=55,M=82,N=91` no longer passes now that row 83 has left GAP, so the live expectation is `N=90` and a census total of 284; that document's own claim is NOT wrong and is NOT rewritten, because it moved no state and said so truthfully.

**2026-09-21. Read-only. `writes_enabled` False, verified in-process before the
browser was touched. Nothing was pressed, typed, scrolled or submitted.**

Fourteen census rows -- `N 80` through `N 93`, the set
`linkedin_server/search_results.py` names in its own `FILTER_TERM_ROWS` -- sat
at GAP citing a blocker that expired on 2026-09-20, when
`/search/results/people/` was admitted together with its shaper and its tool.
Nobody went back to re-price them. The tool existed, the address was admitted,
the rows were named; **what was missing was one firing.**

This is that firing. It built nothing. It ran the shipped readers -- and then
the shipped TOOL itself, end to end -- against the real page, and wrote down
what they said.

**ONE ROW BANKED. THIRTEEN DID NOT.** The most useful sentence in this document
is not about a row at all:

> **`linkedin_people_search_shape` discriminates -- and what the page offers
> without a press is two filters, not fourteen.** Twelve of the fourteen are
> behind an `All filters` panel that is measurably drawn and shut, and opening
> it is a PRESS that condition 5 of the admitting ruling forbids. The blocker
> that expired has a successor, and the successor is a decision nobody has made.

---

## 1. WHICH CODE ACTUALLY RAN, AND WHY THE MCP ROUTE WAS NOT IT

The `linkedin` MCP server refused connection. **It was diagnosed, not worked
around.** The configured endpoint is an HTTP transport on a fixed loopback port.
A server process was alive -- and two independent facts disqualified it:

    the process was listening on NO port at all      (enumerated at the OS level;
                                                      the configured port was
                                                      absent from the listen set)
    the process had started the PREVIOUS DAY         from the MAIN checkout

The second is the one that would have mattered even if the first had not. **A
running MCP server holds the code it started with.** Anything fired through that
process would have been yesterday's bytes from another tree, and this wave's
whole claim is about code at this commit. So the firing went through the direct
script path, and each probe PRINTS ITS OWN PROVENANCE before it reads anything:

    head                     89ad9bdc722c91cfb4959d0585e18987ad04ff64
    sha256_search_results    49130fd348ca874abdb554edc72b1459268722431a41e31d23e4f51ac6bbbb94
    sha256_dom               0b13703319d8005001e95684f4ce7c4ac01d0f087c21c5f9c14e4905259d244e
    mode                     attach

**ATTACH, NEVER LAUNCH.** A Chrome was already running on the persistent
profile. Both probes REFUSE to run unless attach mode is set, and attach mode
opens a tab of its own rather than navigating one the operator is using. No
second browser was started against that profile, and no browser was killed.

## 2. THE INSTRUMENTS, AND THE ONE THING THEY MAY NOT DO

| file | what it is |
|---|---|
| `scripts/_probe_people_search_shape_live.py` | fires the two shipped readers at the live page; 3 built-in controls. `--fire-tool [--fire-tool-times N]` fires the TOOL end to end instead of only its readers -- a count, because a race is a ratio |
| `scripts/_probe_people_search_chrome_diagnosis.py` | drives the SHIPPED in-page classifier through its SHIPPED `phrases` parameter with a different vocabulary; injects no new JavaScript |
| `scripts/_check_the_probe_vocabulary_gate_can_fail.py` | the first probe's leak gate, SHOWN FAILING on planted defects |

**NEITHER PROBE EXTRACTS A LABEL, AND THAT IS NOT A FORMALITY.** A filter label
on this page can BE a person -- the `Connections of` control renders as
`Connections of <a person>` once set -- and a result card's accessible name
carries an employer. The obvious way to explain a zero is to print the 79
unmatched labels and look; that is exactly what may not happen here. So the
diagnosis in section 5 is done by shipping DIFFERENT WORDS IN and reading the
same integers back.

Neither probe prints an address, at any point, including the one it landed on.
Neither prints an exception message, only its type -- the scar one layer out is
that `int()` puts the value it refused verbatim into its own `ValueError`, which
is how a name left this process on 2026-09-20.

## 3. THE NAME-FREE CLAIM, CHECKED ON THE LIVE PAGE RATHER THAN ASSUMED

The shaper is name-free by construction. The point of a live firing is to check
the construction, so the first probe carries a gate that re-derives the shipped
alphabets (`emitted_alphabet()`, `filter_alphabet()`) and refuses any string
outside them plus its own key names.

    every reading, both surfaces          gate raised 0 times
    values_refused, every reading         0

`values_refused` is the stronger of the two, because it is the SHIPPED reader's
own counter: a nonzero means the page answered a count slot with something that
was not an integer, and on this surface a string in a count slot is a name until
shown otherwise. It was zero on every reading of every load of both surfaces.

**THE TOOL'S ONE FREE-TEXT FIELD IS CHECKED FOR PROVENANCE, NOT WHITELISTED.**
The envelope carries a `not_claimed` list of English sentences. Free English is
outside every shipped alphabet by construction, so admitting it would mean
admitting arbitrary text on the one surface where arbitrary text is a name.
Instead each sentence must be found in `linkedin_server/server.py`'s own
source -- a sentence that came off the document cannot be in a file written
before the page loaded. All three resolve.

*The naive form of that check was wrong and said so on its first run*, returning
False for all three and looking exactly like a finding. The literals are written
as implicit concatenation across source lines, so the runtime string is a splice
of fragments the file separates with a quote, a newline and an indent. **A
provenance check that cannot see the shape its own codebase writes strings in
manufactures a leak report** -- which is the same failure as a refusal that
names only what it did not match.

**ONE HAZARD IS REAL AND IS NOT A DISCLOSURE HAZARD.** `FILTER_PANEL_JS` takes
`label = getAttribute("aria-label") || textContent`, and `textContent` is
unconditional -- it ignores `aria-hidden`, `display:none` and clip-styling. So
hidden text CAN join a label inside the page. It cannot cross the boundary: both
scripts return integers and integer arrays only. It is a CORRECTNESS hazard, it
bounds what may be banked, and section 6 is where it decides a row.

## 4. WHAT THE LIVE PAGE SAID

Two loads, each read twice six seconds apart, plus the same readers on the feed
as a cross-page control. **Every people-search reading was byte-identical**, so
the page had settled; the feed had not (62 -> 108 anchors, 73 -> 204 controls),
which is the shell-then-fill behaviour a sibling probe measured on this
platform, and it appears here exactly where it was predicted to.

    surface          anchors  classified  person_result  controls  matched  unmatched  empty  refused
    people search         77          77             18        83        3         79      1        0
    feed (control)    62/108      62/108              0    73/204        0     72/203      1        0

    filter terms reading NONZERO on the people-search page
        actively hiring   2
        locations         1
    filter terms reading NONZERO on the feed
        (none -- all fourteen zero, against 72-203 controls seen)

**THE CROSS-PAGE CONTROL IS THE ONE THAT MATTERS.** The same code, the same
call, a different page, and the filter counts collapse to zero while the reader
still sees a hundred-odd controls. That is what refutes "the number is about the
reader". The route half collapses the same way: 18 `person_result` on the search
page, 0 on the feed, and `all_results` 7-8 on the feed against 0 on the search
page.

**It answers a question the tool's own docstring left open.** It said it did not
claim *"that the address serves a populated page when opened with no query"*. It
does: 77 anchors, 18 of them routing to the people vertical, and a drawn
`All filters` control.

## 4b. THE SHIPPED TOOL FIRED, AND IT HAS A READ-TOO-EARLY RACE

The trials above drive the tool's two readers. **The tool itself was then
called end to end** -- the same code path an MCP client reaches, including
`assert_not_authwall` and the published envelope -- because "the readers ran"
and "the tool ran" are different sentences and a census row says the second.

Three firings:

    firing   ok   landed   controls_seen   anchors   filters.by_term nonzero
      1     True   True         83            77     actively hiring, locations
      2     True   True         45            69     (none)
      3     True   True         83            77     actively hiring, locations

    TOOL FIRINGS THAT SAW ANY FILTER: 2 of 3

**FIRING 2 IS NOT A CONTRADICTION, IT IS A TIMING FINDING, AND THE SHIPPED
PAYLOAD DISCLOSES IT.** The tool reads immediately after the navigation settle,
and this page has two stable shapes -- 45 controls / 69 anchors while it is
still drawing, and 83 / 77 once it has. `denominators.controls_seen` reads 45
against 83, which is exactly the distinction that field exists to draw: the
tool's own docstring says a changed selector must be distinguishable from an
empty page, and a half-drawn page lands in the same slot.

**THE CORRELATION IS EXACT IN BOTH DIRECTIONS.** Across every reading this wave
took -- tool firings and reader readings, two probes, two vocabularies, a quiet
box and a loaded one -- `locations` read **1 on every reading of a drawn page**
(controls 73-83) and **0 on every reading of a partial one** (controls 45).
There is no reading that breaks it either way. That is what makes the zero
attributable to the clock rather than to the page.

**THE RACE WAS ONLY VISIBLE BECAUSE THE BOX WAS BUSY.** The first two runs were
taken on a quiet machine and every reading was byte-identical at 83 controls;
the race never showed. It appeared when a sibling agent's 7,386-test suite
pinned the CPU at 100%, which slowed the render past the settle. **A race that
only loses under load is invisible to exactly the conditions a careful wave
creates for itself** -- and the quiet run is the one that would have banked this
row with a clean story and no knowledge of the defect.

*This is reported, not repaired.* The fix would be a wait-for-the-panel in the
shipped tool, and that is a change to a tool on an admitted surface, which
belongs to whoever owns it rather than to a firing wave.

## 5. WHY TWELVE ZEROS, AND THE THREE KINDS OF ZERO

A zero is not a finding until you know which kind it is: **ABSENT** (not drawn),
**UNDRAWN** (no search chrome at all, so the question was never asked), or
**MISSED** (drawn, and the matcher did not recognise its label). The shipped
matcher is asymmetric, and the asymmetry is what separates them without reading
anything:

    one word   -> the label's ENTIRE normalised word list must equal it
    many words -> the words must appear as a contiguous run ANYWHERE in it

So a MULTI-WORD zero is strong: a decorated label like `Current company filter.
Clicking this button...` would still have matched by containment, and it did
not. A SINGLE-WORD zero is weak: decoration alone defeats it.

The second probe shipped in a different vocabulary and read:

    1   equality   next                positive control -- the equality path IS live on real DOM
    0   contain    school anise        negative control -- the synthetic scar phrase
    1   contain    all filters         THE PANEL IS DRAWN AND SHUT
    0   contain    show results        the panel's submit is not on the page
    0   contain    locations filter    consistency -- `locations` is one control, not a decorated second
    2   contain    actively hiring     the suspect, reproduced under a second vocabulary
    1   equality   locations           the banked reading, reproduced under a second vocabulary

    same twelve phrases on the feed:   all zero, 81 controls seen

`next` = 1 is the control the banking depends on. It proves the whole-label
equality path fires on real LinkedIn DOM, so `locations` = 1 is a match and not
an accident of a dead code path -- and `school anise` = 0 proves the matcher is
not saluting.

**THE ANSWER IS ABSENT-BEHIND-A-PRESS, NOT UNDRAWN.** The chrome is there;
`All filters` is drawn. LinkedIn keeps most people filters behind it. **Opening
it is a press, and condition 5 of the admitting ruling is that nothing is fired
from this surface.** This wave did not press it and did not ask to.

## 6. THE ROWS

`R` throughout. Before-state is GAP for all fourteen, every evidence cell empty.

| row | capability | before | after | one-line reason |
|---|---|---|---|---|
| N 80 | Narrow search results to People | GAP | **GAP** | Route half proves the vertical is ADDRESSABLE (landed with no redirect, 18 `person_result` vs 0 on the feed); it does not prove a control to narrow TO it, and the `people` term the shaper assigns to this row read 0 |
| N 81 | Degree of connections | GAP | **GAP** | Single-word term read 0; equality-only, so absence and a decorated label are indistinguishable |
| N 82 | Actively hiring | GAP | **GAP** | **MATCHED LIVE AND REFUSED.** Multi-word containment over an unscoped whole-document selector, count 2 where a pill should read 1, on a jobs-side phrase, in exactly the class `textContent` hidden text can inflate |
| N 83 | **Locations** | GAP | **COVERED-PROVEN** | **BANKED.** The shipped TOOL fired end to end and returned it on 2 of 3 firings, its readers on 8 further readings; the one zero read a half-drawn page and says so in `denominators.controls_seen` (45 of 83). Discriminates within page, across pages and across match path; rides the equality path, which hidden text cannot inflate |
| N 84 | Current company | GAP | **GAP** | Multi-word containment read 0 -- a decorated label would still have matched, so the control is not among the 83 drawn; behind `All filters` |
| N 85 | Connections of | GAP | **GAP** | Same -- multi-word containment zero; behind `All filters` |
| N 86 | Followers of | GAP | **GAP** | Same -- multi-word containment zero; behind `All filters` |
| N 87 | Past company | GAP | **GAP** | Same -- multi-word containment zero; behind `All filters` |
| N 88 | School | GAP | **GAP** | Single-word term read 0; equality-only, decoration indistinguishable from absence |
| N 89 | Industry | GAP | **GAP** | Single-word term read 0; equality-only, decoration indistinguishable from absence |
| N 90 | Profile language | GAP | **GAP** | Multi-word containment zero; behind `All filters` |
| N 91 | Open to volunteering | GAP | **GAP** | Multi-word containment zero; behind `All filters` |
| N 92 | Service categories | GAP | **GAP** | Multi-word containment zero; behind `All filters` |
| N 93 | Keywords (decorated) | GAP | **GAP** | **THE MISS WAS PRE-REGISTERED.** `search_results.py` limit 3 named this row before any browser ran: a decorated single-word label cannot match. It read 0, which is what the prediction says a decorated control looks like -- not evidence the page lacks one |

**Row 94 is out of scope and untouched.** It shares the expired blocker with
80-93 but is not in `FILTER_TERM_ROWS`; no term serves it and this firing says
nothing about it.

### Why `N 82` is the important refusal

It is the only row where the field a census cell would quote came back POSITIVE
and the row still did not move. A firing wave last week nearly banked a field on
`4 true / 0 false` at n=4 that read `9/2` at n=11, and a sibling probe returned
exactly 7 rows for every filter value it was given. **A present field is not a
meaningful one.** `actively hiring` = 2 is stable, reproducible under two
vocabularies, and unbankable, because nothing available here can tell a people
filter from a job promo without reading a label -- and reading the label is the
one thing this surface forbids.

## 7. THE COUNTS

    network.md      GAP  91 -> 90        COVERED-PROVEN  5 -> 6
    all four slices GAP 285 -> 284

Re-measure with `scripts/count_census_states.py --expect J=57,P=55,M=82,N=90`.

**A PRIOR DOCUMENT'S COMMAND IS NOW STALE AND IS NOT EDITED.**
`_audit/2026-09-21-the-read-triage.md` prints `--expect ... N=91` twice. Its
claim about its own edits stays true -- it moved no state. The successor value
is recorded in `_audit/_census/network.md`'s THIRD DELTA rather than by
rewriting that document, because a wave that rewrites the record it supersedes
leaves no way to see that anything moved.

## 8. WHAT THIS WAVE DID NOT DO

* **Did not press `All filters`,** which is the one action that would settle
  twelve rows, and is forbidden by condition 5.
* **Did not read a single label,** so it cannot say whether the five
  single-word zeros are absent or decorated. The measurement that would settle
  that returns label SHAPE (word counts) and no label text; it was not built,
  because it is a new in-page reader and `dom.py` is where a script is declared
  and scanned.
* **Did not fire a keyword.** The tool takes no parameter by design. Rows 79,
  93, 94 and 194 still wait on the ruling row 79 names.
* **Did not repair the read-too-early race** in section 4b. The fix is a
  wait-for-the-panel inside a shipped tool on an admitted surface; a firing
  wave measures it and hands it over, it does not quietly change the thing it
  was sent to measure.
* **Did not capture the `How you match` panel** for the secondary `J 110`,
  `J 116`-`J 120` hypothesis. Those rows are untouched and remain a hypothesis.

## 9. THE GENERALISABLE HALF, AND IT IS ABOUT ACCESSIBILITY

On the search card the proximity insight renders twice and the copies differ:
the `aria-hidden="true"` visible span is name-free and the `visually-hidden`
screen-reader span carries the employer name. **The accessible copy is the
dangerous one.** `dom.py`'s own 2026-08-30 comment already records `innerText`
leaking that clip-styled pattern -- and `FILTER_PANEL_JS` reads `textContent`,
which is strictly leakier than the thing already shown to leak.

So the safer-looking surface is the dangerous one twice over: once in the page,
where the screen-reader copy holds the name the visible copy hides, and again in
the reader built to consume it. Here it is contained -- only integers cross --
but containment at the boundary is the LAST line, not the first, and a reader
that matched on `textContent` fed a count that a census row would have quoted.
**Registered as instrument-register entry 48.**
