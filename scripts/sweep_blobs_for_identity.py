"""Sweep the BLOBS of a commit range for known-real identity values.

WHY THIS EXISTS, and it is a scar rather than a feature request.

``sweep_tracked_for_identity.py`` reads tracked files AS THEY ARE ON DISK. A
clean working tree therefore says NOTHING about what a push would publish: a
value can be removed in a follow-up commit -- which is the correct remedy in a
tree several waves are writing to -- and still sit in every earlier blob.

On 2026-09-05 three separate people needed that reading, could not get it from
the shipped sweep, and each wrote their own. **All three were broken**, and the
first two were caught only because a control fired. The third printed

    sweeping blobs with 0 spellings
      <sha> ... classes hit: NONE   (and five more, all NONE)

**An empty needle set matches nothing, and its NONE is not a result.** Six
all-clear lines under one line that said the instrument was mute.

The repo already had the rule -- *when a repo ships an instrument, IMPORT IT;
do not reimplement it to point at a different corpus* -- and the rule did not
prevent its own violation three times in one day. **A rule that keeps being
broken from the same motive is a MISSING TOOL, not a missing reminder.** The
motive was identical every time: wanting the sweep aimed somewhere its
enumeration does not reach. This file is that somewhere.

WHAT MAKES IT DIFFERENT FROM THE THREE BROKEN ONES

1. It IMPORTS ``load_wordlist`` and ``redact`` from the shipped sweep. It does
   not parse the key, does not filter values, does not build spellings. Every
   one of the three failures was in exactly that re-derivation -- the key's
   prose fields swallowed as values, ``_ignore_values`` not applied, or (the
   third) the already-expanded return value re-parsed as raw json, yielding
   nothing at all.
2. **IT REFUSES TO REPORT A GREEN IT CANNOT BACK.** If the needle set is empty
   it exits NON-ZERO saying it cannot speak, instead of printing a clean sweep.
   A zero from a working instrument and a zero from a mute one are the same
   character, and this is the one defect this file exists to make impossible.
3. It prints the needle COUNT on every run, above the findings, so the reading
   arrives with its own denominator.
4. It never prints a matched value -- file, line number and class only, plus
   the shipped ``redact`` shape.

USAGE

    ./venv/Scripts/python.exe scripts/sweep_blobs_for_identity.py <range>
    ./venv/Scripts/python.exe scripts/sweep_blobs_for_identity.py --help

``<range>`` is anything ``git rev-list`` accepts; it defaults to the unpushed
commits (``@{upstream}..HEAD``), falling back to all of ``HEAD`` when there is
no upstream.

Exit status is 0 for a clean sweep, 1 for hits, 2 for anything that stops the
sweep from being a real measurement: an empty needle set, a range
``git rev-list`` itself cannot resolve, a range that resolves to zero
commits, or zero blobs actually inspected after exemptions. **2 never means
clean -- only 0 does.**

WHY A RESOLVABLE-BUT-EMPTY RANGE ALSO REFUSES, RECORDED BECAUSE THIS WAS
GOTTEN WRONG ONCE, ON PURPOSE, AND CORRECTED THE SAME DAY. The tempting
argument is that ``origin/master..HEAD`` being empty is the NORMAL state of a
synced repo, so refusing there would hard-fail the healthy case. That
argument attaches a MEASURED FACT (the range is empty right now) to a
NORMATIVE CLAIM (therefore it is safe to pass) without separating them, and
they do not separate: **an empty result is ambiguous between "there is
genuinely nothing to check" and "this range was pointed at the wrong
history."** A misconfigured upstream, a detached HEAD, a typo'd ref that
happens to resolve, a stale local ``origin/master`` nobody fetched -- all
yield zero commits while unpushed work exists outside what was actually
measured. The emptiness proves the RANGE is empty; it does not prove the
REPO is synced. Those are different claims about a real person's identity in
a public repo, and only a refusal is honest about which one was established.

WHY THE REFUSAL IS SPELLED NEITHER ``PASS`` NOR ``FAIL``. ``scripts/
purge_denied_term.py`` is this script's one real caller; it reads the
verdict LINE, not the exit code, and ends with *"Both sweeps must read PASS
before pushing. If either FAILs, run: git reset --hard <tag>."* ``FAIL``
there names a DESTRUCTIVE remedy -- a refusal means "I could not establish
anything," which is not the same claim as "I found a hit," and spelling it
``FAIL`` would point an operator at a hard reset for a problem a hard reset
does not fix. A line starting with neither word prints as ``(no verdict)``
in that caller, which still blocks the push (the caller's rule is "must
read PASS," not "must not read FAIL") without misdirecting the remedy.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from sweep_tracked_for_identity import decode_text, load_wordlist, redact  # noqa: E402

#: Blob paths worth sweeping. The key itself and the denylists legitimately
#: hold real values; the shipped sweep exempts them by exact path and so does
#: this one, by the same names, so the two agree about what is exempt.
SKIP_SUFFIXES = ("_sanitisation_key.json",)


class GitError(RuntimeError):
    """A ``git`` call the caller asked to be checked came back non-zero.

    Carries the argv, the exit code and stderr so a caller can report what
    git actually said instead of guessing from an empty string. Before this
    class existed ``_git()`` returned ``out.stdout`` alone and threw the
    return code and stderr away, so a failed call and a call that
    legitimately produced nothing were the same value to every caller --
    that is the whole defect this file exists to make impossible, one layer
    lower than the mute-needle-set check above.
    """

    def __init__(self, git_args: tuple[str, ...], returncode: int, stderr: str) -> None:
        super().__init__(f"git {' '.join(git_args)} exited {returncode}")
        self.git_args = git_args
        self.returncode = returncode
        self.stderr = stderr


def _git(*args: str, check: bool = True) -> str:
    out = subprocess.run(
        ["git", *args], cwd=REPO, capture_output=True, text=True, errors="replace"
    )
    if check and out.returncode != 0:
        raise GitError(args, out.returncode, out.stderr)
    return out.stdout


def _as_text(data: bytes) -> str:
    """A blob's bytes as the text the wordlist is matched against.

    THE SHARED RULE, ``sweep_tracked_for_identity.decode_text``: UTF-8 when
    valid, else cp1252. CHANGED DELIBERATELY 2026-10-10. Until then this was
    the text ``subprocess.run(text=True, errors="replace")`` produced -- the
    LOCALE's encoding, cp1252 on the operator's box -- so the 9 needles with
    non-ASCII letters could never match a UTF-8 blob there. The batch reader
    that landed the same day reproduced that text byte for byte on purpose;
    this is the separate, ruled change of what the text is.
    """
    return decode_text(data)


class _BlobReader:
    """Every blob of a sweep through ONE ``git cat-file --batch`` process.

    WHY, MEASURED 2026-10-10. The loop below used to call
    ``_git("cat-file", "-p", sha)`` once per blob, and a process launch costs
    tens of milliseconds on Windows: 72s for one commit's 997 blobs, 217s for
    a 3-commit range of 1002 blobs on a busy box. The pre-push gate runs this
    sweep on every ``ci/`` push, so the launch cost was most of a lane's push.

    WHAT THE BATCHING DID NOT CHANGE: which blobs are read, in what order,
    and (at the time) the text each was matched as -- its stdout was byte-
    identical to the per-blob version's on two real ranges. The text itself
    then changed deliberately, in ``_as_text``, as a separate ruled step.
    Started on the first read, so a sweep that refuses before its blob loop
    never launches it.

    A blob git cannot produce -- ``<sha> missing``, a short read, a process
    that died -- raises ``GitError`` (exit 128, what ``cat-file -p`` exited
    with for the same input), so ``main`` refuses with exit 2 exactly as it
    did when the per-blob call failed.
    """

    def __init__(self) -> None:
        self._proc: subprocess.Popen | None = None
        self._err = None

    def read(self, sha: str) -> str:
        if self._proc is None:
            # stderr to a FILE, not a pipe: nobody reads stderr until git has
            # failed, and a full stderr pipe would block git mid-answer.
            self._err = tempfile.TemporaryFile()
            self._proc = subprocess.Popen(
                ["git", "cat-file", "--batch"], cwd=REPO,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=self._err,
            )
        proc = self._proc
        try:
            proc.stdin.write(sha.encode("ascii") + b"\n")
            proc.stdin.flush()
            header = proc.stdout.readline()
        except OSError:  # the pipe broke: git is gone
            header = b""
        fields = header.split()
        if (len(fields) != 3 or fields[1] != b"blob"
                or fields[0].decode("ascii", "replace") != sha):
            self._fail(sha, header)
        size = int(fields[2])
        data = proc.stdout.read(size)
        if len(data) != size or proc.stdout.read(1) != b"\n":
            self._fail(sha, b"short read")
        return _as_text(data)

    def _fail(self, sha: str, header: bytes) -> None:
        said = ""
        if self._err is not None:
            self._err.seek(0)
            said = self._err.read().decode("utf-8", "replace").strip()
        code = self._proc.poll() if self._proc is not None else None
        raise GitError(("cat-file", "--batch", sha), 128 if code is None else code,
                       said or header.decode("utf-8", "replace").strip() or "no answer")

    def close(self) -> None:
        proc, self._proc = self._proc, None
        if proc is not None:
            try:
                proc.stdin.close()
            except OSError:
                pass
            try:
                proc.wait(timeout=30)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
            proc.stdout.close()
        if self._err is not None:
            self._err.close()
            self._err = None


def _default_range() -> str:
    # check=False: a branch with no upstream is an ORDINARY outcome here,
    # not a failure to surface. git exits non-zero for it and this falls
    # back to sweeping all of HEAD -- exactly what it did before this file
    # could tell a failure from an empty success at all.
    if _git("rev-parse", "--abbrev-ref", "@{upstream}", check=False).strip():
        return "@{upstream}..HEAD"
    return "HEAD"


def main(argv: list[str]) -> int:
    # HELP IS NOT A REV RANGE. Checked before anything else touches argv[1]
    # so "--help" (or a typo shaped like a flag) can never fall through to
    # git rev-list as if it were a range -- which is exactly how this file's
    # own vacuous-pass bug was found: git rev-list --help failed silently,
    # _git() swallowed that, and the empty result printed PASS.
    if len(argv) > 1 and argv[1] in ("--help", "-h"):
        print(__doc__)
        return 0

    rev_range = argv[1] if len(argv) > 1 else _default_range()

    # ------------------------------------------------------------------
    # THE RANGE IS VALIDATED FIRST, BEFORE THE WORDLIST IS EVEN LOADED,
    # and the order is deliberate. Rejecting a bad ARGUMENT must not depend
    # on the ENVIRONMENT: the wordlist is gitignored, so on a machine that
    # has none -- every CI runner, by design -- `load_wordlist()` raises
    # before the range is ever looked at, and the tool then reports a
    # missing key for what is actually a malformed range. Measured on
    # 2026-09-20: three CI platforms failed with "the wordlist is missing"
    # on a test whose whole subject was a garbage rev range.
    #
    # It also removes a real overload. `load_wordlist()` exits 1, and exit 1
    # HERE means "hits found" -- so on a keyless machine a missing wordlist
    # was indistinguishable, by exit code, from a positive identity
    # detection. Validating the argument first means the only paths that can
    # still reach the wordlist are ones where a sweep is genuinely about to
    # happen.
    #
    # A git rev-list that FAILS and a range that
    # RESOLVES to ZERO commits are different facts about the world -- see
    # the module docstring for why the second one refuses too, rather
    # than passing on the strength of an empty result this script cannot
    # tell apart from a misaimed range -- but both are refused here,
    # before either can reach the loop, with distinguishable messages
    # naming which one happened.
    # ------------------------------------------------------------------
    try:
        commits = _git("rev-list", rev_range).split()
    except GitError as exc:
        print(
            f"REFUSING TO SWEEP: git rev-list {rev_range!r} FAILED "
            f"(exit {exc.returncode}).\n"
            f"  git said: {exc.stderr.strip()}\n"
            "  A range git itself cannot resolve is not a clean sweep of\n"
            "  zero commits -- it is an instrument that never ran."
        )
        return 2

    print(f"range  : {rev_range} -> {len(commits)} commit(s)")
    if not commits:
        print(
            f"REFUSING TO SWEEP: git rev-list {rev_range!r} resolved to "
            "ZERO commits.\n"
            "  Zero commits is a statement about this range, not about the\n"
            "  blobs it would have swept -- a clean-sweep result printed\n"
            "  here would be indistinguishable from a range that was\n"
            "  actually swept. Pick a range that contains at least one\n"
            "  commit."
        )
        return 2

    # ------------------------------------------------------------------
    # THE MUTE CHECK. This is the whole reason the file exists, and it still
    # runs BEFORE anything is swept, so no reassuring output can precede it.
    # It moved BELOW the range validation on 2026-09-20 and not one line
    # earlier: by here the range is known real and non-empty, so a sweep is
    # genuinely about to happen and the needles genuinely matter.
    # ------------------------------------------------------------------
    wordlist = load_wordlist()
    spellings = [(cls, s) for cls, values in wordlist.items() for s in values]

    print(f"needles: {len(spellings)} spellings across {len(wordlist)} classes")
    if not spellings:
        print(
            "REFUSING TO SWEEP: the needle set is EMPTY.\n"
            "  A sweep with no needles matches nothing and its clean result\n"
            "  would be a statement about this instrument, not about the\n"
            "  blobs. Three hand-rolled versions of this check reported\n"
            "  exactly that all-clear on 2026-09-05. Fix the key, not this\n"
            "  message."
        )
        return 2

    seen: set[str] = set()
    hits: list[tuple[str, str, int, str, str]] = []
    blobs = 0
    reader = _BlobReader()
    try:
        for commit in commits:
            for row in _git("ls-tree", "-r", commit).splitlines():
                meta, _, path = row.partition("\t")
                parts = meta.split()
                if len(parts) < 3 or parts[1] != "blob":
                    continue
                sha = parts[2]
                if sha in seen or path.endswith(SKIP_SUFFIXES):
                    continue
                seen.add(sha)
                blobs += 1
                text = reader.read(sha)
                if not text:
                    continue
                folded = text.casefold()
                found = {cls for cls, s in spellings if s.casefold() in folded}
                if not found:
                    continue
                for number, line in enumerate(text.splitlines(), 1):
                    low = line.casefold()
                    for cls, s in spellings:
                        if s.casefold() in low:
                            hits.append((sha[:9], path, number, cls, redact(line)))
                            break
    except GitError as exc:
        print(
            f"REFUSING TO SWEEP: git {' '.join(exc.git_args)} FAILED "
            f"(exit {exc.returncode}) while walking {rev_range!r}.\n"
            f"  git said: {exc.stderr.strip()}"
        )
        return 2
    finally:
        reader.close()

    print(f"swept  : {blobs} distinct blob(s)")
    print()

    # Same defect, one step later: a sweep that inspected zero blobs has
    # said nothing about the range's content, and a clean-sweep result
    # printed over that would look identical to a real clean sweep. The
    # guard sits immediately before the only print statement it exists to
    # gate.
    if blobs == 0:
        print(
            f"REFUSING TO SWEEP: {len(commits)} commit(s) in {rev_range!r} "
            "produced\n"
            "  ZERO blobs to inspect (after exempting the sanitisation "
            "key).\n"
            "  A sweep that inspected nothing may not report a clean "
            "sweep."
        )
        return 2

    if not hits:
        print(f"PASS: 0 hits across {blobs} blobs, {len(spellings)} needles.")
        return 0

    paths = sorted({h[1] for h in hits})
    print(f"FAIL: {len(hits)} hit(s) in {len(paths)} distinct path(s).")
    print("PURGE SCOPE -- the blobs a rewrite would have to reach:")
    for sha, path, number, cls, shape in hits:
        print(f"  {sha}  {path}:{number}  [{cls}]  {shape}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
