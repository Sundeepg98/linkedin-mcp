"""Red-proof for `tests/test_the_audit_index_is_derived.py`, on demand, forever.

**AN INSTRUMENT THAT HAS ONLY EVER BEEN GREEN CERTIFIES NOTHING.** The guard's
own controls plant defects into `render()` and assert the derivation moves;
that proves the generator is sensitive. It does NOT prove the assertion that
actually gates a commit -- `test_the_committed_index_is_what_the_corpus_derives`
-- has ever gone red. Those are different claims, and this file makes the
second one, by running the real pytest selector against a real planted defect
and asserting it FAILS.

**NOTHING IS MUTATED IN THE LIVE TREE.** `_audit/` is written continuously by
concurrent waves, and this register's own preamble records a wave that proved
three gates by mutating a file another agent was holding uncommitted work in --
five-second windows in which a byte-exact restore would have silently reverted
somebody's edit, and a verification incapable of detecting the failure it was
risking. So this copies what it needs into a scratch directory, ASSERTS the
copy is what pytest loaded, and plants there. The live repository is read only.

The copy needs to be a git repository, because `tracked_documents` asks
`git ls-files` rather than walking the disk -- deliberately, since
`_audit/_scratch/` is gitignored and a disk walk indexes documents no clone
has. So the scratch tree gets `git init` and one `git add`, which also makes
the "a new document was added" mutation mean what it means in the real repo.

    python scripts/_check_audit_index_guard_can_fail.py
    python scripts/_check_audit_index_guard_can_fail.py --keep
    python scripts/_check_audit_index_guard_can_fail.py --verbose

SEVEN RUNS: six planted, one clean control LAST, because a proof that ends on a
red says nothing about whether the tree was restored. Every planted run also
asserts the failure is the RIGHT ONE -- an import error, a collection error or
a missing-file error would fail the run too, and would prove only that the
harness is broken. A red for the wrong reason is worse than a green, because it
reads as rigour.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]

SELECTOR = ("tests/test_the_audit_index_is_derived.py"
            "::test_the_committed_index_is_what_the_corpus_derives")
FLOOR_SELECTOR = ("tests/test_the_audit_index_is_derived.py"
                  "::test_there_is_a_corpus_and_the_index_covers_all_of_it")

#: Copied one by one. `tests/conftest.py` is DELIBERATELY NOT among them: its
#: autouse fixtures import `linkedin_server`, which would drag the whole server
#: package into a scratch tree that has no business holding it, and no test in
#: the guard touches a browser, a session or a page.
COPY = (
    "scripts/build_audit_index.py",
    "tests/test_the_audit_index_is_derived.py",
    "tests/test_a_correction_is_findable_from_the_claim.py",
    "pytest.ini",
)

#: **`_audit/` IS STAGED FROM `git ls-files`, NOT `copytree`.** The first
#: version of this harness copied the directory and then ran `git add -A` in
#: the scratch tree with no `.gitignore` beside it, which would quietly promote
#: every ignored `_audit/_scratch/` working note into the scratch CORPUS. The
#: corpus under proof would then be one no clone has -- the precise
#: local-passes/clone-fails divergence the correction guard's `_documents`
#: exists to prevent, reintroduced by the file proving that guard's neighbour.
AUDIT = "_audit"


def _run(args, cwd, verbose=False):
    proc = subprocess.run(
        args, cwd=str(cwd), capture_output=True, text=True)
    if verbose:
        print("    $ %s -> %d" % (" ".join(args), proc.returncode))
        if proc.stdout:
            print("      %s" % proc.stdout.strip()[-800:].replace("\n",
                                                                  "\n      "))
    return proc


def _pytest(cwd, selector, verbose=False):
    return _run([sys.executable, "-m", "pytest", selector,
                 "-p", "no:cacheprovider", "-q", "--no-header"],
                cwd, verbose)


def _build(cwd, verbose=False):
    return _run([sys.executable, "scripts/build_audit_index.py", "--write"],
                cwd, verbose)


def stage(into: pathlib.Path, verbose=False) -> pathlib.Path:
    """Copy the needed slice of the repository into `into`, as a git repo."""
    for item in COPY:
        source = ROOT / item
        target = into / item
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)

    listing = _run(["git", "ls-files", "--", AUDIT], ROOT, verbose)
    assert listing.returncode == 0, listing.stderr
    tracked = [line.strip() for line in listing.stdout.splitlines()
               if line.strip()]
    assert len(tracked) > 50, "only %d tracked paths under %s; refusing to " \
        "prove anything over that" % (len(tracked), AUDIT)
    for relative in tracked:
        target = into / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, target)

    _run(["git", "init", "-q"], into, verbose)
    _run(["git", "config", "user.email", "scratch@invalid"], into, verbose)
    _run(["git", "config", "user.name", "scratch"], into, verbose)
    _run(["git", "add", "-A"], into, verbose)
    return into


def assert_the_copy_is_what_ran(scratch: pathlib.Path) -> None:
    """ASSERT, do not confirm, that pytest loaded the copy and not the repo.

    The register's proof step requires this and says why: "confirm" is
    something a person does with their eyes, and an eye that has already
    decided the copy is in use will read the path as the copy's. So the check
    is a comparison the interpreter makes, in the scratch tree's own
    interpreter, and a mismatch aborts before a single byte is mutated.
    """
    probe = (
        "import pathlib, sys; sys.path.insert(0, 'scripts'); "
        "import build_audit_index as bai; "
        "print(pathlib.Path(bai.__file__).resolve())"
    )
    proc = _run([sys.executable, "-c", probe], scratch)
    seen = pathlib.Path(proc.stdout.strip())
    expected = (scratch / "scripts" / "build_audit_index.py").resolve()
    assert seen == expected, (
        "the scratch interpreter loaded %s, not %s -- ABORTING before any "
        "mutation" % (seen, expected)
    )
    assert ROOT not in seen.parents, (
        "the scratch interpreter resolved into the LIVE repository (%s) -- "
        "ABORTING" % seen
    )


# --------------------------------------------------------------------------
# The mutations
# --------------------------------------------------------------------------

def _mutate_append_a_line(scratch):
    path = scratch / "_audit" / "INDEX.md"
    before = path.read_text(encoding="utf-8")
    path.write_text(before + "\nA line nobody derived.\n",
                    encoding="utf-8", newline="\n")
    return lambda: path.write_text(before, encoding="utf-8", newline="\n")


def _mutate_drop_a_line(scratch):
    path = scratch / "_audit" / "INDEX.md"
    before = path.read_text(encoding="utf-8")
    lines = before.split("\n")
    del lines[40]
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return lambda: path.write_text(before, encoding="utf-8", newline="\n")


def _mutate_flip_one_count(scratch):
    """Bump the corpus-size cell by one, found by pattern rather than pinned.

    The literal row text was hardcoded here once and went stale the same hour
    somebody renamed the column, at which point the mutation silently applied
    nothing and the run reported a clean red it had not caused. Hence the
    assertion below: a mutation that does not change the file is a proof of
    nothing, and it must say so rather than pass.
    """
    path = scratch / "_audit" / "INDEX.md"
    before = path.read_text(encoding="utf-8")
    row = re.compile(r"^(\| audit documents git tracks[^|]*\| )(\d+)( \|)$",
                     re.MULTILINE)
    found = row.search(before)
    assert found is not None, ("no corpus-size row in the generated index; "
                              "this mutation is vacuous")
    after = row.sub(
        lambda m: "%s%d%s" % (m.group(1), int(m.group(2)) + 1, m.group(3)),
        before, count=1)
    assert after != before, "the count row did not move; this is vacuous"
    path.write_text(after, encoding="utf-8", newline="\n")
    return lambda: path.write_text(before, encoding="utf-8", newline="\n")


def _mutate_add_a_document(scratch):
    path = scratch / "_audit" / "2026-12-31-a-document-nobody-indexed.md"
    path.write_text("# A document nobody indexed\n\nBody.\n",
                    encoding="utf-8", newline="\n")
    _run(["git", "add", "--", str(path.relative_to(scratch).as_posix())],
         scratch)

    def restore():
        _run(["git", "rm", "-q", "-f", "--",
              path.relative_to(scratch).as_posix()], scratch)
        if path.exists():
            path.unlink()
    return restore


def _mutate_edit_a_title(scratch):
    path = scratch / "_audit" / "2026-08-22-parity-linkedin.md"
    before = path.read_text(encoding="utf-8")
    after = before.replace("# LinkedIn parity", "# LinkedIn parity, retitled", 1)
    assert after != before, "the title moved; this mutation is vacuous"
    path.write_text(after, encoding="utf-8", newline="\n")
    return lambda: path.write_text(before, encoding="utf-8", newline="\n")


def _mutate_declare_a_correction(scratch):
    """The one that matters most: the CORRECTION GRAPH going stale."""
    one = scratch / "_audit" / "2026-08-22-parity-linkedin.md"
    two = scratch / "_audit" / "2026-08-25-cannot-vs-will-not.md"
    before_one = one.read_text(encoding="utf-8")
    before_two = two.read_text(encoding="utf-8")
    one.write_text(
        before_one
        + "\n**CORRECTED BY:** `_audit/2026-08-25-cannot-vs-will-not.md` -- "
          "a correction planted by the red proof, never committed.\n",
        encoding="utf-8", newline="\n")
    two.write_text(
        before_two
        + "\n**CORRECTS:** `_audit/2026-08-22-parity-linkedin.md` -- "
          "a correction planted by the red proof, never committed.\n",
        encoding="utf-8", newline="\n")

    def restore():
        one.write_text(before_one, encoding="utf-8", newline="\n")
        two.write_text(before_two, encoding="utf-8", newline="\n")
    return restore


def _mutate_gut_the_corpus(scratch):
    """Leave ten documents. The FLOOR must fire rather than the drift check.

    A sweep over almost nothing is the failure this whole repository is
    written against, so the floor is proved separately from the identity.
    """
    keep = 10
    docs = sorted((scratch / "_audit").glob("*.md"))[:keep]
    names = {doc.name for doc in docs}
    removed = []
    for doc in sorted((scratch / "_audit").glob("*.md")):
        if doc.name in names:
            continue
        removed.append((doc, doc.read_bytes()))
        _run(["git", "rm", "-q", "-f", "--",
              doc.relative_to(scratch).as_posix()], scratch)

    def restore():
        for doc, payload in removed:
            doc.write_bytes(payload)
            _run(["git", "add", "--", doc.relative_to(scratch).as_posix()],
                 scratch)
    return restore


MUTATIONS = (
    ("a line appended to the committed index", _mutate_append_a_line, SELECTOR),
    ("a line deleted from the committed index", _mutate_drop_a_line, SELECTOR),
    ("one count flipped by one", _mutate_flip_one_count, SELECTOR),
    ("a document added and not re-indexed", _mutate_add_a_document, SELECTOR),
    ("a title edited and not re-indexed", _mutate_edit_a_title, SELECTOR),
    ("a correction declared and not re-indexed",
     _mutate_declare_a_correction, SELECTOR),
    ("the corpus gutted to ten documents", _mutate_gut_the_corpus,
     FLOOR_SELECTOR),
)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--keep", action="store_true",
                        help="leave the scratch tree on disk for inspection")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)

    holder = tempfile.mkdtemp(prefix="audit-index-redproof-")
    scratch = pathlib.Path(holder) / "tree"
    scratch.mkdir()
    failures = []

    try:
        print("staging a copy at %s" % scratch)
        stage(scratch, args.verbose)
        assert_the_copy_is_what_ran(scratch)
        print("  the scratch interpreter loads the COPY, asserted")

        built = _build(scratch, args.verbose)
        if built.returncode != 0:
            print("FAIL could not build the index in the copy:\n%s"
                  % built.stdout + built.stderr)
            return 1

        opening = _pytest(scratch, SELECTOR, args.verbose)
        if opening.returncode != 0:
            print("FAIL the copy is not green BEFORE any mutation; every red "
                  "below would be meaningless:\n%s" % opening.stdout)
            return 1
        print("  control: the copy is GREEN before any mutation")
        print()

        for label, mutate, selector in MUTATIONS:
            restore = mutate(scratch)
            try:
                proc = _pytest(scratch, selector, args.verbose)
                red = proc.returncode != 0
                right = ("1 failed" in proc.stdout
                         and "error" not in proc.stdout.lower().split("=")[0])
                blob = proc.stdout + proc.stderr
                broken = ("ImportError" in blob or "ModuleNotFoundError" in blob
                          or "INTERNALERROR" in blob or "errors" in
                          proc.stdout.split("\n")[-2:][0].lower())
                ok = red and right and not broken
                print("  %-44s %s" % (label, "RED (as required)" if ok
                                      else "DID NOT CONVICT"))
                if not ok:
                    failures.append((label, proc.returncode, blob[-1200:]))
            finally:
                restore()

        print()
        closing = _pytest(scratch, SELECTOR, args.verbose)
        if closing.returncode != 0:
            print("FAIL the copy is NOT green after restoring; a proof that "
                  "ends red proves nothing about the restore:\n%s"
                  % closing.stdout)
            failures.append(("the closing control run", closing.returncode,
                             closing.stdout[-1200:]))
        else:
            print("  control: the copy is GREEN again after every restore")
    finally:
        if args.keep:
            print("scratch kept at %s" % scratch)
        else:
            shutil.rmtree(holder, ignore_errors=True)

    print()
    if failures:
        for label, code, blob in failures:
            print("FAILED %s (exit %d)\n%s\n" % (label, code, blob))
        print("%d of %d mutations did not convict" % (len(failures),
                                                      len(MUTATIONS)))
        return 1
    print("all %d mutations convicted, and the controls bracket them green"
          % len(MUTATIONS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
