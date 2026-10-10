"""Sweep every git-tracked file for the REAL strings, in all their spellings.

WHY THIS IS A SCRIPT AND NOT A TEST. It needs the real values, and the real
values are the key to the committed fixtures -- so they live in
``_audit/_sanitisation_key.json``, which is gitignored. A test that needed
that file would either embed the values (which is the leak) or skip when they
are absent (and a skipping guard is a dead guard, certifying nothing on every
machine that lacks the file, including CI).

So the division is deliberate:

* ``tests/test_no_committed_identity.py`` is TRACKED and always runs. It hunts
  what needs no real values: the SHAPE OF A KEY -- a table pairing fixture
  content with something absent from every fixture -- and opaque LinkedIn ids
  across the whole repo.
* this script is TRACKED, its WORDLIST never is, and it hunts the exact
  values. It is the only thing that can catch an employer's campus name in a
  comment, because nothing structural distinguishes that from English.

WHAT IT CHECKS THAT A LITERAL LIST DOES NOT. Every value is expanded through
``tests.leakwalk.url_spellings`` before the sweep. A committed fixture leaked a
real job title past a check reporting ``69/69 forbidden strings absent``,
because the list held the spaced spelling and the file used the hyphenated
one. A LIST OF LITERALS ONLY CATCHES THE SPELLING SOMEBODY TYPED.

WHAT IT DOES NOT DO: print the values it is hunting. A sweep that echoes its
own wordlist into a terminal, a log or a CI transcript has published the key
in a new place. Findings are reported as ``file:line [class]`` with the
matched line REDACTED to its shape.

Usage:
    python scripts/sweep_tracked_for_identity.py            # sweep, exit 1 on a hit
    python scripts/sweep_tracked_for_identity.py --show     # ...and show the line
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tests.leakwalk import url_spellings  # noqa: E402
from tests.repo_paths import sanitisation_key_path  # noqa: E402

#: RESOLVED THROUGH :mod:`tests.repo_paths` SINCE 2026-09-19. This was
#: ``REPO / "_audit" / "_sanitisation_key.json"``, and in a linked worktree
#: that path cannot exist: git populates a worktree from the index and the key
#: is gitignored, so it stays behind in the main checkout. The sweep then
#: exited with "the wordlist is missing" and the pre-commit gate printed
#: "identity wordlist absent; ALLOWING" -- on the operator's own machine, with
#: the key on the same disk.
KEY_PATH = sanitisation_key_path(REPO)

#: Files that must be allowed to name real strings, by EXACT repo-relative
#: path, because a denylist has to name what it denies. There is no way to
#: write those tests without the string; moving them to hashes would buy
#: obscurity rather than secrecy, since they are dictionary words already
#: present in this repository's history.
ALLOWED = {
    "tests/test_sdui_surfaces_fixture.py",
    "scripts/_build_follow_fixtures.py",
    "scripts/sweep_tracked_for_identity.py",
}

#: A short value matches everything. The key holds a few of these (initials,
#: a five-character company name) and sweeping on them is noise, not signal.
MIN_LENGTH = 5


def tracked() -> list[str]:
    proc = subprocess.run(
        ["git", "ls-files"], cwd=str(REPO), capture_output=True, text=True
    )
    if proc.returncode != 0:
        raise SystemExit(f"git ls-files failed: {proc.stderr}")
    return [line for line in proc.stdout.splitlines() if line.strip()]


def load_wordlist() -> dict[str, set[str]]:
    """Real values by class, each expanded into its url and slug spellings."""
    if not KEY_PATH.exists():
        raise SystemExit(
            f"the wordlist is missing: {KEY_PATH}\n"
            "It is gitignored on purpose -- it is the de-anonymisation key for\n"
            "the committed fixtures, and this sweep is the one thing that reads\n"
            "it. Without it the exact-value half of the guard cannot run. The\n"
            "shape half, tests/test_no_committed_identity.py, runs regardless\n"
            "and needs nothing."
        )
    raw = json.loads(KEY_PATH.read_text(encoding="utf-8"))

    # Values too common in ordinary English, or in a Windows path, to sweep
    # for. The list lives in the KEY rather than here for the same reason the
    # key does: an exemption has to name the value it exempts, so writing it
    # in this tracked file would put the value back in the repo. Measured
    # rather than guessed -- each entry earned its place by matching a file
    # that has nothing to do with him.
    ignored = {
        str(v).casefold()
        for v in (raw.get("_ignore_values") or {}).get("values", [])
    }

    out: dict[str, set[str]] = {}
    for name, values in raw.items():
        if name.startswith("_") or not isinstance(values, list):
            continue
        spellings: set[str] = set()
        for value in values:
            for item in value if isinstance(value, list) else [value]:
                if not isinstance(item, str) or len(item) < MIN_LENGTH:
                    continue
                if item.casefold() in ignored:
                    continue
                spellings |= url_spellings(item)
        out[name] = {
            s for s in spellings
            if len(s) >= MIN_LENGTH and s.casefold() not in ignored
        }
    return out


def decode_text(data: bytes) -> str:
    """THE ONE WAY text is read before it is matched against the wordlist.

    UTF-8 when the bytes are valid UTF-8; otherwise cp1252, with replacement
    for the five bytes cp1252 leaves undefined. Universal newlines after, as
    every reader here applied before.

    NEVER THE LOCALE'S ENCODING, and that is the change, made 2026-10-10 on the
    orchestrator's ruling. The blob sweep and the pre-commit gate decoded with
    ``text=True`` and no encoding, which on the operator's Windows box is
    cp1252: 9 of the 226 needles hold non-ASCII letters, and a UTF-8 file
    carrying one was read as mojibake there, so those 9 could never match at
    commit or push time. This sweep and ``identity_gate.py`` read UTF-8 with
    replacement, which turned a cp1252 file's non-ASCII letters into U+FFFD,
    so a value saved by a cp1252 tool could never match here. Every reader of
    the wordlist now calls this, so the four of them read one text.
    """
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        text = data.decode("cp1252", errors="replace")
    return text.replace("\r\n", "\n").replace("\r", "\n")


def redact(line: str) -> str:
    """The line's SHAPE, never its content.

    Every letter and digit IN ANY SCRIPT becomes ``x`` (it was ``[A-Za-z0-9]``
    until 2026-10-10, which would have printed the accented letters of a
    non-ASCII value once ``decode_text`` let those values match), and anything
    else outside ASCII becomes ``?`` -- so a shape carries no letter of the
    value and prints on any console, a cp1252 one included.
    """
    shape = re.sub(r"[^\W_]", "x", line.strip())
    return shape.encode("ascii", "replace").decode("ascii")[:70]


def main() -> int:
    show = "--show" in sys.argv
    wordlist = load_wordlist()
    total = sum(len(v) for v in wordlist.values())
    files = tracked()
    print(f"sweeping {len(files)} tracked files for {total} spellings "
          f"across {len(wordlist)} classes")

    hits = 0
    for rel in files:
        if rel in ALLOWED:
            continue
        path = REPO / rel
        try:
            lines = decode_text(path.read_bytes()).splitlines()
        except OSError:
            continue
        lowered = [line.lower() for line in lines]
        for name, spellings in wordlist.items():
            for spelling in spellings:
                needle = spelling.lower()
                for number, line in enumerate(lowered, 1):
                    if needle in line:
                        hits += 1
                        rendered = lines[number - 1].strip() if show else redact(
                            lines[number - 1]
                        )
                        print(f"  HIT {rel}:{number} [{name}]  {rendered}")
                        break

    if hits:
        print(f"\nFAIL: {hits} hit(s). Every one is a real string in a tracked file.")
        return 1
    print(f"\nPASS: 0 hits across {len(files) - len(ALLOWED)} swept files.")
    print(f"      {len(ALLOWED)} allowed by exact path (denylists, and this file).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
