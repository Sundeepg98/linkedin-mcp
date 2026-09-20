# RULING: a duplicate census row is MARKED, never DELETED

**Ruled 2026-09-20 by the campaign lead.** Standing, and it binds every future
cross-slice re-file. It was blocking `N 149`/`N 160` and the queued
`OWNED-BY-A-SIBLING-SLICE` re-file, both of which asked for a deletion.

## The ruling

When two census rows describe one capability, the duplicate **stays in the file**
and is marked as a duplicate, naming the row it duplicates. It is not removed,
and its id is never reused.

## Why, and the evidence

**1. It is the only precedent this tree has.** Measured today: **34 cells across
the four slices already carry duplicate/same-as/twin language**, and no census row
has ever been deleted. A wave that deletes one would be the first, which is a
poor way to settle a convention.

**2. A deleted row is unfindable, and that is the whole cost.** The census exists
so that a future reader can ask "was this capability considered?" and get an
answer. A marked duplicate answers YES and points at where the answer lives. A
deleted row answers nothing -- it is indistinguishable from a capability nobody
ever thought of, which is exactly the distinction this campaign has spent weeks
trying to recover. You can grep a corpus for what it refuses; you cannot grep it
for what somebody removed.

**3. Deletion moves the denominator silently.** Row counts are load-bearing here
and several published numbers are derived from them. A marked duplicate can be
subtracted by any consumer that wants a de-duplicated count, and the subtraction
is then visible and checkable. A deleted row has already done the subtraction,
invisibly, at a time nobody recorded.

**4. A sibling wave measured the specific case and found no destination.**
`N 150`/`N 151` have no twin in messaging, jobs, profile or the inventory under
34 spellings. So the re-file that wanted to delete them was not pointing at a
wrong destination -- there is none. Under this ruling that re-file cannot be
executed as written, and leaving it queued with the reasoning recorded is the
correct outcome rather than a failure to act.

## What a consumer should do

Anything deriving a capability count subtracts marked duplicates itself and says
that it did. The census reports ROWS; de-duplication is the consumer's job and it
must be shown, not assumed.

## What would overturn this

A measured case where marking produces a wrong answer that deletion would have
prevented. None has been offered. Deletion's only advantage so far is a tidier
count, and a tidier count is not worth an unfindable capability.
