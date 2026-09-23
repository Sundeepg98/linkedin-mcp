claude-opus-5-5[1m]

# Lane L4 -- WRITES: classify the write-direction GAP rows, build the reversible first round to ready-to-fire

Written as the lane runs. Worktree branch `worktree-agent-a6aa0720780262d33`, cut from `master` at `b0d3ab8`.
Nothing in this lane touched LinkedIn: no browser was attached, no grant was issued, and
`writes_enabled()` stayed False in every process this lane started. Fixture tests drive a local
headless Chromium over static HTML with no network, which is how this repository has always run
its fixture tests.

## 0. Status log

- 17:47 -- lane opened; read `linkedin_server/writes.py` end to end, `_audit/RULINGS.md`,
  `_audit/2026-09-21-the-write-ceiling.md`, `_audit/2026-09-20-the-write-partition.md`, the
  coercion-leak record, the follow-control records and the census cells of every row below.
- 18:40 -- denominator derived (section 1); classification rule fixed (section 2); R1 buildability
  measured per row (section 3). One R1 row is buildable offline; that is the build.

## 1. THE DENOMINATOR, DERIVED

The brief said 151. Derived with the shipped instruments -- `count_census_states` for the row
filter and the state, `enumerate_gap_rows.ADMIN_ONLY` for the admin table, and
`reader_closable_blockers.direction_of` for the direction, the same loop `census_completion.walk()`
replicates -- at `b0d3ab8`:

    still-GAP rows, all four slices     274
      by direction   W 151   R 64   R+W 3   unknown 56   (jobs.md has no direction column)

    W-direction GAP                      151   AGREES WITH THE BRIEF
      profile.md                          37
      messaging-and-content.md            65
      network.md                          49

The write-ceiling document counted 152 on 2026-09-21 (37 / 66 / 49). Measured by re-running the
same walk over the census at `d92aa30`, the write-ceiling's own commit, and diffing the key sets:
exactly ONE row has left since, `M C85`, whose direction cell was repaired `W` -> `R+W` under
`COMPOUND-ROW-SPLITS-ONLY-ON-STATE`. It is one of the three `R+W` above, and it is a row this lane
was told not to touch. (A first draft of this paragraph printed 64 / 50 for the last two slices,
counted by eye off a list; the script says 65 / 49 and the diff says why. Corrected before
commit.)

## 2. THE CLASSIFICATION RULE, AND ITS TWO SOURCES

**R1 -- the sanctioned reversible first-round class.** The class is defined in two places, both
quoted rather than paraphrased by the table:

* `linkedin_server/writes.py`, the comment above `SANCTIONED_WRITES`: *"Three, all chosen for
  being REVERSIBLE."*
* `_audit/_census/network.md` section 6, quoting the operator's skill file: *"the first write
  round ships only reversible actions (save/unsave, follow, Open To Work) behind an
  off-by-default flag, why apply, connect and InMail were deliberately cut"*.

So a row is R1 when its act is one of those verbs as LinkedIn names them: save / unsave (a
bookmark), follow / unfollow, or the Open To Work signal itself.

**R2 -- deliberately cut by the operator:** apply, connect (a connection invitation, its note, its
re-send), and a message or InMail send (anything that transmits his words, an attachment or a
structured reply to another member through messaging). Same two sources, plus the writes.py
sentence *"apply, connect and message/InMail were removed from the round"*.

**R3 -- other or undecided.** Everything else, INCLUDING rows adjacent to R1 whose membership is a
reading the operator has not made. Those are the ones worth naming, because each is a place where
widening R1 would be this lane deciding for him:

* newsletter SUBSCRIBE / UNSUBSCRIBE (`N 55`, `N 56`, `M C80`) -- LinkedIn's verb is not "follow",
  and a subscription carries an e-mail channel a follow does not (the census's own `N 58` is the
  row for leaving that channel while staying subscribed);
* the job-seeking signals beside Open To Work -- minimum pay (`P I13`), "interested in working for
  a company" (`P I14`, `P I15`), "how you found your job" (`P I16`), Open to volunteering (`P D24`)
  and the #Hiring family (`P B7`, `P J1`-`J3`). The first-round sanction names the Open To Work
  SIGNAL; these are neighbours of it, not it;
* invitations that are not connection requests -- inviting others to follow a Page, attend an
  event or review a service (`N 7`, `N 8`, `N 186`, `P H9`, `N A4`, `N A9`, `N A10`). They reach
  other people, and the cut names "connect", which is a different act.

The act of every row is written into the table from a CLOSED vocabulary, and the checker holds the
act -> class map, so a row cannot be R1 with an R3 act or the reverse without going red.

## 3. THE SPLIT, AND WHAT STANDS IN FRONT OF EACH R1 ROW

`_audit/_census/write-classes.tsv`, checked by `scripts/check_write_classes.py` (register 61):

    R1  the reversible first round     11
    R2  cut by the operator            23    connect 4, message or InMail send 19, apply 0
    R3  other or undecided            117
                                      ---
                                      151

No write-direction GAP row is an APPLY: the apply capabilities live in `jobs.md`, which has no
direction column, so none of them is in this population at all.

R1 is 11 rows, under the brief's cap of 15, so every one was taken to the build question -- in the
census's own order (slice order J, P, M, N from `count_census_states.SLICES`, then file order).
**Ten of the eleven cannot be built to ready-to-fire in a lane that may not touch LinkedIn,
`readonly.py` or `press.py`**, and each is queued with the one thing that lifts it:

| row | capability | act | disposition | what stands between it and ready-to-fire | whose |
|---|---|---|---|---|---|
| `M C36` | Save a post or article to Saved Items | save | `queued:SAVED-POSTS-SURFACE` | The Save control lives in the post's overflow menu, never opened; the only surface that could VERIFY a save, `/my-items/saved-posts/`, is absent from the read allowlist and its landing is unmeasured (the cell's own cost correction) | a disclosing press (L2 / the live lane) AND an admission plus a landed-address check (L1) |
| `M C37` | Unsave a saved post | unsave | `queued:SAVED-POSTS-SURFACE` | the same two | the same |
| `M C79` | Follow or unfollow member articles | follow-or-unfollow | `queued:ARTICLE-SURFACE` | no article address is on the read allowlist, and no article page has ever been captured, so its follow control is unmeasured | L1, then one capture |
| `N 37` | Unfollow a person directly from a feed post | unfollow | `queued:FEED-ITEM-OVERFLOW-MENU` | the permalink is admitted and two writes already act there; the overflow menu that carries the unfollow item has never been opened, so the item's label is unmeasured | a disclosing press (L2 / the live lane) |
| `N 40` | Re-follow a person you previously unfollowed | follow | `queued:PEOPLE-FOLLOW-LISTS` | its only surface, `/mypreferences/d/unfollowed`, carries the `/unfollow` forbidden substring AND is a settings-family page; `N 39`, the read of that same page, is EXCLUDED-RULED with the reopener *"the operator naming this page"*. A DECIDE item, not a build | the operator |
| `N 41` | Follow a member from one of their articles | follow | `queued:ARTICLE-SURFACE` | as `M C79` | L1, then one capture |
| `N 42` | Unfollow the articles of a member you are not connected to | unfollow | `queued:ARTICLE-SURFACE` | as `M C79` | L1, then one capture |
| `N 47` | Follow an organization's Page from the Page itself | follow | `queued:COMPANY-PAGE-FOLLOW-CONTROL` at the classification commit; **THE BUILD -- section 4** | the one R1 row whose surface is admitted AND whose control is measured in a capture this repository already holds | this lane |
| `N 49` | Follow a skills Page | follow | `queued:SKILL-PAGE-SURFACE` | no skills-Page address is known to this repository or admitted, and nothing has captured one | L1, then one capture |
| `N 59` | Follow a hashtag | follow | `queued:HASHTAG-EXISTENCE` | the surface may be RETIRED: four settle-controlled feed loads on 2026-09-19 drew zero hashtag anchors (`_audit/2026-09-19-hashtag-surface-live-evidence.md`), and no hashtag address is admitted | existence first, then L1 |
| `N 60` | Unfollow a hashtag | unfollow | `queued:HASHTAG-EXISTENCE` | as `N 59` | as `N 59` |

The queue tokens are the lane's own names for the binding constraint, not the blocker map's; where
they differ (`N 47` is mapped to `COMPANY-PAGE-SURFACE`, whose address half was paid on 2026-09-20)
the table says what binds TODAY.
