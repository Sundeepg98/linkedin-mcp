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
