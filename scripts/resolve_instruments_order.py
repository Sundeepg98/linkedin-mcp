"""Resolve an INSTRUMENTS.md conflict where both sides APPENDED sections: keep both, in section-number order.

usage:
    python scripts/resolve_instruments_order.py [--file PATH] [--main-checkout]

Takes the single conflict hunk and cuts both sides into SECTIONS: a '## N.' heading starts one anywhere
in a block, and a '### N.M' heading starts one only before the block's first '## N.' (a subsection the
lane appended to the section above the hunk). Every other line stays with the section it follows, so a
subsection stays under the section its author wrote it in, whatever its number says. The sections of
both sides are written back in number order, one blank line apart. Text before a block's first numbered
heading continues the section above the hunk, so it is written first.

It refuses, and writes nothing, if there is not exactly one hunk, if a block has no numbered heading, or
if a section number is claimed twice in the hunk or is already used outside it. That refusal names the
next free section number: renumber the later section in the conflict and run again.

SECTION ORDER (lane hygiene28, 2026-11-28). Until then the two BLOCKS were ordered by their first
heading. One side holding 114 and 117 against the other's 116 was written 114, 117, 116, and integration
7 split the sections by hand (merge notes, 2026-11-27 18:36). Two sides claiming one number were written
side by side, and the duplicate was found later or not at all.

WHICH FILE IT EDITS (lane hygiene28, 2026-11-28)
* ``--file PATH`` edits exactly PATH.
* With no ``--file`` it edits ``_audit/INSTRUMENTS.md`` under the git root it is RUN FROM
  (``git rev-parse --show-toplevel`` in the current directory), never under the tree it is STORED in.
* It names the file, and which checkout holds it, on its first two lines.
* A file the MAIN checkout holds is refused unless ``--main-checkout`` is passed. The flag only
  permits; it never chooses the main checkout's file. ``merge_wave.py`` resolves the main checkout's
  merge, so it passes the flag; an integrator in a worktree never needs it.

WHY. Until 2026-11-28 this tool lived only in the main checkout's gitignored
``_state/orchestrator-tools/`` and found its file from its own location
(``Path(__file__).resolve().parents[2]``). So whatever directory it was run from, it edited the MAIN
checkout's INSTRUMENTS.md, and it took no arguments. The merge notes record that hazard twice
(integration 6, 2026-11-27); integrator6 pointed it at its own worktree's file by hand, and every
integrator brief had to repeat the warning.

HOW THE MAIN CHECKOUT IS TOLD APART. Git is asked about the FILE's directory, not the caller's: the
file's own work tree (``--show-toplevel``) is compared with the main worktree, the first entry of
``git worktree list``. A path prefix cannot do it, because the worktrees on the operator's box sit
INSIDE the main checkout's directory. Two more ways a worktree path can still be the main checkout's
file are closed:
* the path is resolved first, and the file is also compared, by identity, with the main checkout's
  ``_audit/INSTRUMENTS.md``, so a hardlink, junction or symlink to it is refused;
* git runs with the variables that redirect discovery removed (GIT_DIR, GIT_WORK_TREE and their
  kin), so a hook's environment cannot make git place the file in another repository.
When a ``.git`` sits above the file and git still cannot place it, the file is treated as the main
checkout's: refused unless ``--main-checkout``. A file with no ``.git`` anywhere above it is in no
checkout, and is edited.

EXIT CODES. 0 resolved and written; 1 not resolvable (not exactly one hunk, or a block with no
numbered heading); 2 refused (no such file, no git root to default from, or the main checkout's file
without the flag). Nothing is written unless the code is 0. On 1 or 2 everything, the two naming
lines included, goes to stderr, so a caller that prints ``stdout or stderr`` shows the reason.
"""
from __future__ import annotations

import argparse
import os
import pathlib
import re
import subprocess
import sys

INSTRUMENTS = pathlib.PurePosixPath("_audit", "INSTRUMENTS.md")

#: Variables that move git's repository discovery away from the directory it is run in.
_REDIRECTING = ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE",
                "GIT_OBJECT_DIRECTORY", "GIT_CEILING_DIRECTORIES",
                "GIT_DISCOVERY_ACROSS_FILESYSTEM")

_HUNK = re.compile(r"^<<<<<<< [^\n]*\n(.*?)^=======\n(.*?)^>>>>>>> [^\n]*\n", flags=re.S | re.M)
_SECTION = re.compile(r"^## (\d+)(?:\.(\d+))?", flags=re.M)
_SUBSECTION = re.compile(r"^### (\d+)(?:\.(\d+))?", flags=re.M)


class Refused(Exception):
    """Nothing was written; the message says why."""

    def __init__(self, message: str, code: int) -> None:
        super().__init__(message)
        self.code = code


def _git(where: pathlib.Path, *args: str) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k.upper() not in _REDIRECTING}
    return subprocess.run(["git", "-C", str(where), *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", env=env)


def _same(a: pathlib.Path, b: pathlib.Path) -> bool:
    try:
        return os.path.samefile(a, b)
    except OSError:
        return os.path.normcase(os.path.realpath(a)) == os.path.normcase(os.path.realpath(b))


def default_target(cwd: pathlib.Path) -> pathlib.Path:
    """``_audit/INSTRUMENTS.md`` under the git root of ``cwd``."""
    top = _git(cwd, "rev-parse", "--show-toplevel")
    if top.returncode:
        raise Refused("no --file was given, and the current directory is not inside a git work "
                      "tree to default from (" + top.stderr.strip() + "). Pass --file.", 2)
    return pathlib.Path(top.stdout.strip(), *INSTRUMENTS.parts)


def checkout_of(path: pathlib.Path) -> tuple[str, str]:
    """('main' | 'linked' | 'none' | 'unknown', an account of the reading) for an existing file."""
    real = pathlib.Path(os.path.realpath(path))
    where = real.parent
    if not any((d / ".git").exists() for d in (where, *where.parents)):
        return "none", "no git work tree (no .git above it)"
    try:
        top = _git(where, "rev-parse", "--show-toplevel")
        listing = _git(where, "worktree", "list", "--porcelain")
    except OSError as exc:
        return "unknown", f"git could not run ({exc})"
    if top.returncode or listing.returncode:
        return "unknown", "git could not place it: " + (top.stderr or listing.stderr).strip()
    own = pathlib.Path(top.stdout.strip())
    first = listing.stdout.split("\n\n", 1)[0].splitlines()
    main = None
    if first and first[0].startswith("worktree ") and "bare" not in first[1:]:
        main = pathlib.Path(first[0][len("worktree "):])
    if main is not None and _same(own, main):
        return "main", f"the MAIN checkout ({main})"
    if main is not None:
        theirs = main.joinpath(*INSTRUMENTS.parts)
        if theirs.exists() and _same(real, theirs):
            return "main", (f"the MAIN checkout's {INSTRUMENTS}, reached from {own} through a link "
                            f"or another name")
    return "linked", f"a linked worktree ({own})"


def _sections(block: str) -> tuple[str, list[tuple[str, tuple[int, int], str]]]:
    """(the block's text before its first numbered heading, and its sections as
    (level, (number, sub-number), text))."""
    first = _SECTION.search(block)
    cut = first.start() if first else len(block)
    starts = sorted(list(_SUBSECTION.finditer(block, 0, cut)) + list(_SECTION.finditer(block)),
                    key=lambda found: found.start())
    if not starts:
        raise Refused("a block has no numbered heading; resolve by hand", 1)
    sections = []
    for i, found in enumerate(starts):
        end = starts[i + 1].start() if i + 1 < len(starts) else len(block)
        level = "##" if found.re is _SECTION else "###"
        key = (int(found.group(1)), int(found.group(2) or 0))
        sections.append((level, key, block[found.start():end]))
    return block[: starts[0].start()], sections


def _name(level: str, key: tuple[int, int]) -> str:
    return f"{key[0]}.{key[1]}" if level == "###" or key[1] else str(key[0])


def _spaced(piece: str, last: bool) -> str:
    """The piece ending in one newline if it is the hunk's last, else in one blank line."""
    return piece.rstrip("\n") + ("\n" if last else "\n\n")


def resolve(text: str) -> tuple[str, list[tuple[int, int]]]:
    """The text with its one hunk resolved, and the order it was written in."""
    hunks = list(_HUNK.finditer(text))
    if len(hunks) != 1:
        raise Refused(f"expected exactly 1 conflict hunk, found {len(hunks)}", 1)
    hunk = hunks[0]
    prefixes, sections = [], []
    for block in (hunk.group(1), hunk.group(2)):
        prefix, found = _sections(block)
        prefixes.append(prefix)
        sections.extend(found)

    outside = text[: hunk.start()] + text[hunk.end():]
    used = {("##", (int(n), int(m or 0))) for n, m in _SECTION.findall(outside)}
    used_numbers = {key[0] for _level, key in used}
    used |= {("###", (int(n), int(m or 0))) for n, m in _SUBSECTION.findall(outside)}
    claimed = [(level, key) for level, key, _text in sections]
    twice = sorted({c for c in claimed if claimed.count(c) > 1}, key=lambda c: c[1])
    taken = sorted({c for c in claimed if c in used or (c[0] == "##" and c[1][0] in used_numbers)},
                   key=lambda c: c[1])
    if twice or taken:
        numbers = used_numbers | {key[0] for level, key in claimed if level == "##"}
        said = []
        if twice:
            said.append("claimed twice in the hunk: " + ", ".join(_name(*c) for c in twice))
        if taken:
            said.append("already used outside the hunk: " + ", ".join(_name(*c) for c in taken))
        raise Refused("section number " + "; ".join(said) + ". Renumber the later section in the "
                      f"conflict and run again; the next free section number is "
                      f"{max(numbers, default=0) + 1}.",
                      1)

    ordered = sorted(sections, key=lambda section: section[1])
    pieces = [prefix for prefix in prefixes if prefix.strip()] + [s[2] for s in ordered]
    merged = "".join(_spaced(piece, i == len(pieces) - 1) for i, piece in enumerate(pieces))
    return text[: hunk.start()] + merged + text[hunk.end():], [s[1] for s in ordered]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--file", help="the INSTRUMENTS.md to edit (default: _audit/INSTRUMENTS.md "
                                       "under the git root of the current directory)")
    parser.add_argument("--main-checkout", action="store_true",
                        help="permit editing a file the MAIN checkout holds")
    args = parser.parse_args(argv)
    lines: list[str] = []
    try:
        target = (pathlib.Path(os.path.abspath(args.file)) if args.file
                  else default_target(pathlib.Path.cwd()))
        lines.append(f"target: {target}")
        if not target.is_file():
            raise Refused("no such file", 2)
        kind, account = checkout_of(target)
        lines.append(f"held by: {account}")
        if kind in ("main", "unknown") and not args.main_checkout:
            raise Refused(
                "this is the main checkout's file, or git could not say it is not. Run the tool from "
                "the worktree whose INSTRUMENTS.md it should edit, or name that file with --file. "
                "To edit the main checkout's file on purpose (merge_wave.py does), pass "
                "--main-checkout.", 2)
        resolved, order = resolve(target.read_text(encoding="utf-8"))
    except Refused as refused:
        print("\n".join(lines + [f"refused: {refused}"]), file=sys.stderr)
        return refused.code
    target.write_text(resolved, encoding="utf-8", newline="\n")
    print("\n".join(lines + [f"resolved: order {order}"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
