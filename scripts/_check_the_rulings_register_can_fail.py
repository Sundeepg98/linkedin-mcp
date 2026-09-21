"""Red proof: every anchor in the LIVE register is load-bearing, one at a time.

`tests/test_the_rulings_register_is_derived.py` plants its defects in a
SYNTHETIC corpus, which proves the mechanism works. It does not prove that the
34 anchors actually committed are each doing any work. Those are different
claims, and the second is the one a reader of `_audit/RULINGS.md` is relying
on: that if the ruling behind an entry were edited away, this would say so.

So this runs the mutation over the REAL register and the REAL corpus: for each
registered ruling in turn, delete its own words and assert the register
convicts THAT entry by id. An anchor that survives its own ruling's deletion
is an anchor matching something incidental -- boilerplate, a heading that
would still be there, a phrase the document repeats -- and it would keep an
entry green after the ruling it names had gone.

**NOTHING IS MUTATED IN THE TREE.** The corpus is copied to a temp directory
and the mutation is planted in the COPY, which is why this can run while other
waves are writing `_audit/`. `_audit/INSTRUMENTS.md`'s preamble demands the
copy and records the day that rule was violated by mutating a module another
agent held uncommitted work in; the copy here is cheap because the register's
core is a pure function of (register, document list, root) and needs no git.

Run from the repository root::

    venv/Scripts/python.exe scripts/_check_the_rulings_register_can_fail.py

Exit 0 means every anchor was shown to be load-bearing AND the unmutated
control was green. Exit 1 names each anchor that survived its own deletion.
"""

from __future__ import annotations

import pathlib
import shutil
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build_rulings_index as bri  # noqa: E402


def _documents(live: pathlib.Path, root: pathlib.Path) -> list:
    """The GIT-TRACKED corpus, re-rooted onto the copy.

    **IT ASKS GIT ABOUT THE LIVE TREE AND THEN RE-ROOTS, RATHER THAN WALKING
    THE COPY.** A disk walk and `git ls-files` are different corpora, and the
    difference is every untracked file in the working tree. That divergence is
    not theoretical: the first run of this script walked the copy, picked up
    this wave's own uncommitted report, and the control failed on a `RULED:`
    in that report's TITLE -- while `--check`, which asks git, was green at
    the same instant. A red proof that disagrees with the check it is proving
    is measuring a third thing.

    `build_audit_index.tracked_documents` records the same lesson from the
    other side: `_audit/_scratch/` is gitignored, and 37 working notes made a
    check pass locally and fail in a clone at the same SHA.
    """
    return [root / p.relative_to(live) for p in bri.corpus(live)]


def main() -> int:
    live = bri.ROOT
    surviving, convicted = [], 0

    with tempfile.TemporaryDirectory(prefix="rulings-redproof-") as tmp:
        root = pathlib.Path(tmp)
        shutil.copytree(live / "_audit", root / "_audit")
        docs = _documents(live, root)

        # A CONTROL FIRST. Without it, every conviction below is satisfied by
        # a checker that always complains, and the whole run proves nothing.
        control = bri.problems_over(bri.REGISTER, docs, root, bri.NOT_A_RULING)
        if control:
            print("CONTROL FAILED -- the unmutated copy is already red, so no")
            print("conviction below would mean anything. First complaints:")
            for line in control[:5]:
                print("  %s" % line)
            return 1
        print("control: the unmutated copy is GREEN over %d documents"
              % len(docs))
        print("")

        for entry in bri.REGISTER:
            target = root / entry.document
            original = target.read_text(encoding="utf-8")

            # DELETE THE LINES THE ANCHOR SPANS, located with the SAME
            # `flatten` the resolver uses. An earlier version tried to match
            # whole lines against the anchor and could not delete 2 of 34 --
            # a wrapped anchor's first line usually carries text from before
            # the anchor starts, so the line is not a substring of it. That
            # printed as two anchors "surviving", which reads exactly like a
            # real finding and is not one. **The red proof's own bug convicted
            # the register.** Reusing the shipped locator removes the class.
            lines = original.replace("\r\n", "\n").split("\n")
            flat, line_of = bri.flatten(lines)
            needle = " ".join(bri.fold(entry.anchor).split())
            at = flat.find(needle)
            if at == -1:
                surviving.append("%s: the red proof could not locate its own "
                                 "anchor to delete" % entry.id)
                continue
            first, last = line_of[at], line_of[at + len(needle) - 1]
            gutted = [ln for number, ln in enumerate(lines, 1)
                      if not first <= number <= last]
            gutted.insert(first - 1, "<<REMOVED BY RED PROOF>>")

            target.write_text("\n".join(gutted), encoding="utf-8",
                              newline="\n")
            found = bri.problems_over(bri.REGISTER, docs, root,
                                      bri.NOT_A_RULING)
            target.write_text(original, encoding="utf-8", newline="\n")

            named = [f for f in found if entry.id in f]
            if named:
                convicted += 1
                print("KILLED  %-52s %s" % (entry.id, named[0][:70]))
            else:
                surviving.append(
                    "%s: SURVIVED its own deletion -- the anchor matches "
                    "something the ruling does not own" % entry.id)
                print("SURVIVED %-51s <- this anchor certifies nothing"
                      % entry.id)

        # And finish on a clean control, so a botched restore cannot pass as
        # a green run. The mutation loop restores in place; this proves it.
        after = bri.problems_over(bri.REGISTER, docs, root, bri.NOT_A_RULING)
        if after:
            print("")
            print("RESTORE FAILED -- the copy is red after the run; the "
                  "convictions above cannot be trusted.")
            return 1

    print("")
    print("%d of %d anchors shown load-bearing; control green before and "
          "after." % (convicted, len(bri.REGISTER)))
    for line in surviving:
        print("  %s" % line)
    return 1 if surviving else 0


if __name__ == "__main__":
    raise SystemExit(main())
