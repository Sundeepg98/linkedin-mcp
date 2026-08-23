# The key that shipped beside its own output -- `oldsha10` + `oldsha02`

**The finding, restated so it is not softened.** The four follow fixtures are CLEAN: 86/86 forbidden
strings absent, 0 of 181 url spellings present, 0 real follower counts. The sanitisation worked.
`scripts/_build_follow_fixtures.py` then shipped the complete before->after mapping in the same
tracked, pushed file -- twenty real Pages with their real numeric ids, thirteen slugs, his name and
vanity, a real title, requisition id, ATS account and job id, his city in two spellings, an office
campus. **A clean fixture plus its key is not a sanitised fixture; it is a sanitised fixture and the
instructions for reversing it.** The same commit had already learned this and not applied it to
itself: it gitignored `_fixture_sanitisation_check.txt` *because that file enumerates what it
removed*.

**Fixed by splitting the pair, not by deleting a table.** Only the INVENTED side stays tracked -- it
is the literal content of the fixtures, readable by anyone who opens one. The real side is in
`_audit/_sanitisation_key.json`, gitignored, paired by index. This takes away nothing: both scripts
already needed untracked input (the raw captures). Absent the key they **refuse, loudly** -- a
sanitiser that cannot name what it removes would report every file clean. Also fixed: both probe
scripts (a real company id and name as constants; his vanity slug where `/in/me/` already means
that), and the real `/company/<id>` in `notifications.html` whose NAME was pseudonymised at `oldsha08`
while the id was left.

**The guard, and why it could not be the obvious one.** The obvious guard is a list of the real
strings swept over every tracked file -- and **writing it down is the leak**. The cold review's own
sweep had to embed the mapping to hunt it, which is why that script lives outside the repo. So
`tests/test_no_committed_identity.py` hunts what needs no real value: **the SHAPE of a key** (a table
pairing fixture content with something absent from every fixture is a pre-image by construction) and
the member-id shape repo-wide. `scripts/sweep_tracked_for_identity.py` is the exact-value half:
tracked, wordlist permanently untracked, every value expanded through `leakwalk.url_spellings`
because a list of literals only catches the spelling somebody typed, and findings printed with the
line **redacted to its shape** -- a sweep that echoes its wordlist into a CI log has published the
key somewhere new.

**It immediately found a second key the review could not have.** `scripts/_build_job_fixtures.py` --
a different sanitisation script from an earlier wave -- shipped `SUBS` and `OTHER_EMPLOYERS`, thirteen
real->invented pairs. The cold review swept every tracked file and did not flag it, and that is not
carelessness: **its wordlist was built from the Manage-Pages capture, and a value list cannot name a
value nobody has seen.** The shape guard needs to know nothing about what it is looking for. Same
split applied; its capture filenames spelled the real job id, so they are globbed now.

**Then the value sweep found 37 more, now 0**: the real job id in seven tracked files including a
comment in `readonly.py` and a docstring in `server.py`; his given name and vanity slug as literal
test data in five test modules. Two false positives (a very common word; the GitHub account that owns
this repo and must appear in its own remote url) are exempted **in the untracked key**, because an
exemption list has to name the value it exempts.

**Three things I got wrong on the way, recorded because each is the same class as the bug.** (1) My
first draft of the shared spelling-expander docstring **quoted the real job title in both spellings**,
to explain why real titles reach tracked files -- caught only by re-running the sweep against my own
change. A guard is not exempt from what it guards. (2) My exact-match scrub of his city took three
passes: each replacement left the assertion that carried the same string. (3) Both build scripts had a
bare module-level `main()`, and `main()` WRITES `tests/fixtures/` -- importing either one to read a
single table rebuilt committed fixtures as a side effect. It fired once during extraction and
regenerated them byte-identically, which was luck. Both guarded now.

**Needs a ruling rather than my assumption.** `linkedin_server/readonly.py` and
`tests/test_readonly.py` are **no longer zero-line diffs** against `oldsha14`, because the real job id
was in both. The change is literal-only, and that is proven rather than asserted: `_ALLOWED_URL_PATTERNS`,
`_FORBIDDEN_URL_SUBSTRINGS`, `_MUTATION_CALL_PATTERNS` and `JS_MUTATION_TOKENS` are byte-identical by
AST comparison, the function set is identical and every function body is identical.
`test_launch_boundary.py` is still zero-line.

**Not fixed, deliberately.** The denylists in `_build_follow_fixtures.py` and
`test_sdui_surfaces_fixture.py` still name real strings. A denylist must name what it denies; hashing
buys obscurity, not secrecy, for dictionary words already in this repo's history. The cold review
scored them the same way. **Operator's call.** Also unfixed: his Windows username in workspace paths
in `README.md`, `pyproject.toml`, `ci.yml` and `test_path_hygiene.py` -- structural, not removable
from here.

**Measured.** Suite 1092 -> **1188 passed, 2 skipped**. Sweep **0 hits across 87 tracked files**, 191
spellings, 10 classes. Reviewer's independent sweep: 6 files -> **2**, both denylists. CI `32632258303`
**success** at `oldsha10`.

**Final.** `oldsha23`: suite **1190 passed, 0 skipped**; CI run **32633922350 success** on all three cells.
The run before it was red with `failed 0 | errors 0` -- two SKIPS, both mine, refused by
`scripts/ci_full_run_check.py`. A local run cannot see that: pytest reports a skip as a pass.
The guard now excludes its two shape-defining modules by NAME when the parametrised set is built,
which is what they always were -- out of scope, not unexaminable.

**Shown failing on the real artefact, not a synthetic.** Run against the pre-scrub files from
history, the key-shape detector fires on `_build_follow_fixtures.py` (`FOLLOWED_PAGES` 21 paired
rows, `SLUGS` 4, `OPERATOR` 4, `POSTING` 7, `OTHER_EMPLOYERS` 3) and on `_build_job_fixtures.py`
(`SUBS` 3, `OTHER_EMPLOYERS` 3); both are clean after. A planted member id in `linkedin_server/paths.py`
fails the repo-wide sweep.

---

## The landmine underneath it (`oldsha15`)

`tests/test_scripts_are_import_safe.py`: **importing a script must not DO anything.** Both build
scripts ended in a bare module-scope `main()`, and `main()` writes `tests/fixtures/` -- so importing
either one to read a table rebuilt committed fixtures. Guarding the two was the fix; this is the rule.
Static on purpose: the dynamic version would have to EXECUTE the thing it is proving safe. Refused --
a bare call to a plain NAME, any statement containing a write-shaped call (assignment or not), `open()`
in a writing mode. Accepted -- attribute calls (`sys.path.insert` writes nothing), reads, and anything
under `if __name__ == "__main__"`. **Shown failing at `oldsha22`** on both real files, clean today.

**The instrument caught me twice, and that is the finding.** The first draft of the spelling expander
quoted the real job title in both spellings inside the docstring explaining why real job titles reach
tracked files. Then, writing the paragraph recording THAT, I named the real city in two of its three
forms. Both caught by re-running the sweep against my own change, neither by reading it back. **A guard
is not exempt from what it guards** -- now stated in the identity guard's own docstring.

**The pass count, because it is the whole argument for shape over literals:** the exact-value scrub of
ONE city took **three passes**. Each replaced the spelling it could see and reported clean; the next
found another -- the full form, the bare city, then the bare city inside an assertion written to match
the input the previous pass had just changed.

**Final: 1211 passed, 0 skipped.** Sweep 0 hits across 88 swept files.

### Correction: the import-safety rule went red twice before it went green

`oldsha15` and `oldsha12` both failed **all three cells** -- and **zero of those failures were about the
rule**. `test_it_fires_on_this_repos_own_history` ran `git show oldsha22:<path>`, which passes here
because a full clone has the object. **CI checks out SHALLOW**: `fatal: invalid object name`,
`2 failed, 1211 passed`. A test that proves something about history may not DEPEND on the history
being present -- a shallow clone is the normal case, not the exception. The evidence is now frozen in
the test with its sha and a one-line re-verification command.

**Then the fix was wrong too, and a shallow clone caught it before CI did.** The first frozen tails
were verbatim FRAGMENTS beginning mid-indentation, so `ast.parse` raised `IndentationError` -- the two
tests failed for a reason unrelated to the rule they exercise. Each entry is now the module-level shape
with bodies elided and the load-bearing `main()` line verbatim, plus a test asserting the frozen
evidence parses at all. Verified in a `--depth 1` clone with the history genuinely absent:
**1211 passed**.

**The lesson I keep re-learning this wave, now three times over:** green locally is not green. Local
has history CI lacks, local counts a skip as a pass, and local had a key file CI never sees. The
repo's own gates caught the first two; a deliberate shallow-clone reproduction caught the third.

---

## A real member URN was at HEAD, and why three guards walked past it (`oldsha11`)

`tests/test_sdui_surfaces_fixture.py` carried **four real values** -- a member URN, an activity urn,
a `ugcPost` id and a per-impression tracking token -- as the inputs to its own can-it-fail control.
Its docstring said so: *"the real ids that WERE in these files before they were pseudonymised."* The
fixtures were scrubbed and the scrubbed-out values were kept in the file beside them. **A control
needs the SHAPE, not the VALUE.**

**WHY NEITHER GUARD CAUGHT IT. Three independent blindnesses, all measured, none of them the one I
first assumed.**

1. **The word boundary.** `\bACoAA[A-Za-z0-9_-]{20,}` cannot match `%3AACoAA...`: the trailing `A`
   of the percent-encoded colon is a word character, so `\b` never fires -- and percent-encoded is
   the form LinkedIn actually serves. Bare id matches, raw-colon urn matches, percent-encoded does
   not. This was the load-bearing one.
2. **I had dropped the urn prefix** from the repo-wide sweep as too noisy. True of the bare prefix,
   false once a six-digit floor is required of the id behind it.
3. **The file was excluded**, because it defines the allowlist. An exclusion is a promise that
   nothing in the file needs checking, and the real values were inside the excluded file.

The key-shape detector was never going to see it, and that is a **class**: it hunts a PAIRING, and a
lone literal has no partner column. Keys were covered and known values were covered; **an unknown
real value arriving alone was covered by neither.** Nothing is skipped now -- files that deliberately
carry a violation are **pinned by count**, so a new real id changes the count and goes red, and every
pin is exercised.

**Closed loop:** run against HEAD, the merged guard reports exactly the three values it previously
walked past, redacted -- `member token AC..uY <39 chars>`, two `urn id`. After the scrub: only the
one declared plant.

**Resolved rather than scrubbed:** the phone-shaped value a sibling sweep left UNRESOLVED is **not a
phone**. It sits inside `id="ab7dc03f-6282-46a6-a3b9-XXXXXXXXXXe2"` -- a ten-digit run inside a
UUID's tail. Encoded as a UUID-context rule, not an allowlisted value.

**The freeze is now an invariant, not a line count** (operator ruling): AST digests of the four
boundary structures and every function body of `readonly.py`, pinned against `oldsha14`, **frozen not
fetched** because CI checks out shallow. A comment or an identity swap cannot move it; deleting
`/messaging`, widening the allowlist to the whole domain, or removing the click detector all do --
shown failing on those three.

**Stated at the top of the merged guard, because it is the gap most likely to be misread:** NONE OF
THESE CHECKS DETECTS A PERSONAL NAME. NAMES HAVE NO SHAPE. Green means no third-party IDENTIFIERS of
these shapes. Every real name in this family's sweep was found by a human reading fields.

**Accepted residuals, operator-ratified:** the denylists keep their real strings (a denylist must
name what it denies; these are unpaired lone tokens, and a PAIRING is what makes a key), and his
username in workspace paths is structural -- the real fix would be configurable paths, which is a
refactor, not a privacy action.

**Measured:** 1211 -> **1244 passed, 0 skipped**; **1240 passed in a `--depth 1` clone** before
pushing. Sweep **0 hits across 89 files**.

**Instrument law, from this wave's most repeated failure:** *a check that skips has not run, and a
suite that counts skips as passes cannot tell you what it verified.* Local green failed three ways
here -- a skip counted as a pass, history CI lacks, and a gitignored file CI never sees.
