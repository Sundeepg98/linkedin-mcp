"""``scripts/sweep_blobs_for_identity.py`` reads every blob through ONE
``git cat-file --batch`` process, and matches exactly the text the old
per-blob ``git cat-file -p`` call handed it.

WHY. The sweep used to launch one ``git cat-file -p`` per blob. A launch costs
tens of milliseconds on Windows, so one commit's 997 blobs took 72s and a
3-commit range of 1002 blobs took 217s on a busy box -- and the pre-push gate
runs this sweep on every ``ci/`` push. Measured after the change: about 10s
for the same 3-commit range (``_audit/2026-10-10-lane-ci-fastlane.md``).

WHAT THIS PINS, each on a SYNTHETIC repository in a tmp dir with a synthetic
wordlist (the planted value is invented here and names no one):

* ONE PROCESS. A sweep of several blobs launches ``git cat-file --batch``
  exactly once and ``git cat-file -p`` never. The old loop launched one per
  blob, and that is this file's red run.
* THE SAME BYTES. Blobs built to break a framing or decoding mistake -- CRLF,
  a lone CR, bytes that are not UTF-8, cp1252 punctuation, valid UTF-8, an
  empty blob, one larger than a pipe buffer -- read back from the batch reader
  equal to one ``git cat-file -p`` per blob, both decoded by the sweep's rule.
  (Until the 2026-10-10 decoding ruling the comparison was against the LOCALE
  text the old loop used, and it held byte for byte; the rule itself is
  pinned in ``tests/test_identity_text_is_decoded_one_way.py``.)
* THE SAME REPORT. ``main()``'s whole output over a repository with a planted
  value is identical with the batch reader and with one process per blob
  swapped back in -- and it is a FAIL naming the planted line, so the
  planted-value control still fails.
* A BLOB GIT CANNOT PRODUCE REFUSES (exit 2); it never reads as clean.
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "sweep_blobs_for_identity.py"

PLANTED = "Quorvexindale Plimbury"  # invented; names no one

_GIT_ENV = {
    "GIT_AUTHOR_NAME": "fixture",
    "GIT_AUTHOR_EMAIL": "fixture@example.com",
    "GIT_COMMITTER_NAME": "fixture",
    "GIT_COMMITTER_EMAIL": "fixture@example.com",
    "GIT_CONFIG_NOSYSTEM": "1",
}

#: Each one chosen to make a decoding or framing mistake visible.
BLOBS = {
    "crlf.txt": b"first line\r\nsecond line\r\n",
    "lone_cr.txt": b"one\rtwo\rthree",
    "not_utf8.txt": b"bytes \xff\xfe\xfd that no utf-8 decoder accepts\n",
    "cp1252.txt": b"\x93quoted\x94 and \x85 an ellipsis\n",
    "utf8.txt": b"caf\xc3\xa9 na\xc3\xafve \xe2\x80\x93 dash\n",  # valid utf-8
    "empty.txt": b"",
    "big.txt": (b"0123456789abcdef" * 64 + b"\n") * 300,  # ~300 KB
    "planted.md": f"line one\r\na line naming {PLANTED} in prose\r\n".encode(),
}


def _load():
    spec = importlib.util.spec_from_file_location(
        "_sweep_blobs_one_process_under_test", SCRIPT)
    assert spec is not None and spec.loader is not None, SCRIPT
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def repo(tmp_path, monkeypatch):
    root = tmp_path / "work"
    root.mkdir()
    env = dict(os.environ)
    env.update(_GIT_ENV)
    for name in ("GIT_DIR", "GIT_WORK_TREE"):
        monkeypatch.delenv(name, raising=False)
        env.pop(name, None)

    def git(*args: str) -> str:
        out = subprocess.run(
            ["git", "-c", "core.autocrlf=false", "-c", "core.hooksPath=.nohooks",
             "-c", "commit.gpgsign=false", *args],
            cwd=root, capture_output=True, text=True, env=env, timeout=60)
        assert out.returncode == 0, (args, out.stderr)
        return out.stdout.strip()

    git("init", "-q", "-b", "master")
    (root / "base.txt").write_bytes(b"the published history\n")
    git("add", "base.txt")
    git("commit", "-q", "--no-verify", "-m", "base")
    base = git("rev-parse", "HEAD")
    for name, data in BLOBS.items():
        (root / name).write_bytes(data)
        git("add", name)
    git("commit", "-q", "--no-verify", "-m", "the blobs")
    tip = git("rev-parse", "HEAD")
    shas = {name: git("rev-parse", f"HEAD:{name}") for name in BLOBS}
    return root, base, tip, shas


def _aim(module, monkeypatch, root: Path) -> None:
    monkeypatch.setattr(module, "REPO", root)
    monkeypatch.setattr(module, "load_wordlist",
                        lambda: {"planted_class": {PLANTED}})


def _old_text(module, root: Path, sha: str) -> str:
    """One ``git cat-file -p`` per blob -- the old loop's framing -- decoded
    by the sweep's own rule. (Until 2026-10-10 the comparison was against the
    LOCALE decoding the old loop used; the rule then changed deliberately,
    ``tests/test_identity_text_is_decoded_one_way.py``, and this file pins the
    FRAMING: one process hands over the bytes N processes did.)"""
    raw = subprocess.run(["git", "cat-file", "-p", sha], cwd=root,
                         capture_output=True).stdout
    return module.decode_text(raw)


def test_a_sweep_launches_one_cat_file_process_not_one_per_blob(
        repo, monkeypatch, capsys):
    root, base, tip, _shas = repo
    module = _load()
    _aim(module, monkeypatch, root)
    launched: list[list[str]] = []
    real = subprocess.Popen

    class Counting(real):  # type: ignore[misc, valid-type]
        def __init__(self, args, *a, **k):
            launched.append([str(x) for x in args])
            super().__init__(args, *a, **k)

    monkeypatch.setattr(subprocess, "Popen", Counting)
    assert module.main(["prog", f"{base}..{tip}"]) == 1
    capsys.readouterr()
    cat_files = [a[1:] for a in launched if "cat-file" in a]
    assert cat_files == [["cat-file", "--batch"]], (
        f"{len(cat_files)} cat-file launch(es) for {len(BLOBS) + 1} blobs: "
        f"{cat_files[:3]}")


def test_the_batch_reader_hands_over_the_text_cat_file_p_did(repo, monkeypatch):
    root, _base, _tip, shas = repo
    module = _load()
    monkeypatch.setattr(module, "REPO", root)
    reader = module._BlobReader()
    try:
        for name, sha in shas.items():
            assert reader.read(sha) == _old_text(module, root, sha), name
    finally:
        reader.close()


def test_the_report_is_identical_and_the_planted_value_still_fails(
        repo, monkeypatch, capsys):
    root, base, tip, _shas = repo
    module = _load()
    _aim(module, monkeypatch, root)

    assert module.main(["prog", f"{base}..{tip}"]) == 1
    batch = capsys.readouterr().out

    class PerBlob:
        """The old loop's framing -- one process per blob -- swapped back in."""

        def read(self, sha):
            return _old_text(module, root, sha)

        def close(self):
            pass

    monkeypatch.setattr(module, "_BlobReader", PerBlob)
    assert module.main(["prog", f"{base}..{tip}"]) == 1
    per_blob = capsys.readouterr().out

    assert batch == per_blob
    assert "FAIL: 1 hit(s) in 1 distinct path(s)." in batch, batch
    assert "planted.md:2  [planted_class]" in batch, batch
    assert PLANTED not in batch, "the sweep printed the value it was hunting"


def test_a_blob_git_cannot_produce_refuses_rather_than_passes(
        repo, monkeypatch, capsys):
    root, base, tip, _shas = repo
    module = _load()
    _aim(module, monkeypatch, root)
    absent = "0123456789abcdef0123456789abcdef01234567"

    def fake_git(*args, **kwargs):
        if args[0] == "rev-list":
            return tip + "\n"
        if args[0] == "ls-tree":
            return f"100644 blob {absent}\tghost.txt\n"
        raise AssertionError(f"unexpected git {args!r}")

    monkeypatch.setattr(module, "_git", fake_git)
    assert module.main(["prog", "fake-range"]) == 2
    out = capsys.readouterr().out
    assert "REFUSING TO SWEEP" in out and "cat-file --batch" in out, out
    assert "PASS" not in out, out


def test_closing_a_reader_that_never_read_launches_nothing(monkeypatch):
    """Started on first read: a sweep that refuses before its loop -- every
    zero case -- must not leave a git process behind, or start one."""
    module = _load()
    launched = []
    real = subprocess.Popen

    class Counting(real):  # type: ignore[misc, valid-type]
        def __init__(self, args, *a, **k):
            launched.append(args)
            super().__init__(args, *a, **k)

    monkeypatch.setattr(subprocess, "Popen", Counting)
    module._BlobReader().close()
    assert launched == []
