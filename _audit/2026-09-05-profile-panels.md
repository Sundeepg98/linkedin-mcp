# profile-panels -- 19 rows on his own profile's panels

Wave window 18:47 -> 19:30 BY THE BOX (`date`, +0530). Every timestamp here was
taken with `date`, not from an agent's sense of elapsed time.

    18:47:11   wave start
    18:52:35   the live probe attached over CDP
    18:52:54   the taint guards ran against the new probe
    18:56      this document
    19:03      run 2 aborted on a regex it built badly, and cost one page load
    19:05      run 3: a second instrument, and it settled both declared defects

## WHAT THIS WAVE ACTUALLY MOVED

| row | blocker | queue | what happened |
|---|---|---|---|
| 38 | `CONTACT-INFO-PANEL` | MEASURE | **MEASURED LIVE. The panel was opened for the first time in this repository.** |
| 39 | `RECOMMENDATIONS-SURFACE` | DECIDE | ruling and design recorded below. **The module was delegated and NEVER ARRIVED** -- measured on disk at 19:07, neither file exists. Nothing recommendations-related is in the tree |
| 43 | `BADGES-SURFACE` | BUILD | **NOT STARTED** |
| 72 | `MULTILANG-PROFILE` | BUILD | **NOT STARTED** |
| 78 | `OPEN-PROFILE-SETTING` | BUILD | **NOT STARTED** |

Three of the five blockers were not touched. They are BUILD rows costing
allowlist +1 and a WriteSpec each; none of them is closer than it was at 18:47.

---

## 1. `CONTACT-INFO-PANEL` -- THE MEASUREMENT

The instrument is `scripts/_probe_contact_info_panel.py`.

> **CORRECTED at 18:58 by the box.** This line read *"It is NOT in this commit"*
> when committed at `e69c348`, and section 3 argued the case for leaving it out.
> The guard red was then diagnosed and fixed, and the probe IS committed. The
> superseded reasoning is kept in section 3 rather than deleted, because the
> diagnosis is the useful part and a record of a defect may not outlive the
> defect quietly.

### It added no address. It pressed one.

`/in/me/` is already on `readonly._ALLOWED_URL_PATTERNS`. The overlay address is
not, and the probe never navigates to it: it presses the affordance the profile
page already draws and reads what renders in place. That is exactly why the
ledger costs this row as a MEASURE with no allowlist entry.

### The presser was shown able to report an absence

The same presser ran first at `/mypreferences/d/dark-mode`, an admitted read
page that draws no contact-info affordance:

    CONTROL PAGE      status control_absent   controls 0   dialogs 0

So a clean absence and a broken presser are DISTINGUISHABLE on this instrument.
That check exists because `CENSUS_CONTROL_SELECTOR` shipped here aimed at a menu
role that did not exist, certified nothing, and looked green throughout.

### The reading on his own profile

    HIS OWN PROFILE   status pressed
                      controls           1
                      dialogs before     4
                      dialogs after      5
                      rows in dialogs    1
                      links in dialogs   3
                      unmatched dialogs  2
                      label profile      1
                      label email        1
                      label phone        1
                      label im           2

    session control   census 20 then 20 (floor 10) -- PASS at both ends
    invitation badge  read 0 then read 0

Both control readings are PRESENCE readings taken at two moments and printed
side by side. **Neither is subtracted into a delta**, because the question here
is whether a control EXISTS, and a delta cannot answer that.

### What this establishes, stated narrowly

1. **The contact-info control EXISTS on his profile and is pressable.** One
   anchor carrying `dom.PROFILE_EDITOR_HREFS[2]`, pressed, no exception.
2. **Pressing it draws a dialog.** Four dialogs on the page before, five after.
3. **The panel draws three field classes** -- profile, email, phone -- each
   confirmed by a WORD-BOUNDARY match over the visible dialog in run 3. A
   fourth, instant messaging, appeared under the substring rule and is ABSENT
   under the boundary rule. See the run-3 section below.
4. **Nothing about his contact details left the page.** The in-page script has
   no branch that returns a substring of the document; it returns integers and
   keys from the caller's own tuple. That is a structural property, not a
   filter, and it is why a birthday or a phone number could not have crossed
   even if one had been present.

### What this does NOT establish, and two of these are defects in my instrument

> **SUPERSEDED IN PART, and the pointer is here rather than at the foot of the
> file because this is where the stale claim gets read.** The first three
> bullets below were written at 18:56 against run 1 alone. Run 3 settled all
> three -- two in my favour and ONE AGAINST ME. Read the run-3 section before
> quoting any of them. The fourth bullet stands unchanged.

* **`label im 2` IS NOT A READING.** `im` is a two-character token matched as a
  SUBSTRING of the dialog's whole text, so it matches inside ordinary English
  words. This repository has already paid for the substring-versus-token
  distinction once, on an events footer. The count of 2 across 5 dialogs is
  consistent with zero instant-messaging sections. **`profile`, `email` and
  `phone` are longer tokens and are therefore weaker overreach risks, not
  proof-against-overreach** -- all four numbers are UPPER BOUNDS on section
  presence, and none of them is a section count.
* **`rows in dialogs 1` is implausibly low** for a panel drawing three field
  classes. The likeliest cause is that the overlay's rows are not `li` or
  `section` elements, or are rendered outside `[role=dialog]`. Do not read 1 as
  the number of contact rows he has.
* **The dialog count is over the WHOLE PAGE, not the panel.** Four dialogs
  existed before the press; two of the five after matched no vocabulary word at
  all. The press-attributable dialog is one of five and the probe does not say
  which.
* **Five rows are not retired by this.** One press on one aim, once. The row set
  filed against this blocker includes four WRITES, and this measurement says
  nothing whatever about a write.

### A SECOND INSTRUMENT SETTLED BOTH DEFECTS -- run 3, 19:05 by the box

The two caveats above were published as declared upper bounds. Rather than
leave them declared, a second instrument was added to the SAME run so the two
readings could disagree in one place. It shares no input feature with the
first: the first matches by SUBSTRING over EVERY dialog on the page, the second
by WORD BOUNDARY over the VISIBLE dialog only.

    HIS OWN PROFILE      dialogs 5,  VISIBLE dialogs 1
                         visible rows 1, headings 2, links 3, elements 43

    label SUBSTRING      profile 1   email 1   phone 1   im 2
    label TOKEN          profile 1   email 1   phone 1   im --

    CONTROL PAGE         VISIBLE dialogs 0, and every count 0

**THE DISAGREEMENT IS THE FINDING, and it resolves against my first
instrument.** `im` scored 2 by substring and ZERO by token. The overreach
mechanism is known and demonstrable -- `im` occurs inside ordinary words -- so
the token rule wins on mechanism, not on being newer. **There is no instant-
messaging section in his contact panel.** That is now measured; at 18:52 it was
only suspected.

**AND THE THREE THAT AGREE ARE UPGRADED.** `profile`, `email` and `phone` each
survive the boundary rule at 1. They are no longer upper bounds on section
presence -- they are readings.

**ONE OF MY TWO HYPOTHESES ABOUT THE ROW COUNT WAS WRONG.** I wrote that a row
count of 1 was implausible and guessed the rows were either not `li`/`section`
or rendered outside `[role=dialog]`. The second reading REFUTES the second
guess: the visible dialog holds 43 elements and still only 1 `li`/`section`,
so nothing is hiding outside it. The panel is small and its structure is
headings and links -- 2 and 3 -- not list items. **The count of 1 was correct
and my objection to it was not.**

**`VISIBLE dialogs 1` also retires the "one of five" caveat.** Four dialogs
existed before the press and all four are hidden; exactly one dialog was open
after it. The press-attributable dialog is now identified rather than inferred.

### Run 2 died and cost a page load, and the cause is worth one line

Between the two good runs, a version building a JavaScript `RegExp` from the
vocabulary aborted with `Invalid regular expression: missing /`. The escape had
to survive a Python string literal and a JS regex literal at once, and it did
not. **The remedy was to delete the requirement, not to fix the escaping**: a
neighbour-character test needs no escaping and cannot be mis-quoted. The tab
still closed in the `finally`, which is the one thing that had to hold when a
run aborts.

Same class as the freeze ruling's "prose with backticks never goes through a
shell string" -- and it bit again in this wave when a patch script passed
through a heredoc and lost a backslash. **Both were fixed by using the file
tools instead of a shell string.**

### The single-aim caveat, and it is the honest limit

One aim was used: an anchor whose path carries the marker. If LinkedIn also
draws this affordance as a button with no href, this probe cannot see it and
would have reported `control_absent`. It did not report that here, so the
caveat costs nothing THIS run -- but a future zero from this instrument would
be a fact about one aim, not about his profile.

---

## 2. `RECOMMENDATIONS-SURFACE` -- THE RULING, AND WHY IT IS NOT A COPY

The wave lead ruled and I implemented against the ruling: **a recommendation is
written BY a named third party ABOUT him, so this surface is other people's
words under their names. READS publish counts and relations, never names or
text. WRITES -- requesting or giving a recommendation -- are outward-facing acts
naming a real person: design and gate them, fire none.** No write was designed
and none was fired.

`linkedin_server/groups.py` is the pattern and it is name-free STRUCTURALLY: no
name is a parameter of any function in it, asserted on `inspect.signature`, and
a slug is refused there because a slug is a name.

**THE HALF THAT CANNOT BE COPIED.** `groups.py` publishes a numeric group id,
on the argument that a group id names a GROUP and a group's NAME can be a
person's. A recommendation's author href is `/in/<slug>`, and there is no
non-name segment anywhere in it. **So this surface has no publishable
identifier at all**, and the structural property has to be stronger than the
signature rule:

    NO PUBLIC FUNCTION MAY RETURN ANY STRING DERIVED FROM ITS INPUT.
    Every published value is an int, a bool, or a literal from a closed
    module-level vocabulary. Distinctness is computed internally and published
    only as a COUNT.

That property is testable in a way the signature rule is not: sweep every public
callable with an adversarial needle and assert the needle appears nowhere in the
output -- with the sweep factored out as a helper that a deliberately-leaky
local function is fed to, so the passing test cannot be passing because the
detector is dead.

**A DIGEST OF THE SLUG WAS REJECTED, and for a sharper reason than `groups.py`
had.** That module rejected hashing an 8-digit id as brute-forceable end to end.
The slug domain is worse: slugs are enumerable and guessable, so a digest would
be a lookup table wearing a redaction's clothes -- the shape this repository
calls worse than the leak.

**STATUS AT THE FREEZE, MEASURED ON DISK AND NOT RELAYED.** The module and its
test were delegated to an implementer at 18:50. At 19:07 -- 28 minutes later --
`ls` reports neither `linkedin_server/recommendations.py` nor
`tests/test_recommendation_tally.py` exists, and `git status` shows no
recommendations-named file of any kind. **No result of that agent's is reported
here, in either direction:** an agent that has gone quiet is indistinguishable
from one that is working, and only the box can tell them apart. What is stated
is the disk reading and its timestamp.

**So this row did NOT move.** The ruling and the design above are the durable
part, and they are written here precisely because the code is not -- the next
wave starts from the design rather than from the surface name, which is the
whole point of routing the artifact rather than the verdict.

---

## 3. THE GUARD RED, AND IT IS THE SAME MODULE-SCOPE SCAR AS `196394d`

At 18:52:54 the guards were run against the new file:

    pytest tests/test_navigation_is_never_derived.py \
           tests/test_page_text_is_never_printed.py -q -p no:randomly --tb=line

    3 failed, 233 passed in 16.37s

One of the three names this wave:

    scripts/_probe_contact_info_panel.py  0 -> 1

`test_no_file_prints_page_text_beyond_its_pinned_inventory` -- one site where a
value derived from a page read reaches a `print`. The guard's own message says
what to do and what NOT to do: emit a count, a relation or a marker, and do not
add the file to the inventory dict to clear the red.

**The guard is RIGHT and my file is wrong**, even though every value that
actually printed is an integer or a literal I wrote. The taint engine follows
the BINDING, not the content, and it is correct to -- a check that tried to
reason about content is the check this repository keeps catching being wrong for
the inputs it was imagined against.

### THE DIAGNOSIS, and it beats the fix

My first read of this was wrong in the ordinary way: I assumed the flagged site
printed something page-derived, and started designing a `_SANITISERS` entry.
Running the guard's own engine over my file instead of reasoning about it named
the site in one call:

    tainted names: ['after', 'before', 'controls', 'count', 'key', 'value']
    HIT line 234 print :: print(f"    label {key:<18} {count}")

`key` and `value` are the DICT-COMPREHENSION VARIABLES inside
`press_contact_control`, bound from a page-derived object. **The taint engine
tracks names across a MODULE, not per scope**, so binding `key` there tainted
the name `key` everywhere in the file -- including a loop over
`LABEL_VOCABULARY` inside `report()`, a function that touches no page at all
and prints two integers.

That is the identical mechanism `groups-events` root-caused at `196394d`, where
locals named `before` and `after` tainted three prints tallying shaped control
names that touched no url. Reading that entry did not prevent me writing the
same defect; running the guard caught it. **The note is not the control.**

**THE FIX IS A RENAME**, and two things that look like fixes are not:

* `int()` does not launder. `_COUNTING_CALLS` is `frozenset({"len"})` and
  nothing else, so wrapping a tainted name in `int()` changes nothing.
* Assigning to a fresh variable does not launder either -- the fixed point
  follows the binding.

Renamed to `vocab_word` / `vocab_hits` in the comprehension and
`label_word` / `label_count` in `report()`. The guard now reports this file
nowhere. **The rename is documented in the file itself with the measurement
attached**, so the next reader does not undo it as a style preference.

### Verified without spending another live load

The rename touches the print path, and the only end-to-end evidence was from
BEFORE it. Rather than re-run five page loads on his account, the exact dict the
live run produced was replayed through the renamed `report()` and reproduces the
published output line for line. A rename inside a comprehension cannot change a
count; what needed proving was that the renamed path still prints, and that is
proven without touching LinkedIn.

### The other two reds are NOT mine, and I checked rather than assumed

    test_no_navigation_derived_value_reaches_an_output_sink[_probe_profile_modal_presence.py]
    test_every_relation_definition_is_byte_identical

Neither file is this wave's. `_probe_comment_identifier.py 0 -> 12` also appears
in the same inventory failure and is likewise not mine. Routing them is not this
wave's to do from a reading this thin -- name the owner with
`git log --oneline -3 -- <path>` before handing either on.

---

## 4. WHAT I DID NOT DO

* **`BADGES-SURFACE` (5 rows), `MULTILANG-PROFILE` (2), `OPEN-PROFILE-SETTING`
  (1): not started.** No allowlist pattern proposed, no capture taken, no
  WriteSpec drafted. Eight rows untouched.
* **No allowlist pattern was added, and the boundary digest was not recomputed.**
  Nothing this wave did touches `readonly._ALLOWED_URL_PATTERNS`, so there is no
  chain step to append.
* **No write was designed, gated or fired** on any of the five surfaces.
* **No test was added, and the probe was NOT admitted to any instrument
  register.** It has been shown able to report an absence where one is known,
  which is the bar for believing this run -- but its label vocabulary is a
  substring match with a measured overreach (`im`), and an instrument with a
  known overreach should not be registered for reuse until that is fixed.
* **The full suite was not run** and no clone was taken. The only pytest runs in
  this wave are the guard pair quoted above (236 tests at 18:52, 242 at 18:56 as
  the tree moved under me). **Targeted runs clear SHAPE violations, never
  ENUMERATION violations** -- if this probe should have been enrolled somewhere
  by name, no run scoped to these files could have told me.
* **Nothing was pushed.**

## 5. COST, RECOMPUTED RATHER THAN RECALLED

**THE FIRST VERSION OF THIS SECTION UNDER-REPORTED BY MORE THAN HALF, AND IT
UNDER-REPORTED IN THE FLATTERING DIRECTION.** It read *"five page loads"*,
which is the count for ONE run, and there were THREE. Nothing external would
have flagged it: five is derivable from the code, it was mine, and it made the
wave look cheaper than it was. **Recomputing the number caught it; re-reading
the sentence could not have**, which is the same 6x lesson the groups wave
recorded today at a larger magnitude.

Recomputed from the probe's own control flow with `grep -c` rather than from
memory -- **five loads PER RUN**:

    /mypreferences/d/dark-mode, /feed/, /in/me/, /feed/, /mypreferences/d/dark-mode

    run 1  18:52   5 loads   completed
    run 2  19:03   1 load    ABORTED at the first evaluate, on its own bad regex
    run 3  19:05   5 loads   completed
    ------------------------------------------------------------------
    TOTAL         11 page loads, 2 completed presses, 2 Escape presses

One tab per run, opened and closed. `page.is_closed()` read `True` on all
three, INCLUDING the aborted one -- which is the reading that matters, because
the `finally` is there for exactly the runs that do not finish. That is a
presence reading about the one object each run created, not a count over a
pool a dozen waves share.
