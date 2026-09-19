# The anchor reader: one module, and two of my own predictions refuted by it

Wave `anchor-reader`, 2026-09-19, 10:29 to 12:xx by the box (`date`, stamps in
section 7). **No write fired, no boundary moved.** Four live reads, one address
per surface plus deliberate repeats, badge read before and after, tab closed
every time.

## 1. WHAT IT IS, AND WHY THE OBVIOUS DESIGN IS THE FORBIDDEN ONE

Three read-tail surfaces need anchors the shipped census cannot give.
`read_surface_census` carries `has_href` and `href_shape` and **never hands out
a raw href by construction** -- measured, `(no href)` on 147 of 147 controls of
a page made entirely of links, which presented as a clean zero rather than an
error.

**And an anchor reader that can see hrefs can see `/in/<slug>`, and a slug is a
name.** So `linkedin_server/anchors.py` does not see them either.

> The route table is shipped INTO the page, the comparison happens in the
> document, and what crosses the CDP boundary is a **POSITION IN A TUPLE**
> defined in the module.

It answers **which SHAPE** an anchor is, from a closed alphabet, never **which
anchor**. `member_profile` is the hazard class: counted, never described. No
address is a parameter of any publishing function, asserted on
`inspect.signature`.

## 2. THE SEGMENT RULE -- and the prediction that produced it was WRONG

`menus.py`'s scar: `classify("Star Anise")` returned `star`, because containment
was applied at every phrase length and **the hazard had been treated as a
property of one WORD rather than of every single-word term.**

Here a route term tested by containment matches inside any segment, so a term
must be a **whole path segment at a fixed position**. I wrote that rule, and I
wrote down what I expected the containment version to do: move a name-bearing
anchor OUT of `member_profile`.

**Run against the control fixture in a page, it did the opposite:**

    member_profile   1 -> 4        help_article   1 -> 0
                                   messaging      1 -> 0
                                   school_page    1 -> 0

because **`in` is a substring of `linkedin`, `messaging` and `institute`.** A
help article, a messaging thread and a school page were all reclassified as
member profiles.

**Over-reporting the hazard class is not the safe direction.** It makes the one
count a caller must never publish per-record wrong by 4x, and tells a caller a
page is full of people when it holds one.

**AND MY OWN DEMONSTRATION UNDERSTATED WHAT IT HAD JUST MEASURED.** Its branch
only checked whether `member_profile` FELL, and printed *"member_profile held;
the harm landed on other classes"* -- while the hazard count had quadrupled.
That is the probe set agreeing with its author, and it is the third instance in
my work today. The module docstring, the test comments and a new test now carry
the measured number instead of the predicted one.

## 3. THE CONTROL CARRIES A WRITTEN EXPECTATION

`CONTROL_EXPECTATION` is spelled out in the module, because **a control whose
result nobody predicted cannot fail.** It covers all 13 classes and the probe
ABORTS if the fixture does not reproduce it.

It carries the two adversarial anchors that convict a containment design:

    /company/star-anise-school/        must stay company_page
    /in/star-anise-company-ltd/        must stay member_profile

Reproduced exactly on every run. **The slugs are synthetic and deliberately not
people** -- `menus.py` uses a spice for the same reason: a tracked file may not
carry a third party's name even as an illustration.

## 4. THE HEADLINE MEASUREMENT: 9 POSTINGS WHERE THE CENSUS SAW ZERO

    surface                anchors   notable classes
    job collections          25-35   job_posting 9, company_page 6-9
    jobs search                 28   job_posting 9, company_page 9
    premium (entitlement)       46   premium_surface 12, external 8, member 1

**The collections page draws 9 job postings. The census-based probe measured
ZERO on the same address.** That is the entire argument for this module,
demonstrated rather than asserted.

## 5. A DISCRIMINATION I PUBLISHED AND RUN TWO REFUTED

Reads were interleaved deliberately -- collections, premium, collections, jobs
search, premium -- because an adjacent pair had given near-identical profiles,
which has two explanations (one shared shell, or an SPA that did not re-render).

    RUN 1   collections == jobs search      FALSE
            premium == premium               TRUE
            collections A == collections B   FALSE
    RUN 2   collections == jobs search      FALSE   <- held
            premium == premium              FALSE   <- FLIPPED
            collections A == collections B   TRUE   <- FLIPPED

**I wrote run 1 up as "the reader is deterministic and the collections surface
is not". Minutes later both comparisons inverted.** Withdrawn.

**The narrower true statement: both surfaces move between loads, and which one
happens to repeat is itself unstable across runs.** A single run of a comparison
is not a comparison -- a control proves an instrument CAN speak, and only
repetition proves what it said was stable.

**The reader's determinism is proven elsewhere and better.** The DETACHED
fixture reproduced its expectation on every run, and that is the only place the
input is held constant -- so it is the only place determinism can be read at
all. A live repeat varies the DOM and the reader together and cannot separate
them. **What did hold both times** is the comparison that was not about
stability: collections and jobs-search differ, so they are not one shell.

**One number that outranks the rest:** collections showed **4 member_profile
anchors on one load and 0 on another.** A hazard-class count that appears and
disappears between loads is the strongest available argument for counting that
class and never describing it.

## 6. "SERVE ALL THREE SURFACES" -- and it is not a clean yes

The brief asked for one reader across job-collections, school and premium, and
said to name what it cannot do rather than ship two.

| surface | classification | page opened |
|---|---|---|
| job collections | **yes** -- 9 postings, 6-9 company anchors | **yes**, 4 loads |
| premium | **yes** -- 12 premium anchors on the entitlement page | **yes**, but see below |
| school | **yes** -- proven by the control fixture | **NO** |

**PREMIUM, PRECISELY.** The page I read is `/premium/my-premium/`, the
ENTITLEMENT page. The census's premium rows (`J 114`, `J 123`, `J 124`, `J 126`)
are Premium *Page Insights* on company pages -- a different surface I did not
open. The reader works there in principle; nothing here measures it.

**SCHOOL, AND THE REASON IS A RULING RATHER THAN AN OMISSION.** Opening
`/school/<slug>/` requires a slug, and **a slug is a name.** To obtain one this
server would have to read it off his profile's education section first -- which
is reading a name in order to navigate by it. The reader CLASSIFIES school
anchors correctly (the control proves it, and it is the exact case a containment
matcher gets wrong), but **reaching a school page needs a ruling this wave did
not have and did not take.**

## 7. WHAT THIS WAVE DID NOT DO

* **No tool wiring.** The reader has no `linkedin_*` entry point, so no census
  row moves to COVERED on its account. `server.py` is permanently contended.
* **No boundary change.** 32 patterns in, 32 out.
* **No disclosing press.** The ruling exists (`c48ec60`) and the mechanism does
  not; an anchor rendering only behind a disclosure is invisible here and that
  is a stated limit, not a measurement.
* **No school page opened**, for the reason in section 6.

Stamps, by the box:

    Sat, Sep 19, 2026 10:29:52 AM   start; Chrome identity re-checked first
    Sat, Sep 19, 2026 10:32:01 AM   control fixture matches its expectation
    Sat, Sep 19, 2026 10:37:14 AM   reader + 13 tests committed
    Sat, Sep 19, 2026 10:41:22 AM   run-2 refutation recorded

## 8. MY ROWS REACHED HEAD IN SOMEBODY ELSE'S COMMIT AGAIN -- and the rule I wrote does not cover it

Census rows `J 42` and `J 112` carry this wave's annotations in HEAD, committed
by `58c3101` -- another wave's. **Byte-identical to what I wrote, so nothing is
lost and nothing is rewritten.** Credited here and routed, per the standing
protocol. That is the second time today, after `J 10` in `6353f6b`.

### THE WINDOW IS EDIT-TO-COMMIT, NOT STAGE-TO-COMMIT

After the first instance I adopted -- and the lead recorded as standing -- *stage
and commit in ONE chained command, never two steps with thinking in between.*
**I followed it here and it did not help**, which makes the rule narrower than
it reads:

    stage -> commit    the window that rule closes
    EDIT  -> commit    the window that actually matters on a shared file

My edit landed in the working tree; the neighbour ran `git add` on that path
minutes later, for their own reasons, and committed everything in it. **A
chained stage-and-commit closes seconds at the END of that window and leaves
the whole editing interval open.** On a file several waves append to, the only
thing that shortens the real window is editing and committing in one motion --
and even then a neighbour's `git add` between the two is unpreventable.

### WHAT ACTUALLY WORKED, and it is worth keeping

The blob technique from section 6 of `_audit/2026-09-19-read-tail.md` -- build
HEAD-plus-only-my-rows, `git hash-object -w`, `git update-index --cacheinfo` --
**refused correctly here rather than doing damage.** Run after the neighbour's
commit, it reported *"already identical to HEAD"* for both rows and staged
nothing, because its premise (my rows differ from HEAD) was false. A tool that
discovers its own premise has expired and stops is the behaviour worth having;
it is how I learned the rows had already landed.

### THE HONEST ACCOUNTING

**Three of this session's census rows reached history under other waves'
commits, and every one of them is content I wrote and stand behind.** The cost
is attribution, not correctness, and the remedy is credit rather than a rewrite
-- rewriting HEAD in a tree with several live writers trades a mis-attributed
line for something genuinely hard to undo.
