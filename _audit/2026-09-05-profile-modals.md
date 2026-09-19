# profile-modals -- four blockers on his own profile, and the one that was mis-queued

Wave `profile-modals`, 2026-09-05. Blockers assigned: ledger rows 20
`OPEN-TO-WORK-MODAL` (11W), 42 `OPEN-TO-HIRING-MODAL` (1R/4W), 22
`INTRO-EDITOR-UNREAD-CONTROLS` (4W), 71 `ADD-SECTION-MENU` (1R). All four were
handed to me queued **MEASURE**.

**THE HEADLINE, AND IT IS A REFUSAL RATHER THAN A DELIVERY.** One of the four
cannot be measured by the instruction it carries, because on that surface the
measuring click and the writing click are the same click. That is not this
wave's caution; it is a ruling already written into this package, and I found
it by reading the artifact instead of obeying the queue.

---

## 1. What I did, and what I did not

**DID:**

* Read the `set_open_to_work` WriteSpec, `linkedin_server/writes.py:838-946`,
  and the census block it is quoted in, `_audit/_census/profile.md:337-373`.
* Built a PRESENCE instrument, `scripts/_probe_profile_modal_presence.py`,
  with a two-directional control that gates its own report, and ran it live
  against his profile and the intro editor.
* Pressed exactly one control -- the add-a-section menu button -- and read the
  page before and after as two absolute counts.
* Extended it with an AIM reader -- named is not pressable -- and ran it a
  second time, which **refuted a number in section 6.3 of this document.**
  Section 6.4 carries the correction, beside the claim rather than at the foot
  of the file.
* Recomputed the cost of row 20 from the artifacts rather than from the ledger.
* Had the denylist question re-measured against a corpus of my choosing by a
  slice that imported the shipped predicate instead of rebuilding it.

**DID NOT:**

* **Did not open the open-to-work editor, and did not press its entry
  control.** Section 2 is why.
* **Did not narrow the denylist**, which my brief named as this wave's
  boundary cost. Section 3 is the measurement behind declining it. The four
  frozen boundary lists are byte-identical across this wave; I recomputed
  nothing because I changed nothing.
* Did not edit `_audit/2026-09-03-linkedin-gap-blockers.md`. Two other waves
  have committed to it today (`71abba1`, `a91469b`); its re-costing is the
  lead's and my numbers below are stated against it, not inside it.
* Did not build a tool for any of the four rows. Nothing here is registered on
  the MCP surface and nothing here can be called.
* Did not settle `OPEN-TO-HIRING-MODAL`'s four write rows beyond presence and
  aim.
* **Did not touch `dom.py`, `server.py`, `readonly.py` or `writes.py`.**
  Recomputed at freeze rather than asserted: the union of paths across all
  four of this wave's commits is three files -- the probe, this document, and
  one row in `tests/test_a_sanitiser_earns_its_entry.py`. So the census fix
  section 6.5 argues for is written down and NOT applied, deliberately: both
  modules were contended all afternoon and the remedy belongs to whoever owns
  the census.

---

## 2. Row 20 is queued MEASURE and MEASURE is the wrong instruction

`OPEN-TO-WORK-MODAL` carries eleven write rows and the queue says MEASURE --
go and render the modal, read its controls, cost the writes off what is really
there. **That instruction, executed, performs an unconsented write on his live
profile.** The package already says so, in the spec's own
`reversibility_procedure`:

> *"The editor is not url-addressed AT ALL -- its screens are addressed by an
> internal screen id, and its entry control fires a request whose own name is
> saveAndFetchNextStep. So the one click that would first REVEAL the editor is
> also the first click that could CHANGE it, which is why no capture of it may
> be taken except with him watching."*

Three things follow, and they are separable claims:

1. **There is no page to load.** Zero of 237 distinct urls and 37 payload
   paths across all five profile captures reach an open-to-work editor, a
   job-preferences page or a career-interests page (measured 2026-08-24, on
   the spec). A MEASURE row normally means "open the address nobody opened".
   Here there is no address to open.
2. **The only route in is a click, and that click is the write.** So the
   render this row asks for cannot be bought without spending the thing the
   render was supposed to cost out.
3. **Therefore the row is not blocked by a missing observation. It is blocked
   by a decision only he can make** -- whether to sit and watch one capture
   being taken. That is a `DECIDE` row, and specifically an operator-present
   one, which is a class this ledger does not currently have.

**AND THE COST IS ALREADY MOSTLY PAID, which nobody has counted.** The ledger
costs row 20 at 8 = `denylist x1` + `WriteSpec` (3W) + the rest. The WriteSpec
is not owed: **it exists, in full, and has since `8da9d46`.** 109 lines at
`writes.py:838`, carrying `summary`, `direction_source`, three
`audiences` strings written out verbatim, `reversibility_class`,
`reversibility_evidence` (including its own 2026-08-24 self-correction),
`reversible_by`, `residue` and `reversibility_procedure`. The consent text
this wave was asked to design is written, reviewed, and better than what I
would have produced cold: it names the green `#OpenToWork` frame as the single
setting on this account an employer can read.

So row 20's honest cost is not 8. **`3W` is spent, and `denylist x1` buys
nothing (section 3). What remains is one operator ruling.** I am not restating
the ledger total on my own authority -- that is the lead's -- but the
component I was sent to build is already in the tree, and a wave that did not
read `writes.py` would have built it a second time.

**The census and the ledger disagree about these eleven rows and the
disagreement is legible.** `_audit/_census/profile.md` block I marks I2-I12 --
exactly eleven rows -- **EXCLUDED-RULED**, and states the ruling explicitly:
*"Open To Work stays EXCLUDED-RULED and was NOT promoted to the fifth state"*.
The ledger counts the same eleven as GAP under a blocker queued MEASURE. I am
not adjudicating which document is current. I am recording that **a wave
routed by the ledger alone is told to press a control the census has ruled
must not be pressed**, and that the two documents are three commits apart on a
tree eleven waves are writing.

### What a consented capture would cost, written now so it is cheap later

If he ever says yes, this is the shape, and it needs no boundary edit:

* He watches. One click on the `Edit` control on the open-to-work card --
  **not** the `Open to` button, which the spec's own 2026-08-24 correction
  proved resolves to three items (Hiring, Providing services, Finding
  volunteer opportunities) and **none of them is the audience editor**.
* The census reads the modal. Nothing in the modal is pressed.
* He closes it himself.

The trap that correction exists to stop is still live and worth restating: a
capture attempt aimed at `Open to` **fails silently** -- it opens a menu, the
menu has three items, none is the thing, and a wave reports "the editor draws
three controls."

---

## 3. I decline to narrow the denylist, and here is the measurement

My brief costed this wave a `denylist x1` and warned -- correctly -- that
narrowing a forbidden substring is the most dangerous edit in this repo,
because the entry exists to stop something and the narrowing must name what it
stops stopping.

`linkedin_server/readonly.py:1011-1012` carries two entries:

    "opentowork",
    "open-to-work",

**Narrowing them would buy nothing, because they were already measured to
match nothing.** The spec's own enumeration, quoted above, reports that across
all five profile captures *"the strings 'opentowork' and 'open-to-work' occur
zero times anywhere."* A substring gate cannot admit an address that does not
exist. The editor is not url-addressed; the denylist is not what is standing
in the way, and removing it would trade a live guard for zero reach.

**The general form, because this wave nearly made the mistake the other way
round:** a boundary cost written into a ledger row is a HYPOTHESIS about what
blocks the row. Row 20's says `denylist x1`. The artifact says the blocker is
that there is no url at all. **Those are different blockers with different
remedies, and only one of them is edited by touching the denylist.** A wave
that discharged its assigned boundary cost without checking would have weakened
a guard to reach a surface that has no address.

So: the four frozen lists are untouched, and there is no digest to recompute.
That is a stronger statement than a re-pin, and it is checkable in one command.

**INDEPENDENTLY RE-MEASURED, because the quote above is a year-old reading
against a corpus that has moved.** A slice re-took it today over a corpus this
wave chose rather than the one the spec used -- 42 files across
`tests/fixtures/` and `_audit/_census/`, 246 distinct url-shaped strings --
and ran the causal form of the question rather than the containment form:
**how many of those strings does `readonly.is_read_url` refuse, that it would
admit if only those two entries were removed?** It monkeypatched the shipped
tuple inside its own process and imported the shipped predicate rather than
reimplementing it, which is this repo's standing rule after two home-made
sweeps disagreed with the shipped one.

    url-shaped strings containing "opentowork"     0
    url-shaped strings containing "open-to-work"   0
    admissions those two entries cost              0

**AND ITS FALSE-NEGATIVE CHECK IS THE PART THAT MAKES THE ZERO WORTH
ANYTHING.** A zero over a regex-extracted corpus is exactly the reading that
looks the same when the extractor is broken, so the slice went back to the RAW
TEXT and found the substrings ARE present -- as prose, and as a feature-flag
key -- and never in a url. **So the extractor works and the zero is about
addresses.** That is a stronger result than the containment zero on its own,
and it is a correction to the shape of my own claim: the strings are not absent
from the repo, they are absent from the class the denylist can act on.

**Two independent corpora, taken a year apart by different methods, agree at
zero.** The containment reading says the entries never match; the causal
reading says removing them would change no verdict. Those are different
claims and both were taken.

The slice's own caveat travels with it and I am not dropping it: `git ls-files`
returns nothing for the `_audit/_probe-*.html` glob, so the probe captures
listed in this repo's audit directory are UNTRACKED and were not in its
corpus. That is a hole in the denominator, not a zero -- but it cuts toward
the same conclusion, since an untracked capture cannot be what a shipped
denylist is protecting.

---

## 4. The census counts menu items and never lists them

`ADD-SECTION-MENU` (row 71) is queued MEASURE on the premise that the menu's
contents are unread. **That premise is half wrong and the half that is wrong
matters.**

Census `profile.md` D25 already enumerates nineteen items in three groups --
Core, Recommended, Additional -- **from a LinkedIn Help article (`a540837`),
not from his rendered page.** So what is unread is not "what the menu
contains" in general; it is "what THIS account's menu draws", which is a
different and smaller question.

**And the shipped census could not answer it even if it pressed.**
`dom.CENSUS_CONTROL_SELECTOR` is:

    button, a[href], input, textarea, select,
    [role="button"], [role="link"], [role="textbox"], [role="combobox"],
    [contenteditable]:not([contenteditable="false"])

**Measured mechanically rather than eyeballed** (regex over both strings
verbatim): the `counts` block names **6** ARIA roles, the control selector
names **4**, and **only `button` overlaps.** Five roles are counted and never
listed as an individual control:

    dialog   menu   menuitem   menuitemcheckbox   menuitemradio

So a menu item that is not also a button or a link is **counted and never
listed**: press the menu, `counts.menu_items` moves, `controls` does not.
`writes.py:7348` already records this for one menu; the measurement here is
that it is not one menu's problem but a **five-role hole in the census's
listing**, and `dialog` being in it matters more than `menuitem` -- every
blocker in this wave's set is named for a MODAL, and a dialog's contents reach
`controls` only through whatever buttons happen to sit inside it.

That is the `CENSUS_CONTROL_SELECTOR` failure this repo has hit before, still
live: an instrument aimed at a role that is not there, reporting a clean
absence.

---

## 5. The instrument, and the failure it was shown producing

`scripts/_probe_profile_modal_presence.py`. Read-only apart from one menu
press, attaches (never launches), closes THE PAGE in a `finally`, and emits
integers, relations and shapes -- no accessible name, href or page text leaves
the process. The needles are this file's own literals, matched inside the page,
with only a count returned.

**IT IS A PRESENCE INSTRUMENT AND THAT IS DELIBERATE.** Three waves today
measured CHANGE at a question about whether controls EXIST. All four of my
rows ask "is this drawn at all", so every live number below is an absolute
count taken directly. The one before/after pair is printed as two absolute
readings, never as a difference.

**THE CONTROL RUNS FIRST AND GATES THE REPORT.** A needle reader's most likely
output is a zero, and a zero from a working reader and a zero from a broken aim
are the same character. So the same reader is aimed at markup this file owns,
where the answer is known in both directions, and the expected integers live
outside the detector:

    needle add_profile_section   expected 2
    needle open_to               expected 1
    needle must_be_absent        expected 0
    struct menus                 expected 1
    struct menu_items            expected 3
    struct dialogs               expected 0

If the must-find needle reports 0 the live numbers are not printed at all. The
`must_be_absent` needle is the shown-failing half: it names a string no
LinkedIn surface draws, so a reader that matches everything is visible as
broken rather than as thorough.

RESULTS -- see section 6.

---

## 6. Live readings, 2026-09-05, one attach, one process

Control block: **6 of 6 PASS**, both directions. `must_be_absent` returned 0
and `add_profile_section` returned 2 against the same reader on markup this
file owns -- so a live 0 below is a fact about the page and not about the aim.

### 6.1 -- his profile, first read

    controls matched by the census selector   67
    needle add_profile_section                 0
    needle edit                                4
    needle open_to                             4
    needle hiring                              0
    needle providing_services                  0
    needle volunteer                           0
    needle must_be_absent                      0
    dialogs 2   menus 0   menu_items 0
    aria-expanded=false 11   aria-expanded=true 0
    aria-haspopup 1   aria-modal=true 0

**`add_profile_section` is 0.** The control row 71 is named for is not drawn
on this render, and the reader that says so found two of them a second earlier
in its own control fragment. **The press did not happen and the probe said so
rather than widening its aim until something matched** -- which is the failure
mode this wave was warned about, arriving on the first live run and reporting
itself.

**`menus` and `menu_items` are both 0 on an unpressed page**, so nothing here
is a menu until something is pressed, and the four `edit` and four `open_to`
matches are buttons on cards.

### 6.2 -- THE FINDING THAT OUTRANKS THE REST: this surface drifts under you

Two readings of the SAME page, in the same process, with **no navigation and
no successful press between them**:

    census-selector controls    67  ->  80      (+13)
    dialogs                      2  ->   4      (+2)

Nothing was pressed. The add-section press was refused for want of a target,
and both readings bracket that refusal. **The +13 and the +2 are hydration.**

That is a measured, on-this-surface, same-session demonstration of the law
this repo derived three times today the hard way: **a delta cannot answer a
question about presence.** A wave that pressed a real control here and read
"+13 controls appeared" would have credited its press for the page finishing
its own render. The magnitude is not marginal -- +13 is 19% of the starting
count, and larger than most menus this server would want to measure.

**The practical rule for anyone censusing his profile: take absolute counts,
and take them twice.** A single reading of `/in/me/` is a reading of one
moment of a render that is still moving.

### 6.3 -- the intro editor

Requested `/in/me/edit/intro/`; the landing was NOT the requested path and was
within member space. (That relation was reported by the FIRST version of
`_relation` in this probe, before section 5's byte-identical replacement --
the reading is a relation either way and no address was emitted, but the
function that produced it is not the one in the file now, and saying so is
cheaper than implying otherwise.)

    controls matched by the census selector   252
    needle edit                                7
    needle open_to                             5
    needle hiring                              3
    needle add_profile_section                 0
    needle providing_services                  0
    needle volunteer                           0
    needle must_be_absent                      0
    dialogs 5   menus 0   menu_items 0
    aria-expanded=false 37   aria-expanded=true 0
    aria-haspopup 1   aria-modal=true 0

**SUPERSEDED BY SECTION 6.4 OF THIS FILE, four sections below, before this
document was ever pushed.**
This paragraph read: *"252 against a pin of 255 (`server.py:4034`) --
consistent with the census having read this surface, and re-dated today rather
than resting on 2026-09-02."* **A second run of the same probe eleven minutes
later read 96.** The agreement with the pin was a coincidence of the moment,
and I recorded it as corroboration because it flattered the reading. The
sentence is kept rather than deleted so the mistake is legible; the number it
rests on is not a measurement and section 6.4 says why.

**252 census-visible controls where `linkedin_profile_editor_fields` read 17.**
Those two numbers count different things -- the field reader is looking for
labelled form fields and the census selector takes every button and link on the
page -- but the gap is the size of `INTRO-EDITOR-UNREAD-CONTROLS`' whole
premise, and nobody had put the two numbers next to each other. Census section
5.1 says nine block-A rows are blocked purely by "not among the 17 read", with
**no boundary move and no new permission needed.** That remains the single
cheapest group in my four blockers and it is a re-read, not a press.

**37 controls carry `aria-expanded="false"` and none carries `true`.** Every
disclosure on that page is shut. That is the presence reading a delta-based
pass would have had to infer. (Run 2 read 12 on the same surface. See 6.4.)

---

## 6.4 -- SECOND RUN. Two things it settled, and one of them is against me.

The probe was extended with an AIM reader and run again, same process shape,
eleven minutes later.

**THIS SECTION SUPERSEDES 6.3 ABOVE**, which read a count of 252 as
corroborating a pinned 255. The second run read 96.

NO `CORRECTS:` MARKER, AND THE REASON IS A MEASUREMENT ABOUT THE MACHINERY
RATHER THAN A SHORTCUT. I wrote the marker pair first and
`test_a_correction_is_findable_from_the_claim.py` refused it twice: a marker
naming the file it lives in resolves ZERO documents. So the correction
machinery does not model a document correcting itself -- and on inspection it
should not, because the failure it exists to stop cannot happen here. That
scar is that a reader who starts at the wrong claim can never find the
corrector, since only the corrector names the correction. **When both are the
same file, a reader who reaches 6.3 has already reached 6.4.** The pointer at
6.3 is four sections from the fix, in the reading order, which is stronger
than a cross-file marker and needs no index to survive.

Recorded because the next wave to correct its own document in-flight will hit
the same two reds and should not spend the round I spent.

### The census control count on these surfaces is not a measurement

Six readings, two processes, **no press succeeded in either run**:

    /in/me/              67   80   |   80   235
    /in/me/edit/intro/        252   |        96
                        run 1      |  run 2

`/in/me/` spans 67 to 235 -- a factor of 3.5. `/in/me/edit/intro/` read 252
and then 96. **Nothing was pressed and nothing navigated between the paired
readings**, so none of this is an effect anybody caused.

**SUPERSEDED BY SECTION 6.5. The sentence that stood here read: "a single
census control-count of either surface supports nothing", and a series taken
twenty minutes later showed the count settling and staying settled.** It is
kept because the mistake is the instructive part: I drew "never settles" from
six PAIRED readings, which is exactly the inference a pair cannot support --
the same shape as the delta-for-presence error I had spent the afternoon
naming in other people's work. Section 6.2's +13 hydration reading was right
and my escalation of it was not.

The sentence as it should have read: **a single census control-count of either
surface supports nothing, BECAUSE OF WHEN IT IS TAKEN and not because the
quantity is unstable.** That reaches `server.py:4034`'s pin of 255 for
`profile_edit_intro`, and it reaches the census note at `server.py:4000` that
the surface *"was read TWICE at 67 controls and twice at 256"* -- which reads
as two stable states and is equally consistent with two samples of a quantity
that does not settle.

**What would settle it: N readings of one surface in one process at spaced
intervals, reported as a series. I said nobody had taken it, then took it.**
Section 6.5.

### 6.5 -- I TOOK THE SERIES, AND IT REFUTED 6.4. The count settles.

`--series`: one navigation, eight reads, 1500ms apart, same process.

    /in/me/              80  235  235  235  235  235  235  235
                         min 80   max 235   distinct 2   last three equal
    /in/me/edit/intro/  252  252  252  252  252  252  252  252
                         min 252  max 252   distinct 1   last three equal
    dialogs              4 x8 on the profile, 5 x8 on the editor -- flat

**Both surfaces settle, and one settles after a single read.** Every
"unstable" number in 6.2 and 6.4 was a FIRST read, taken in the moment after
navigation while the page was still hydrating. There is no instability. There
is a reader that does not wait.

**THIS EXPLAINS A BIMODALITY THIS PACKAGE RECORDED AS A MYSTERY.**
`server.py:4000` notes `profile_edit_intro` *"was read TWICE at 67 controls
and twice at 256"*, and that has been carried as two states of the surface.
**They are one state read at two moments** -- 67 is a pre-hydration read and
256 a settled one. My own runs reproduced exactly that split on the profile
(80 then 235, seven times 235) without pressing or navigating anything.

**So the remedy is not to distrust the census. It is to make it wait**, and
the wait has a written stop condition rather than a magic number:

    read until the last three reads agree, then report -- and report the
    number of reads it took, so a surface that never converges is visible
    as one rather than silently truncated at a timeout.

That is buildable, cheap, needs no boundary and no ruling, and it retires a
whole class of "the count moved" reds. It is the single most valuable thing
this wave found and it was found by taking a measurement I had already written
down as owed.

**And the pin: today's settled value is 252 against a pinned 255.** Those are
close and they are not equal, and after the above I will not call a
three-control gap corroboration in either direction. It is a settled reading
that disagrees with a settled pin by 3, taken three days later on a profile
whose content changes.

### AIM: named is not pressable, and on this page it mostly is not

The aim reader counts, per needle, how many named controls carry an
ACTIVATION relation (`aria-haspopup`, `aria-expanded`, `aria-controls`). Its
rule is a pure function controlled in four branches with the expected verdict
written outside it. On his profile:

    add_profile_section   ABSENT -- 0 controls carry the name
    edit                  NAMED BUT INERT -- 6 named, 0 with any relation
    open_to               AMBIGUOUS -- 3 of 5 carry one
    hiring                NAMED BUT INERT -- 3 named, 0 with any relation

**Three consequences, and each retires a plan somebody would otherwise make.**

1. **`ADD-SECTION-MENU` (row 71) cannot be pressed because the control is not
   drawn**, at count 0, from a reader that found 2 of them in its own fragment
   seconds earlier. Whatever draws that menu is not on this render.
2. **`OPEN-TO-HIRING-MODAL` (row 42): `hiring` is named 3 times and carries no
   activation relation at all.** A wave told to press the Hiring entry has
   nothing evidenced to press. This does NOT prove the control is not
   clickable -- a React handler needs no aria attribute -- and that distinction
   is the whole reading: **the page offers no evidence about what opens, so any
   press here is a guess wearing a selector.**
3. **`open_to` is AMBIGUOUS: 3 of 5 named controls carry a relation.** A press
   would be choosing between three. That is exactly the bar
   `linkedin_send_message` enforces on recipients -- *exactly one, or refuse* --
   arriving unbidden on a different surface, and it is the same trap as the
   spec's own 2026-08-24 correction, where aiming at `Open to` would have
   opened a three-item menu containing none of the thing.

**AND THIS IS WHERE `CENSUS_CONTROL_SELECTOR` WOULD HAVE FAILED SILENTLY.**
`menus` and `menu_items` read 0 on every reading of both surfaces. A census
aimed at a menu role finds nothing here -- not because the page has no menus,
but because none is open and the selector that would list their items does not
carry the role anyway (section 4). **A clean absence and a blind instrument
produce the same table**, which is why the aim verdict distinguishes ABSENT
from NAMED BUT INERT rather than reporting one count.

### A caveat on the relation strings, stated rather than buried

Run 1's landing relations were produced by this probe's FIRST `_relation`,
which compared paths; run 2's by the sanctioned byte-identical one, which
compares depth. **The two runs' relation strings are not comparable and I am
making no claim from their difference.** The control counts are comparable
because the reader did not change.

---

## 7. What is still owed

1. **An operator ruling on row 20.** Not a measurement. The question is
   narrow: *may one capture of the open-to-work modal be taken with you
   watching, knowing the click that opens it is a request named
   `saveAndFetchNextStep`?* Everything else on those eleven rows is written.
2. **A re-queue of rows 20 and 71 from MEASURE.** Row 20 is operator-gated;
   row 71 is a tool, not an observation. Neither is what its queue says.
3. **`OPEN-TO-HIRING-MODAL` (row 42) is genuinely MEASURE and I got it to the
   aim and no further.** Section 6.4: `hiring` is named 3 times on his profile
   and carries no activation relation; `open_to` is ambiguous at 3 of 5. So
   the next step is NOT a press -- it is deciding which of the three `open_to`
   openers is the menu, and that is settled by reading their relations, not by
   pressing one and seeing what happens.
4. **DONE, and it changed the answer -- see 6.5.** This item read: *"a
   stability series on the census control count ... the cheapest high-value
   thing left in my four rows."* I took it before winding up. The count
   settles; what does not is when the census reads it. **What that item
   becomes: teach the census to wait -- read until the last three reads agree,
   report the number of reads it took.** No boundary, no ruling, no write, and
   it retires a class of "the count moved" reds across every surface this
   server censuses, not just my four. It is the largest thing this wave found
   and it is not mine to build: `linkedin_surface_census` and `dom.py` were
   contended all afternoon and I did not touch either.
5. **The `_probe_*.html` captures under `_audit/` are UNTRACKED** (section 3).
   Any argument resting on "measured across all five profile captures" is
   resting on files a clone does not have.
4. **The intro editor's control set has a measured two-day half-life**
   (finding 7.6: 23 controls on 2026-08-31, 17 on 2026-09-02, *a different
   set*). Any row in census block A resting on the 2026-09-02 reading is now
   three days old.
