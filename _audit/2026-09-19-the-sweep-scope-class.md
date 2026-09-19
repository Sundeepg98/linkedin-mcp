# The sweep-scope class: three incidents, two classes, and the narrowing I refuse

Wave `sweep-scope`, 2026-09-19. Hard stop 18:10 IST; this is written at 18:05.

## The question

Three incidents in one day looked like one collision class -- "a sweep scoped to
whatever is lying at the repo root inherits every tool's choice of where to put
things." The task was to establish whether a class-level fix exists and is safe,
or to report honestly that the per-instance fixes are correct.

## What the scope actually is

`tests/test_no_committed_credential.py::committable_files` -- reused by
`tests/test_no_committed_identity.py::sweepable` -- is:

```
tracked  UNION  untracked-not-ignored     (git ls-files  +  git ls-files --others --exclude-standard)
```

That is not "whatever is lying here." It is **exactly the set a `git add -A`
would pick up**, which is exactly the guard's subject: what we are about to
commit. The docstring already says so, and it was widened to this on 2026-09-01
by a real leak -- an untracked file carrying a real activity id sat through a
full green suite and became visible only in the commit that published it.

Measured on this tree, 17:58 IST:

| quantity | count |
|---|---|
| tracked | 482 |
| untracked-not-ignored | 0 |
| union (the sweep's subject) | 482 |
| swept after the extension filter | 482 |
| swept files with a NUL byte in the first 8 KB | **0** |
| swept files over 1 MB | **0** |
| swept files with no extension at all | 2 |

Script: `scratchpad/census.py` (disposable; the numbers are the deliverable).

## The verdict: TWO classes, not one, and not three

### Class B -- derived artifact lands at the repo root (incidents 2 and 3)

`.pw-browsers/` and the CI working files are the **same** class, and c47a070's
own commit message already wrote the principle out:

> "the same argument for why ignoring is the repair rather than declaring: the
> ids are DERIVED from the test files, and those are swept directly. This
> artifact is a second copy of text the guard already reads at its source, so
> nothing stops being checked."

That is the class rule, and it is already correct. **An ignore entry that
shields the sweep is admissible if and only if the ignored content is derived
from text the guard already sweeps at its source** -- because then ignoring it
removes zero coverage. Both repairs satisfy it. Neither is a narrowing of the
guard's subject; both are removals of a *second copy*.

The class-level fix available here is therefore **not** a scope change. It is
promoting that sentence from a commit message to an admission test that every
future `.gitignore` entry must pass. Cost of not having it: the argument gets
re-derived per instance, which is what happened twice today.

### Class A -- matcher precision (incident 1)

`_RECOVER_*.patch` is **not** the same class. A saved patch is a legitimate
member of "what we are about to commit"; the defect was that a diff marker
followed by a module path read as an address shape. The repair narrowed
`_email_ok` (local part with no letter or digit). That is a **matcher**
precision fix inside a correctly-scoped set. Nothing about where the file sat
caused it; the identical false hit would fire on a tracked patch fixture.

Filing it with 2 and 3 would have produced a scope fix for a shape bug.

## What I refuse to narrow, and why

**1. "Untracked content at the repo root is swept only if it is text and under
some size."** Refused. A size gate is a gate on the guard's *subject*. A
multi-megabyte JSON capture of a platform response is text, large, and precisely
the artifact most likely to carry a real member id -- this repo's fixture
pipeline produces exactly that shape. The size gate does not prevent a fourth
incident; it *is* the fourth incident, pre-authorised.

**2. An allowlist of what MAY be swept, replacing the denylist.** Refused, and
this is the sharper one. It inverts the default from "everything we could commit
is checked" to "only what somebody enumerated is checked." Every new file class
then starts life unchecked and stays unchecked until a human notices. That is
the 2026-09-01 incident -- the invisible untracked file -- reintroduced as
architecture rather than as an accident.

**3. Anything that could reach the `shape.census_shape` class.** Today's wave
found that function returning the operator's own name unchanged into stdout, in
a file whose heading promised no option text is printed. That file is a tracked
`.py`, pure text, well under any size bound, with no NUL byte. State the
relation: **no gate keyed on size, on byte-content, or on tracked-ness can reach
it** -- it is small, textual, and tracked on all three axes. Any narrowing
proposed in future must be checked against that triple before it lands.

## The one narrowing that IS defensible -- and why it did not land today

Incident 2 also slipped `BINARY_SUFFIXES`, because a Linux executable named
`chrome` has no suffix. That is real: **the binary test is keyed on an extension,
and incident 2 proved extensions do not decide.** The correct fix is the test git
itself uses -- sniff for a NUL byte in the first 8 KB -- which is *wider* than the
current list (it also catches the unlisted binary extension that today gets read
as text and manufactures garbage hits).

It did not land, and the reason is the measurement above: **0 of 482 swept files
carry a NUL byte and 0 exceed 1 MB.** Against this tree the content sniff is a
no-op. Per the instrument register's second law -- an instrument enters only if
it has been shown failing -- a gate that changes nothing on the live tree cannot
be admitted on live evidence alone. Its controls must be:

- **RED control:** plant a file with no extension whose first bytes contain NUL
  plus an address-shaped byte run. Assert the *extension* filter admits it (the
  incident-2 reproduction) and the *content* sniff rejects it. Shown failing
  before the fix, passing after.
- **GREEN control (the non-narrowing proof):** assert that the count of swept
  files that are text is **unchanged at 482**, and specifically that a small
  tracked `.py` carrying a name in a print path is still swept. This is the
  control that fails if the narrowing ever reaches the census class.
- **Anti-vacuity:** assert the plant was actually created and read, so the RED
  control cannot pass by finding nothing.

I am not landing a guard edit on the most dangerous file in the repo in the five
minutes before a hard stop. The specification above is the handoff; it is a
closed-form slice and needs none of this wave's tacit context.

## Answer to the question asked

A class exists, and it covers **two** of the three incidents, not three. Its fix
is **not** a scope narrowing -- the scope is already exactly right, and every
scope narrowing weighed today either fails to prevent a fourth instance or
recreates a leak this repo has already had. The class fix is an *admission rule*
for ignore entries (derived-from-swept-source), which both existing repairs
already satisfy, plus one extension-to-content correction to the binary test
that is genuinely pending and genuinely specified.

The per-instance fixes are correct. Incident 1 is a different class from 2 and 3
and was fixed in the right layer.

Attribution in this commit: 0.
