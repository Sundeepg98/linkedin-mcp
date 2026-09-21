# The output-sink guard misses a landed URL that reaches stdout

**Found by a survey child (`landing-evidence`), VERIFIED here by tracing the
data path rather than by reading the claim.** Nothing was fixed. The owner
question is in section 4 and it is a design decision, not a bug fix.

## 1. The claim, and what verifying it changed

The child reported that `scripts/_probe_file_inputs_live.py` prints
`out.get('landed')` and is not among `KNOWN_TAINTED_OUTPUT`'s declared sites.
Both halves check out, and the second is the interesting one:

    grep -c "_probe_file_inputs_live" tests/test_navigation_is_never_derived.py
    0

The file is **tracked** and **undeclared**, and the suite is green. So this is
not a missing declaration — **the guard does not detect the site at all.** A
declaration would have changed nothing.

## 2. The chain, traced end to end

Every hop measured in the file, not inferred:

    landed = await BROWSER.goto(page, url)        # navigation result: TAINTED
    return {"landed": landed, ...}                # -> into a dict
    ...
    lines.append(f"    landed: {out.get('landed')}")   # -> read back, into a list
    return "\n".join(lines)                       # -> joined to one string
    ...
    print(reports[-1])                            # -> REACHES STDOUT

## 3. Why the guard cannot see it — two independent reasons

`output_violations` parses for `print`/logging calls and asks
`_is_tainted_expr` of each argument, against names `_tainted_names` bound to a
navigation result.

- **`lines.append(...)` is not a sink.** The interpolation happens at a list
  append; only the much later `print` is a sink, and by then the argument is
  `reports[-1]` — an ordinary string element.
- **Taint does not survive a container.** The value crosses a dict literal, a
  `.get()` call, an f-string, a `join` and a second list. Nothing carries the
  mark across those hops, so the expression the sink actually receives is
  untainted by construction.

**THE DOCSTRING NAMES ITS GAPS HONESTLY AND THIS IS NOT ONE OF THEM.** It
declares one exclusion — a response BODY is not tainted, deliberately, because
tainting it would flag `len(payload)` and every count taken off it. The
container gap is a different thing and is unnamed, so a reader who trusts the
"WHAT THIS DOES NOT COVER" section is told less than the whole truth.

## 4. Why nothing was fixed here, and who should decide

**The obvious repairs are the ones the docstring already argues against.**
Adding `list.append` as a sink, or propagating taint through dicts, `.get()`
and joins, widens the rule until, in its own words, *"a rule whose true
positives arrive buried in false ones gets declared into uselessness."* That is
a judgement about the guard's design, not a defect to patch, and it belongs to
whoever owns the landed-URL boundary — `tests/test_navigation_is_never_derived.py`
is currently unowned by any live wave, but the DOMAIN is the `scrub-the-landing`
wave's, which is building `linkedin_server/landing.py` for exactly this class.

Deliberately not done, each for a stated reason:

- **No declaration added.** The guard does not detect the site, so a
  `KNOWN_TAINTED_OUTPUT` entry would be inert and would read as coverage.
- **No edit to the guard.** See above — it is a design call.
- **No edit to the probe.** It is a hand-run diagnostic, and changing what a
  probe prints while a wave fires probes against live pages invites exactly the
  two-writer confusion this repository keeps paying for.

## 5. What the blast radius actually is, stated rather than implied

This is a **probe**, run by hand, printing to the operator's own terminal — not
the server, and not a tracked output file. The value is a URL the site chose
during one allowlisted navigation.

That is smaller than it sounds, and larger than it looks. **This exact thing
has already happened once**, and the guard exists because of it: the function's
own docstring records that on 2026-09-03 a vanity slug reached a transcript
three ways, one of them *"a probe printing a landed path out of a file whose
docstring promised it never printed a url."* The guard built in answer to that
incident does not catch this spelling of it.

A terminal is not nothing: transcripts are read, pasted and summarised, and the
measured landings are `/feed`, `/messaging` and `/jobs/view/<numeric-id>` —
none carrying a slug today. **"The landing can be a NAME" remains DERIVED, not
observed** (`landing-evidence`, 14 of 14 predecessor-to-parameter agreements,
zero `/in/` and zero slugs among them). So the leak is real and its worst case
is unwitnessed, which is the honest way round to say it.
