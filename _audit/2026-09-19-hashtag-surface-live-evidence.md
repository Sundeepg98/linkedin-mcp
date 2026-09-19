# The hashtag surface, read live -- citable evidence for conflicts A and C

Written 2026-09-19 by the small-measures wave. **This document exists because
its evidence was previously only in `_audit/_scratch/`, which is gitignored
and therefore not a citable source.** `skew-gate` is adjudicating two
conflicts that rest on these readings; everything below is in tracked history
with file and line.

**SCOPE, STATED FIRST SO IT TRAVELS WITH THE NUMBERS.** Every reading here is
of `https://www.linkedin.com/feed/`. Nothing here is a reading of a settings
surface, of a followed-hashtags list, or of `network.md` rows 59-61. What this
document can support is bounded accordingly, and s4 states the bound rather
than leaving a reader to infer it.

## 1. WHAT WAS READ, AND WITH WHAT CONTROL

Four loads across two independent instruments, both attaching over CDP to the
operator's real signed-in Chrome (153.0.8010.48, port 9224). Nothing was
pressed, typed, scrolled or submitted on the feed.

| instrument | when | control | result |
|---|---|---|---|
| `scripts/_probe_unmeasured_surfaces_live.py` stage a | 08:36 | census settle: 263 controls read against a ~277 baseline, floor 138 -- **CONSISTENT** | hashtag needles all 0 in main text |
| `scripts/_probe_small_measures_live.py` | 08:49 | `PAGE CONTROL: PASS` (`Feed`, `Start a post`) | 0 anchors |
| `scripts/_probe_small_measures_followup.py` | 09:07 | `PAGE CONTROL: PASS` | 0 anchors, partition sums PASS |
| `scripts/_probe_small_measures_followup.py` | 09:20 | `PAGE CONTROL: PASS` | 0 anchors, partition sums PASS |

**A ZERO FROM AN UNRENDERED PAGE AND A ZERO FROM A PAGE WITH NO SUCH CONTROL
ARE THE SAME ZERO.** Every reading above is gated by a control that had to
fire first; none is offered as a reading without one.

## 2. THE STABLE RESULT -- what four loads agree on

    a[href*="hashtag"]           0    all four loads
    a[href*="/feed/hashtag/"]    0    all four loads
    "/feed/hashtag/" in html     0    all four loads
    "hashtag" in main text       0    all four loads
    "#hiring" in main text       0
    "Followed hashtags"          0

**No member-clickable hashtag surface renders on this account's feed.**

## 3. THE UNSTABLE NUMBER, AND MY OWN INSTRUMENT'S FAILURE

The raw-HTML occurrence count of the word moved across loads: **20, 15, 33,
10.** The feed is not a settled surface and each count is a reading with a
timestamp.

**MY FIRST CLASSIFIER ACCOUNTED FOR 0 OF 15.** It guessed seven shape classes
-- href value, `/feed/hashtag/` path, attribute name, JSON key, JSON string
value, class token, urn -- and every one read zero. **Seven guessed buckets
that all read zero look exactly like absence and were really a classifier that
did not fit.** That is a defect in the instrument, not a finding about
LinkedIn, and it was recorded as such before it was repaired.

The replacement is a PARTITION rather than a bucket list -- script content vs
everywhere else, exhaustive by construction, with its sum asserted and
printed:

    23 in <script> + 10 elsewhere = 33    PARTITION SUMS: PASS
     0 in <script> + 10 elsewhere = 10    PARTITION SUMS: PASS

A partition can fail its own arithmetic. A bucket list cannot, which is why
its zeros were uninterpretable.

## 4. WHAT THIS EVIDENCE DOES **NOT** SUPPORT

Stated explicitly, because a downstream verdict will otherwise take s2 at face
value:

1. **It does not establish where the raw-HTML occurrences live.** The
   partition places them inside or outside `<script>` content and no finer.
   The seven-class attempt failed entirely. Anyone needing to know what those
   strings ARE must measure it; this document cannot tell them.
2. **It does not rule on `network.md` rows 59-61** (follow a hashtag, unfollow
   a hashtag, view your followed hashtags). A feed that surfaces no hashtag
   anchors is consistent BOTH with the member hashtag-follow surface having
   been retired AND with its existing somewhere the feed does not link to. The
   evidence is genuinely non-dispositive for those rows, and `network.md:292`
   records the standing reason they were deliberately kept mapped: *removing
   capabilities on an inference is the same undercount this pass exists to
   fix.* That reasoning is untouched by anything here.
3. **It is not a reading of any settings surface.** See s6.

## 5. CONFLICT A -- `N 194` is `SEARCH-RESULTS-SURFACE`

`_audit/2026-09-06-corpus-sweep-blocker-evidence.md` s3 finding A asks whether
`N 194` ("Find hiring managers through the #Hiring hashtag in search") belongs
to `HASHTAG-EXISTENCE` or `SEARCH-RESULTS-SURFACE`.

**This wave adds a second, independent line of support for
`SEARCH-RESULTS-SURFACE`,** beyond the ledger arithmetic that finding A
already cites:

* **The row's own text names its blocker.** `_audit/_census/network.md:545`:
  *"Blocker: no people search."* Not hashtags.
* **And the hashtag half is moot on this account anyway.** s2 finds no
  hashtag surface on the feed. So even granting the hashtag reading, the row
  would still be blocked by the absence of people search -- the people-search
  blocker is load-bearing whichever way the hashtag question falls.

**A blocker that still blocks when the contested half is removed is the
row's real blocker.** No state change: `N 194` is GAP either way, and this is
an assignment question, not coverage.

## 6. CONFLICT C -- `M C52` is `FEED-PREFERENCES`, and I withdraw my own state

Finding C asks whether `M C52` is `HASHTAG-EXISTENCE` (from the ledger's
ambiguous bare `C 52`) or `FEED-PREFERENCES` (from
`_audit/2026-09-05-settings-tail.md:224`, which spells the id fully
qualified).

**IT IS `FEED-PREFERENCES`, AND MY OWN HASHTAG EVIDENCE ARGUES AGAINST THE
ASSIGNMENT I APPEARED TO SUPPORT.**

* `_audit/2026-09-19-settings-tail-addresses.md:108` measured the real
  address: **`/mypreferences/d/unfollowed`**, refused at the
  FORBIDDEN-SUBSTRING gate by `/unfollow` (`linkedin_server/readonly.py:1096`).
  An allowlist edit cannot reach it.
* `_audit/2026-09-05-settings-tail.md:224` names `M C52` fully qualified under
  `FEED-PREFERENCES`, with no bare-id ambiguity to resolve.
* **The capability is therefore NOT ABSENT. It exists, at a known address, and
  is refused.** That is EXCLUDED-RULED, not MEASURED-ABSENT.
* **My hashtag reading does not support `HASHTAG-EXISTENCE` for this row -- it
  undermines it**, because it finds no hashtag surface for the row to have
  been about.

**I MOVED THIS ROW TO MEASURED-ABSENT IN `a402c35` AND THAT STATE IS
WITHDRAWN.** The row now reads EXCLUDED-RULED.

**How the error happened, because it is the third instance of one disease in
this wave.** The row's hashtag wording was CORRECTED OUT on 2026-09-03 -- its
source article returns HTTP 404 and two help-index queries find no
hashtag-following article -- and the row now reads *manage your LinkedIn feed
preferences*. I measured hashtags on the feed, which is the surface the row
USED to name, and labelled the row on that reading.

The same shape produced the other two:

| row | needle taken from | what the page used |
|---|---|---|
| `P D25` | help article `a540837`, "Add profile section" | three links reading "Add section" |
| `M C52` | the row's pre-2026-09-03 hashtag wording | a feed-preferences settings address |
| `J 25/29/30` | (the one that held) section 6's own control, re-fired live | control reproduced 1/1/0 |

> **A MEASUREMENT AIMED BY A ROW'S STALE WORDING MEASURES THE ROW'S PAST.**
> The census records when a row was corrected; the correction note is exactly
> the thing that tells you your needle may be out of date, and in both failures
> it was sitting in the cell I was reading.

The one that held is the one whose needle came from a CONTROL that had to fire
on the page, not from prose describing the page.

## 7. PROVENANCE

Raw captures are untracked, under `_audit/_scratch/`:
`_probe-unmeasured-surfaces-live.txt`, `_probe-small-measures-live.txt`,
`_probe-small-measures-followup-v2.txt`, and the wave record
`_progress-small-measures.md`. **Cite this document, not those paths.**

Instruments, each shown failing before admission:
`scripts/_probe_small_measures_live.py`,
`scripts/_probe_small_measures_followup.py`,
`scripts/_probe_add_section_menu.py`.
