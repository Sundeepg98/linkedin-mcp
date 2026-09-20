"""`scripts/classify_writeoff_reasons.py --check` must be able to go RED.

WHY THIS EXISTS. An instrument that has never been shown failing certifies
nothing, and this repository has measured the disease rather than assumed it:
56 of 88 probe files carry a control that is computed, printed, and never
branched on. `--check` prints six `ok` lines over 309 write-off rows, and
before this file existed not one of them had been convicted.

WHAT IT DOES. It copies the four census slices into a temp dir, repoints the
instrument at the copy, damages the copy in a specific way, and asserts the
check goes red AND NAMES THE DAMAGE. Nothing in the repository is written.

THE MUTATION THAT MATTERS MOST is `test_a_slice_that_stops_being_read_goes_red`.
`--check` asserts PER FILE rather than over the union, and the whole argument
for that design is that a union assertion over a redundant corpus cannot detect
a lost source -- if `network.md` stopped being read, the other three slices
would still satisfy a union. That claim is only worth having if it is tested,
so the mutation is run against EVERY slice, not just the one the design
document names.

THE CALIBRATION IS PART OF THE INSTRUMENT, NOT A COURTESY.
`test_a_cosmetic_edit_changes_nothing` makes a change that must NOT move the
verdict -- a capability cell reworded, an id cell padded with whitespace, no
reason cell touched -- and asserts the output is BYTE-IDENTICAL to the
unmutated run. A harness where every mutation goes red is not discriminating,
it is broken, and there would be no way to tell from the red alone.

EVERY MUTATION ASSERTS IT LANDED BEFORE ITS RESULT IS BELIEVED. A mutation
that did not change the text looks EXACTLY like a control that did not fire,
and this repository has already been burned by precisely that: a harness that
inserted itself before `</body>` in a file that is a fragment with no `</body>`
and reported GREEN. `_landed` refuses on a byte-identical edit.

WHAT WAS FOUND BY RUNNING IT, recorded here because the findings are the
reason to keep the file rather than a footnote to it:

  * BACKREFERENCE INHERITANCE WAS SILENTLY DEAD. `build()` recovered the
    donor by matching `backref<-(\\S+)` against `r.resolution`. Every row key
    in this corpus contains a space (`P D14`), so the capture stopped at `P`,
    `by_key.get("P")` returned None, and none of the 46 `same` rows ever
    inherited a kind. No error, no warning -- they simply came out UNCLEAR,
    which is indistinguishable from a census that never wrote a reason.
    `test_backreference_inheritance_actually_runs` is the regression guard.

  * THE PER-FILE CONTROL'S SECOND HALF CANNOT FAIL.
    `unkinded = [r for r in sub if not r.kind]` runs after `finalise`, which
    sets `r.kind = "UNCLEAR"` when the kind set is empty. `r.kind` is
    therefore never falsy and that branch is unreachable. The half that CAN
    fail -- `if not sub` -- is the one exercised below. The dead half is
    documented rather than tested, because a test cannot convict it.

  * `FKEYS_SOURCE` IS NEVER PRINTED. `forbidden_keys()` says every failure
    path falls back to the nine measured names "AND SAYS SO in the run
    header". It does not: the value is assigned at module scope and read
    nowhere, so a reader of a FALLBACK run cannot tell it was one. There is
    no test for it below, because the property does not hold and this file
    may not fix the instrument it measures -- it is recorded here and in
    `_audit/_scratch/_kinds-mutation-results.md` for whoever does.

SHOWN FAILING, which is the only thing that makes any of it worth running.
The two backreference tests were run against the instrument as it stood at
`b839c85`, with the `\\S+` donor parse still in place: both went red, the
other 67 stayed green. A file that has only ever been green certifies nothing.

NO NETWORK, NO SESSION, NO BROWSER. This is a text test over markdown.
"""
from __future__ import annotations

import contextlib
import io
import pathlib
import re
import shutil
import sys

import pytest

_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "scripts"))

import count_census_states as C            # noqa: E402
import classify_writeoff_reasons as cw     # noqa: E402


# ---------------------------------------------------------------------------
# Sandbox
# ---------------------------------------------------------------------------
@pytest.fixture
def census(tmp_path):
    """A writable copy of the four slices, with the instrument repointed at it.

    REBINDING `cw.ADJUDICATIONS` ALONE IS NOT ENOUGH and the difference is
    silent. `load_adjudications(path=ADJUDICATIONS)` binds its default at
    definition time, so a test that moves only the module global keeps reading
    the committed overlay and cannot tell. Measured: 12 adjudications came
    back from a sandbox file holding none. Both are moved here, and both are
    put back.
    """
    sandbox = tmp_path / "_census"
    shutil.copytree(C.CENSUS, sandbox)
    real_census = C.CENSUS
    real_adj = cw.ADJUDICATIONS
    real_defaults = cw.load_adjudications.__defaults__
    C.CENSUS = sandbox
    cw.ADJUDICATIONS = sandbox / "reason-kind-adjudications.tsv"
    cw.load_adjudications.__defaults__ = (cw.ADJUDICATIONS,)
    try:
        yield sandbox
    finally:
        C.CENSUS = real_census
        cw.ADJUDICATIONS = real_adj
        cw.load_adjudications.__defaults__ = real_defaults


def _check() -> tuple[int, str]:
    """(exit code, everything `--check` printed)."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = cw.main(["--check"])
    return code, buf.getvalue()


def _read(path: pathlib.Path) -> str:
    with path.open("r", encoding="utf-8", newline="") as fh:
        return fh.read()


def _write(path: pathlib.Path, text: str) -> None:
    """Newline-transparent: the slices are CRLF and must stay CRLF."""
    with path.open("w", encoding="utf-8", newline="") as fh:
        fh.write(text)


def _landed(before: str, after: str, what: str) -> None:
    assert before != after, (
        f"THE MUTATION DID NOT LAND: {what} is byte-identical after the edit. "
        f"A mutation that changed nothing looks exactly like a control that "
        f"did not fire, so its GREEN would mean nothing."
    )


# ---------------------------------------------------------------------------
# Row surgery, using the shipped parse rather than a second one
# ---------------------------------------------------------------------------
_FENCE = re.compile(r"^\s*(```|~~~)")


def _raw_cells(line: str) -> list[str] | None:
    s = line.strip()
    if not (s.startswith("|") and s.endswith("|")):
        return None
    return s[1:-1].split("|")


def _rebuild(line: str, raw: list[str]) -> str:
    body = line.rstrip("\r\n")
    newline = line[len(body):]
    indent = body[: len(body) - len(body.lstrip())]
    return indent + "|" + "|".join(raw) + "|" + newline


def _state_index(raw: list[str]) -> tuple[int, str]:
    """Where `count_census_states.classify` would find this row's state.

    The first cell after the id whose leading word is in the shipped
    vocabulary -- the same rule `classify` applies, so a mutation cannot
    target a cell the instrument does not read.
    """
    for i, cell in enumerate(raw):
        if i == 0:
            continue
        bare = cell.replace("`", "").replace("*", "").strip()
        head = bare.split(" ")[0]
        if head in C.STATES:
            return i, head
    return -1, ""


def _gap_out_writeoffs(path: pathlib.Path) -> int:
    """Rewrite every WRITE-OFF state cell in this slice to GAP. Fence-aware.

    GAP is the right neutralising value: a GAP row is not closed, so it owes
    no reason and the instrument drops it from the write-off set without any
    other complaint. Returns the number of cells rewritten, so the caller can
    assert the edit was not a no-op.
    """
    out: list[str] = []
    changed = 0
    in_fence = False
    for line in _read(path).splitlines(keepends=True):
        if _FENCE.match(line):
            in_fence = not in_fence
            out.append(line)
            continue
        raw = None if in_fence else _raw_cells(line)
        if raw is None or len(raw) < 3:
            out.append(line)
            continue
        first = raw[0].strip()
        if not first or set(first) <= set("-: ") or first.lower() in C.HEADERS:
            out.append(line)
            continue
        idx, state = _state_index(raw)
        if idx < 0 or state not in cw.WRITEOFF:
            out.append(line)
            continue
        raw[idx] = " GAP "
        out.append(_rebuild(line, raw))
        changed += 1
    _write(path, "".join(out))
    return changed


# ---------------------------------------------------------------------------
# The baseline every mutation is measured against
# ---------------------------------------------------------------------------
def test_the_unmutated_corpus_is_green(census):
    """Without this, a red below could be the corpus rather than the mutation."""
    code, out = _check()
    assert code == 0, f"the committed census does not pass --check:\n{out}"
    assert "FAIL" not in out, out


# ---------------------------------------------------------------------------
# M1 -- the per-file assertion
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("letter,name", sorted(C.SLICES.items()))
def test_a_slice_that_stops_being_read_goes_red(census, letter, name):
    """One slice yielding zero write-off rows must fail, and must be NAMED.

    RUN AGAINST ALL FOUR, not just the slice the design document names. The
    claim being tested is that the assertion is PER FILE; a union assertion
    would be satisfied by the surviving three in every one of these cases, so
    each slice is its own conviction.
    """
    path = census / name
    before = _read(path)
    rewritten = _gap_out_writeoffs(path)
    _landed(before, _read(path), name)
    assert rewritten > 0, f"{name} had no write-off state cells to neutralise"

    code, out = _check()
    assert code != 0, (
        f"{name} now contributes ZERO write-off rows and --check still passed. "
        f"The per-file control is decorative: a slice that stopped being read "
        f"looks exactly like a slice with nothing to say.\n{out}")
    assert f"FAIL  {name} contributed ZERO write-off rows" in out, out


# ---------------------------------------------------------------------------
# M2 -- the pinned quote
# ---------------------------------------------------------------------------
def test_a_pinned_quote_that_moved_goes_red(census):
    """Reword a ruling out from under its hand judgement; expect a loud red.

    This is the entire reason the hand overlay is safe. A hand judgement
    written against text somebody has since rewritten is a label that looks
    maintained and is not, which is the failure the whole classification
    exists to find -- one level up, in its own machinery.
    """
    path = census / "network.md"
    before = _read(path)
    quote = "catching a read that has nothing to do with inviting"
    assert quote in before, (
        "the R2 ruling body no longer contains the quote this test moves. "
        "Re-read the adjudication before editing this test.")
    _write(path, before.replace(quote, "intercepting a read that has "
                                       "nothing to do with inviting", 1))
    _landed(before, _read(path), "network.md")
    assert quote not in _read(path)

    code, out = _check()
    assert code != 0, f"the pinned-quote control did not fire:\n{out}"
    assert "ADJUDICATION for RULING R2 pins the quote" in out, out
    assert "NO LONGER PRESENT" in out, out


# ---------------------------------------------------------------------------
# M3 -- an adjudication that has gone moot
# ---------------------------------------------------------------------------
def test_an_adjudication_on_a_row_that_left_the_writeoffs_goes_red(census):
    """`J 134` stops being a write-off; its row-level judgement is now moot.

    A hand ruling that survives the row it rules on is not merely useless --
    it is a claim about a row nobody is checking any more.
    """
    path = census / "jobs.md"
    before = _read(path)
    out_lines, touched = [], 0
    for line in before.splitlines(keepends=True):
        raw = _raw_cells(line)
        if raw and len(raw) >= 3 and raw[0].strip() == "134":
            idx, state = _state_index(raw)
            if idx >= 0 and state in cw.WRITEOFF:
                raw[idx] = " GAP "
                line = _rebuild(line, raw)
                touched += 1
        out_lines.append(line)
    assert touched == 1, f"expected exactly one J 134 write-off row, hit {touched}"
    _write(path, "".join(out_lines))
    _landed(before, _read(path), "jobs.md")

    code, out = _check()
    assert code != 0, f"the moot-adjudication control did not fire:\n{out}"
    assert "ADJUDICATION for 'J 134' names a row that is not a write-off row" in out, out


# ---------------------------------------------------------------------------
# M4 -- a ruling section that has gone missing
# ---------------------------------------------------------------------------
def test_a_deleted_ruling_section_is_reported(census):
    """Delete `### R5` and expect BOTH failure modes, not either one.

    Rows point at a ruling by code and inherit its adjudicated kind, so a
    ruling that disappears breaks the chain at two places at once: the rows
    citing it can no longer resolve, and the hand adjudication pinned on it
    now names a section nothing has. Asserting only one of those would let
    the other rot -- a corpus with no rows citing R5 would still need the
    orphaned adjudication reported, and vice versa.

    The count is asserted too. R5's own heading says "Produces 9 rows", and
    exactly nine rows complain, so the ruling's published count is checked
    against the corpus for free.

    **THE PIN MOVED 6 -> 9 ON 2026-09-20 AND THE NUMBER IS WRITTEN OUT HERE
    RATHER THAN DERIVED FROM THE HEADING, DELIBERATELY.** Reading the count out
    of the heading would make this assertion unfalsifiable: the heading and the
    corpus would then be compared against each other by a test that got its
    expectation from one of them, so a wave that moved rows and updated the
    heading to match would stay green while a wave that moved rows and forgot
    would ALSO stay green. A literal here is the only version that can convict.

    It moved because the write-partition wave filed three more rows under R5 --
    `96`, `A14`, `A15` -- and this test is what caught the heading still saying
    six. That is the guard working, and the cost of the design is exactly one
    line of maintenance per real change, paid here.
    """
    path = census / "network.md"
    before = _read(path)
    lines = before.splitlines(keepends=True)
    in_fence, start, end = False, None, None
    for i, line in enumerate(lines):
        if _FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if start is None and re.match(r"^###\s+R5\b", line):
            start = i
            continue
        if start is not None and re.match(r"^#{1,3}\s", line):
            end = i
            break
    assert start is not None, "no `### R5` heading in network.md"
    end = len(lines) if end is None else end
    _write(path, "".join(lines[:start] + lines[end:]))
    _landed(before, _read(path), "network.md")
    assert not re.search(r"^###\s+R5\b", _read(path), re.M)

    code, out = _check()
    assert code != 0, f"a deleted ruling section did not turn --check red:\n{out}"

    citing = [l for l in out.splitlines()
              if "cites R5, which has no ruling section" in l]
    assert len(citing) == 9, (
        f"R5's heading says it produces 9 rows; {len(citing)} rows reported an "
        f"unresolvable citation:\n" + "\n".join(citing))
    assert ("ADJUDICATION 'RULING R5' names a ruling section that network.md "
            "no longer has") in out, out


# ---------------------------------------------------------------------------
# M5 -- an empty corpus
# ---------------------------------------------------------------------------
def test_an_empty_corpus_is_a_loud_event(census):
    """All four slices neutralised. An assertion satisfied by nothing is not one.

    The dangerous version of this failure is not the check returning 1, it is
    the check printing six `ok` lines over an empty set and returning 0.
    """
    total = sum(_gap_out_writeoffs(census / name) for name in C.SLICES.values())
    assert total > 0

    code, out = _check()
    assert code != 0, f"an empty corpus passed --check:\n{out}"
    assert "the corpus yielded ZERO write-off rows" in out, out
    assert "never a silent pass" in out, out
    assert "ok    corpus is non-empty" not in out, out


# ---------------------------------------------------------------------------
# M8 -- the calibration. This one must stay GREEN.
# ---------------------------------------------------------------------------
def test_a_cosmetic_edit_changes_nothing(census):
    """A change outside every reason cell must not move one byte of the verdict.

    Without this, every red above is uninterpretable: a check that fails on
    any edit at all is not measuring reasons, it is measuring that somebody
    touched the file.
    """
    baseline_code, baseline_out = _check()
    assert baseline_code == 0

    path = census / "profile.md"
    before = _read(path)
    lines = before.splitlines(keepends=True)
    touched = []
    for i, line in enumerate(lines):
        raw = _raw_cells(line)
        if not raw or len(raw) < 4:
            continue
        if raw[0].strip() == "D18":
            raw[1] = " Accolades and prizes "      # capability reworded
            lines[i] = _rebuild(line, raw)
            touched.append("D18")
        elif raw[0].strip() == "D13":
            raw[0] = "  D13  "                     # pure padding
            raw[2] = "  " + raw[2].strip() + "  "
            lines[i] = _rebuild(line, raw)
            touched.append("D13")
    assert sorted(touched) == ["D13", "D18"], touched
    _write(path, "".join(lines))
    _landed(before, _read(path), "profile.md")

    code, out = _check()
    assert code == 0, f"a cosmetic edit turned --check red:\n{out}"
    assert out == baseline_out, (
        "a capability-cell rewording and some whitespace padding moved the "
        "verdict. Either a signal is matching text outside the reason cell, "
        "or the reason cell is not being identified the way this test thinks "
        "it is.\n" + "\n".join(
            l for l in out.splitlines() if l not in baseline_out.splitlines()))


# ---------------------------------------------------------------------------
# P1 -- needle liveness
# ---------------------------------------------------------------------------
def _synthetic_positive(label: str) -> str:
    """A string each signal MUST match. See `test_every_signal_has_a_needle`."""
    if label == "forbidden-key":
        # Derived, not spelled: the key list is read from the package, so a
        # hardcoded name here would rot the day somebody renames an entry.
        return cw._FKEYS[0]
    return _SYNTHETIC[label]


#: A SIGNAL THAT FIRES ZERO TIMES ON THE CORPUS AND A SIGNAL THAT CANNOT FIRE
#: AT ALL LOOK IDENTICAL IN A COUNT. Five of the table's signals are at zero
#: over all 704 stated rows -- `not-built`, `cannot-verify-send`,
#: `unverifiable-account`, `his-locale` and the whole of PROCESS-FACT's
#: `live-process` -- and the only way to say "that is a real zero" is to feed
#: each pattern a string it is supposed to match. The corpus has already paid
#: for this lesson once: `separate-product` was written `separate product`,
#: never fired, and was read as a fact about the world rather than as a dead
#: needle.
_SYNTHETIC = {
    "allowlist":            "the address is not on the allow-list",
    "denylist":             "it sits on the deny-list",
    "forbidden-substring":  "/invite/ is a forbidden substring",
    "mutation-verb":        "no mutation-verb is exposed for it",
    "not-on-allowlist":     "not admitted by the allowlist at all",
    "admitted-by-name":     "the family is admitted by name or not at all",
    "boundary":             "the boundary refuses it",
    "settings-family":      "a /psettings/ toggle, settings-family",
    "src:readonly.py":      "no spec in readonly.py",
    "src:writes.py":        "writes.py ships no spec",
    "src:server.py":        "server.py exposes no tool",
    "src:shape/dom":        "nothing in shape.py builds it",
    "src:package":          "linkedin_server has no reader",
    "ruling":               "written off on the NEVER-LOADED ruling",
    "edit-family":          "/edit/ family ruling",
    "operator-ruled":       "the operator ruled it out",
    "no-tool":              "no tool reaches it",
    "no-reader":            "no reader parses that panel",
    "not-built":            "deliberately not built",
    "nothing-builds":       "nothing builds this payload",
    "structurally":         "structurally unable to answer",
    "unaimable":            "the control has no aria-label and is unaimable",
    "this-server":          "this server refuses it",
    "writespec":            "no WriteSpec covers it",
    "name-freedom":         "the name-freedom ruling forbids it",
    "cannot-verify-send":   "nothing here can verify a send",
    "this-account":         "this account does not hold it",
    "for-him":              "LinkedIn does not draw it for him",
    "he-holds":             "he holds a paid subscription",
    "his-thing":            "his profile draws no such row",
    "never-actioned":       "NEVER ACTIONED by him",
    "not-drawn-for":        "not drawn for this account",
    "spends-a-credit":      "the send spends an InMail credit",
    "entitlement":          "the panel is premium-gated",
    "unverifiable-account": "unverifiable on this account",
    "operator-must-act":    "the operator names the target himself",
    "his-locale":           "his locale does not render it",
    "help-centre":          "the Help article documents it",
    "linkedin-says":        "LinkedIn draws no such control",
    "linkedin-learning":    "it opens LinkedIn Learning in a new tab",
    "geography":            "the product is US-only",
    "mobile-only":          "the control is mobile only",
    "third-party":          "loading a third-party profile",
    "served-by-skill":      "this is served by the skill instead",
    "sibling-slice":        "owned by the messaging slice",
    "separate-product":     "opens as a separate LinkedIn Learning product",
    "http-404":             "the Help article is 404 on all three verticals",
    "needs-hardware":       "it needs camera and microphone",
    "not-on-the-page":      "the balance is not on the page",
    "live-process":         "measured off the live server, which is 58 commits stale",
    "forbidden-key":        "",   # derived in _synthetic_positive
}


@pytest.mark.parametrize("label", [s[0] for s in cw.SIGNALS])
def test_every_signal_has_a_live_needle(label):
    """Each pattern must match a string it is supposed to match.

    This is the only assertion that can tell a real zero from a dead needle,
    and it runs over EVERY signal rather than only today's zeroes -- a signal
    at 40 hits today can be narrowed to zero tomorrow by an edit that looks
    like a tightening.
    """
    pattern = dict((lab, pat) for lab, _kind, pat in cw.SIGNALS)[label]
    probe = _synthetic_positive(label)
    assert probe, f"no synthetic positive is written for signal {label!r}"
    assert pattern.search(probe), (
        f"DEAD NEEDLE: signal {label!r} does not match {probe!r}.\n"
        f"pattern: {pattern.pattern}\n"
        f"A signal that cannot match anything reports the same zero as a fact "
        f"that is never true, and nothing downstream can tell the two apart.")


def test_the_needle_table_covers_every_signal():
    """A signal added without a synthetic positive must fail here, not pass silently."""
    missing = sorted({lab for lab, _k, _p in cw.SIGNALS} - set(_SYNTHETIC))
    assert not missing, (
        f"{len(missing)} signal(s) have no synthetic positive, so their "
        f"liveness is unmeasured: {missing}")
    stale = sorted(set(_SYNTHETIC) - {lab for lab, _k, _p in cw.SIGNALS})
    assert not stale, f"synthetic positives for signals that no longer exist: {stale}"


def test_process_fact_has_exactly_one_needle_and_it_is_alive():
    """PROCESS-FACT fires zero times on the corpus. Prove that is a real zero.

    The class was added on a coordinator's report that one refusal had been
    read off a server 58 commits stale. If the needle were dead, the corpus
    would report the same zero and the class would look like a category
    somebody invented.
    """
    needles = [(lab, pat) for lab, kind, pat in cw.SIGNALS
               if kind == "PROCESS-FACT"]
    assert [lab for lab, _ in needles] == ["live-process"], needles
    pattern = needles[0][1]
    for probe in ("measured off the live server, which is 58 commits stale",
                  "read from the running server",
                  "the server that answered section 3",
                  "a stale mcp process answered"):
        assert pattern.search(probe), (probe, pattern.pattern)
    assert not pattern.search("no such control is drawn on the page")


# ---------------------------------------------------------------------------
# M6 -- the fallback may never build a match-everything pattern
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("damage", ["renamed", "emptied", "absent"])
def test_forbidden_keys_never_returns_an_empty_list(tmp_path, damage):
    """Every failure path returns the nine-name fallback, and says which path.

    THE HAZARD IS SPECIFIC. `"|".join([])` inside an alternation yields
    `\\b(?:)\\b`, which matches at every position -- so an empty key list would
    not disable the `forbidden-key` signal, it would tag all 309 rows
    US-RULING. The assertion below is on the built pattern, not on the list
    length, because the list length is not what would do the damage.
    """
    real = (_ROOT / "linkedin_server" / "writes.py").read_text(
        encoding="utf-8", errors="replace")
    pkg = tmp_path / "linkedin_server"
    pkg.mkdir()
    if damage == "renamed":
        (pkg / "writes.py").write_text(
            real.replace("PERMANENTLY_FORBIDDEN", "TEMPORARILY_ALLOWED"),
            encoding="utf-8")
        expect = "FALLBACK -- no PERMANENTLY_FORBIDDEN block"
    elif damage == "emptied":
        (pkg / "writes.py").write_text(
            "PERMANENTLY_FORBIDDEN: dict[str, str] = {\n}\n", encoding="utf-8")
        expect = "FALLBACK -- block parsed but held no keys"
    else:
        shutil.rmtree(pkg)
        expect = "FALLBACK -- writes.py unreadable"

    real_root = cw.ROOT
    cw.ROOT = tmp_path
    try:
        keys, source = cw.forbidden_keys()
    finally:
        cw.ROOT = real_root

    assert keys, "forbidden_keys() returned an EMPTY LIST -- see the docstring"
    assert keys == list(cw._FORBIDDEN_FALLBACK), keys
    assert source == expect, source

    built = re.compile(r"\b(?:" + "|".join(re.escape(k) for k in keys) + r")\b")
    assert not built.search("hello world"), (
        f"the {damage} fallback built a pattern that matches arbitrary text: "
        f"{built.pattern}")
    assert built.search(keys[0]), built.pattern


def test_an_empty_key_list_really_would_match_everything():
    """The hazard the guard exists against, demonstrated rather than asserted.

    Without this, `test_forbidden_keys_never_returns_an_empty_list` is a check
    against a danger nobody has seen. The pattern below is exactly what the
    alternation builds from no keys.
    """
    hazard = re.compile(r"\b(?:" + "|".join([]) + r")\b")
    assert hazard.pattern == r"\b(?:)\b"
    assert hazard.search("hello world"), (
        "the documented hazard does not reproduce; re-read forbidden_keys()")


def test_the_live_key_list_is_read_from_the_package():
    """The committed tree must be on the READ path, not the fallback path.

    A green fallback test above says nothing about which path production takes.
    """
    keys, source = cw.forbidden_keys()
    assert source == "read from linkedin_server/writes.py", source
    assert len(keys) >= 9, keys


# ---------------------------------------------------------------------------
# The backreference regression that this file was written to find
# ---------------------------------------------------------------------------
def test_backreference_inheritance_actually_runs(census):
    """A `same` row must end up with its donor's kinds, not with UNCLEAR.

    THIS WAS DEAD AND NOTHING SAID SO. The donor was recovered by matching
    `backref<-(\\S+)` against a label holding `backref<-P D14`; the capture
    stopped at `P`, the lookup missed, and 46 rows silently kept an empty kind
    set. The failure mode is the one this whole wave is about: a result that
    looks like a finding about the census (`UNCLEAR`) and is a fact about the
    instrument.
    """
    assert "backref_donor" in cw.Row.__slots__, (
        "Row carries no `backref_donor` slot, so the donor can only be "
        "recovered by re-parsing the `backref<-...` label out of "
        "`.resolution`. That parse was MEASURED WRONG: every row key holds a "
        "space, `\\S+` stops at the slice letter, and the inheritance step "
        "silently never ran.")
    rows, wo, _dialects, _stated, _rulings, _problems, _adj = cw.build(None)
    donors = [r for r in rows if r.backref_donor]
    assert donors, "no row resolved a backreference at all -- check the corpus"

    by_key = {r.key: r for r in rows}
    unresolved = [r.key for r in donors if r.backref_donor not in by_key]
    assert not unresolved, (
        f"{len(unresolved)} backreference donor(s) do not name a real row: "
        f"{unresolved[:10]}. The donor is being derived from a string the "
        f"row keys do not match.")

    inherited = [r for r in wo
                 if r.source == "inherit-backref" and r.kinds]
    assert inherited, (
        "not one write-off row inherited a kind through a backreference. "
        "Either every donor has an empty kind set, or the inheritance step "
        "is not running.")


def test_a_row_inserted_above_a_backreference_repoints_it(census):
    """The census's own construct is position-resolved. Measured, not argued.

    This is NOT a defect in the classifier -- it faithfully reproduces what
    `same` means. It is a measurement of how fragile the construct is: one
    row inserted between the donor and its dependents re-points three rows
    and changes their verdict, with exit 0 and no warning anywhere. The
    assertion is on the SILENCE as much as on the re-pointing.
    """
    rows, _wo, *_ = cw.build(None)
    before = {r.key: getattr(r, "backref_donor", "")
              for r in rows if r.key in ("P D15", "P D16", "P D17")}
    assert set(before.values()) == {"P D14"}, before

    path = census / "profile.md"
    original = _read(path)
    lines = original.splitlines(keepends=True)
    planted = ("| D14a | Volunteer experience | W | EXCLUDED-RULED | a wholly "
               "different argument planted by a test, sharing no vocabulary "
               "with the row above it, long enough to clear the substantive "
               "threshold |")
    for i, line in enumerate(lines):
        raw = _raw_cells(line)
        if raw and len(raw) >= 3 and raw[0].strip() == "D14":
            tail = line[len(line.rstrip("\r\n")):] or "\n"
            lines.insert(i + 1, planted + tail)
            break
    else:
        pytest.fail("P D14 not found in profile.md")
    _write(path, "".join(lines))
    _landed(original, _read(path), "profile.md")

    code, out = _check()
    rows2, _wo2, *_ = cw.build(None)
    after = {r.key: getattr(r, "backref_donor", "")
             for r in rows2 if r.key in ("P D15", "P D16", "P D17")}

    assert set(after.values()) == {"P D14a"}, (
        f"expected all three dependents to re-point at the inserted row; "
        f"got {after}")
    assert code == 0 and "FAIL" not in out, (
        "the re-pointing was reported, which would be better than the "
        "measured behaviour -- update this test and say so")


# ---------------------------------------------------------------------------
# RESTORED VERBATIM FROM `e1b44b0`, WHICH A LATER WHOLE-FILE WRITE DROPPED
# ---------------------------------------------------------------------------
# TWO AGENTS WROTE THE SAME PATH IN ONE TREE AND THE LATER WRITE TOOK THE WHOLE
# FILE. `e1b44b0` committed an 11-test version of this file; `dd73d37` replaced
# it wholesale with a colder, better 69-test one, and two unique tests went with
# it. That is a COVERAGE REGRESSION regardless of whose file was better, and it
# is the second instance of this root cause today -- the other landed through
# the git index rather than the filesystem, sweeping 208 lines of a live wave's
# staged work. THE HAZARD IS TWO WRITERS AND ONE PATH; the index and the
# filesystem are only two ways it lands. A wave creating a file at a path a
# sibling might also target should check for it BEFORE writing, not after.
#
# The test below is lifted UNCHANGED from `e1b44b0` -- not paraphrased, not
# "improved" in transit, because guessing at the intent of a test is how a test
# gets weakened while looking restored. Only the two helpers it needs are new,
# and they are mechanical.
#
# (`test_a_deleted_ruling_section_is_reported`, the other dropped test, was
# restored separately and independently because it fell inside the mutation set.)


@pytest.fixture
def real_census():
    """The committed corpus, restored afterwards whatever a test does to it.

    New here. `e1b44b0` carried a fixture of this name; the surviving file
    drives everything through a mutated sandbox instead, so the unmutated
    corpus needed a name again.
    """
    original = C.CENSUS
    yield original
    C.CENSUS = original


def build_at(census_dir):
    """`cw.build` against a given corpus directory. New here, mechanical."""
    C.CENSUS = census_dir
    return cw.build(None)


def test_every_ruling_section_is_adjudicated(real_census):
    """72 rows inherit from 11 rulings, so an unadjudicated ruling silently unclassifies
    a whole block. A keyword sweep over a 2,735-character ruling body was measured to
    produce a three-kind verdict carrying no information, which is why these are hand
    judgements pinned to quotes."""
    _, _, _, _, rulings, problems, adj = build_at(real_census)
    adjudicated = {a.key for a in adj if a.key.startswith("RULING ")}
    for code in rulings:
        assert f"RULING {code}" in adjudicated, f"{code} has no adjudication"
    assert not [p for p in problems if "ADJUDICATION" in p]
