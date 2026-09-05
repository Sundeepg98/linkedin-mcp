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
* Recomputed the cost of row 20 from the artifacts rather than from the ledger.

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
* Did not settle `OPEN-TO-HIRING-MODAL`'s four write rows beyond presence.

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

It carries **no menuitem role**, while `CENSUS_JS`'s `counts` block does
(`[role="menuitem"], [role="menuitemcheckbox"], [role="menuitemradio"]`). So a
menu item that is not also a button or a link is **counted and never listed**:
press the menu, `counts.menu_items` moves, `controls` does not. `writes.py:7348`
already records this for a different menu; this wave measured it on the
add-section menu directly, and section 5 carries the numbers.

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

**252 against a pin of 255** (`server.py:4034`) -- consistent with the census
having read this surface, and re-dated today rather than resting on 2026-09-02.

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
pass would have had to infer.

---

## 7. What is still owed

1. **An operator ruling on row 20.** Not a measurement. The question is
   narrow: *may one capture of the open-to-work modal be taken with you
   watching, knowing the click that opens it is a request named
   `saveAndFetchNextStep`?* Everything else on those eleven rows is written.
2. **A re-queue of rows 20 and 71 from MEASURE.** Row 20 is operator-gated;
   row 71 is a tool, not an observation. Neither is what its queue says.
3. **`OPEN-TO-HIRING-MODAL` (row 42) is genuinely MEASURE and genuinely
   cheap** -- the `Open to` menu item is observed across five captures and
   resolves to three items, one of which is Hiring. Nothing acts on it and
   nothing has to be pressed to cost it. It is the best-value row of my four
   and I did not get to it beyond presence.
4. **The intro editor's control set has a measured two-day half-life**
   (finding 7.6: 23 controls on 2026-08-31, 17 on 2026-09-02, *a different
   set*). Any row in census block A resting on the 2026-09-02 reading is now
   three days old.
