# The `/my-items/` premise: one offline route ruled out, and why the claim reads as settled

Second look at `M C36` / `M C37` (`SAVED-POSTS-SURFACE`), whose cost
`_audit/2026-09-19-content-tail.md` section 4.1 corrected upward on the ground
that the `/my-items/` redirect is **asserted, never measured**.

**NOTHING WAS FIRED AND NO BROWSER WAS OPENED.** Every measurement below is
offline, over tracked files. **No pattern moved. `C36` and `C37` stay GAP.**

**THREE RESULTS, and the second is the one worth keeping:**

1. The tracked-fixture route to settling the premise is **RULED OUT, with a
   control** -- so the next wave does not spend a cycle discovering that.
2. The redirect claim is **SHELTERED BY AN ADJACENT MEASURED CLAIM** in the same
   comment, which is why four readers in a row have taken it as settled.
3. The claim is **LOAD-BEARING FOR NOTHING** in the shipped boundary. Both
   things it looks like it supports are justified independently.

---

## 1. THE FIXTURE ROUTE, AND THE CONTROL THAT KILLED IT

The obvious cheap idea: this repo tracks sanitised HTML captures. If LinkedIn
still draws a `/my-items/` link on a page this server ALREADY reads, the surface
is live and the premise gains evidence **without admitting any address**.

    22 tracked .html fixtures
    /my-items/ hits                          0

**A zero from an instrument nobody has shown able to speak certifies nothing**,
so the same scan was run for routes that MUST be present:

    fixture                            href   /in/  /jobs/  /company/  my-items
    manage_pages_following_hydrated      40      0       0         40         0
    job_detail_following_hydrated        24      0       5          8         0
    profile_topcard_hydrated             19     11       0          0         0
    connections_list                     14      7       0          0         0
    jobs_search                           7      0       7          0         0
    ... 22 fixtures, every one non-zero on href

**The control fires: hrefs survive sanitisation and known routes read
non-zero.** So the zero is a real absence -- and it is still worthless, for a
reason the control does not cover.

> **THE ZERO MEASURES THE CORPUS, NOT LINKEDIN.** The 22 fixtures capture job
> detail, jobs search, the tracker, profile topcard, skills, profile-views
> analytics, connections, manage-pages, notifications, newsletter subscriptions
> and the apply modal. **Not one of them is a page where a "Saved posts" link
> would live.** There is no feed capture and no my-items capture in the corpus.

This repository has already paid for this exact mistake once: the
`job_collections` row records two zeros that "measured the instrument, not the
surface." **This would have been the third, and the only thing that stopped it
was running the control against a route I already knew was there.** A result I
set out to find is precisely when one observation is not enough.

**What would settle it offline:** a tracked capture of the feed left rail or the
profile My Items module. Neither exists, and producing one needs a live load of
a page that is already admitted -- which is a browser act, not an offline one.

---

## 2. WHY THE CLAIM READS AS SETTLED: IT SHARES A SENTENCE WITH A MEASUREMENT

Verified at all three sites by reading them, rather than relayed from section
4.1. `linkedin_server/readonly.py`, at the `/jobs-tracker/` entry:

> "The job tracker, which is where `/my-items/saved-jobs/` **now redirects** (the
> cardType query is **dropped on the way**, and that older address is no longer
> on this list because nothing builds it any more). `?stage=` selects which of
> his own lists renders. **It is a read: measured 2026-08-22** by opening three
> stages in turn and re-reading the default view afterwards, where every tab
> count was unchanged."

**One comment, two claims, one date -- and the date belongs to the other one.**

    now redirects / query dropped     UNMEASURED   about /my-items/
    it is a read, tab counts held     MEASURED     about /jobs-tracker/
                                      2026-08-22

The measurement opened `/jobs-tracker/?stage=...`. **It never opened
`/my-items/saved-jobs/`, so it cannot say what that address does.** The
DESTINATION is measured; the REDIRECT is not. A reader checking whether this
comment is evidence-backed finds a date and a method, and both belong to the
half that was not in question.

> **AN UNMEASURED CLAIM PLACED BESIDE A MEASURED ONE INHERITS ITS CREDIBILITY
> WITHOUT INHERITING ITS EVIDENCE.** The citation is real, the date is real, the
> method is real -- and none of them is about the sentence a reader is checking.

This is the same family as the ruling retracted earlier today: *a component's
own documentation explains the component, not the policy it implements.* Here it
is finer -- not a different file two hundred lines away, but **the next clause**.

**A HYPOTHESIS I HELD AND THE SOURCE REFUTED, recorded because I nearly wrote
it up.** I expected to find the claim had ACCRETED detail: `tests/test_tools.py`
says the redirect "drops its query string", which reads like a stronger claim
than the boundary file would make. **It is not.** `readonly.py` already says
"the cardType query is dropped on the way". The test comment restates it; it
does not grow it. **The interesting finding was one line further down, and I
would have missed it had I written up the first one.**

---

## 3. THE CLAIM IS LOAD-BEARING FOR NOTHING SHIPPED

The reason this matters less than it looks: **both things the redirect claim
appears to support are justified without it.**

**The tracker's ADMISSION** rests on "it is a read, measured 2026-08-22" and on
`?stage=` being the only address a client-side radio tab has. Neither clause
needs the redirect to be true.

**The old pattern's REMOVAL** rests on a different argument entirely, and
`tests/test_readonly.py` states it at the must-stay-refused entry for
`/my-items/saved-jobs/?cardType=SAVED`:

> "Nothing builds it any more, so it is off the list -- **a pattern kept for a
> url the server never opens is a door with nobody watching it.**"

That is a sound reason and it is about THIS REPOSITORY, not about LinkedIn. It
holds whether or not the address redirects. And
`test_that_list_is_the_urls_the_server_really_builds` proves only that
`server.py` no longer BUILDS the retired url -- **a fact about our source, not
about their behaviour**, which is exactly the dead-code-hygiene shape section
4.1 identified.

**SO NOTHING IN THE SHIPPED BOUNDARY NEEDS REPAIR.** The only artifact the
redirect claim was ever load-bearing for is the census COST ESTIMATE for `C36`
and `C37` -- *"one allowlist entry away"* -- and that is precisely where section
4.1 already found it wrong and corrected it upward.

---

## 4. WHAT THIS CHANGES, WHICH IS LESS THAN IT SOUNDS

    C36  Save a post to Saved Items      GAP -> GAP
    C37  Unsave a saved post             GAP -> GAP
    rows banked                          ZERO
    patterns moved                       ZERO

**The chicken-and-egg in section 4.1 stands, verified rather than relayed:**
`scripts/_probe_landed_address_sweep.py` gates on `readonly.is_read_url(url)`
before `BROWSER.goto()`, so the landing cannot be measured until the address is
admitted, and admitting first is Amendment A10's *boundary opened with nothing
behind it*. Every other tracked `/my-items/` reference is an offline
`assert_read_url()` refusal, a `blast_radius.py` probe url, or prose -- counted
directly, not taken from section 4.1's word.

**And `C37` is doubly gated, which the cost note says and is worth keeping in
view:** it is a WRITE behind an unadmitted address, so the address question and
the write sanction are two prices, not one. Today's proof that `unsave_job`
fires and reverses on the JOBS surface says nothing about the posts surface --
different address, different tool, no shared code path.

**The honest next step is unchanged from section 4.1** -- admit narrowly and
anchored, run the landed-address check IN THE SAME WAVE, name the landed address
or revert before the wave closes. **What this pass adds is that one route which
looked cheaper than that is now measured and closed**, and that anyone re-reading
the `readonly.py` comment should not mistake its date for evidence of its first
clause.
