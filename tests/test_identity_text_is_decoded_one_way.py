"""Every reader that matches text against the identity wordlist decodes it ONE
way: UTF-8 when the bytes are valid UTF-8, else cp1252 -- never the locale's.

THE HOLE, MEASURED 2026-10-10. The blob sweep and the pre-commit identity gate
decoded with ``text=True`` and no encoding, i.e. the LOCALE's encoding, which
is cp1252 on the operator's Windows box. 9 of the wordlist's 226 needles hold
non-ASCII characters, and a UTF-8 file carrying one of them was read as
mojibake there -- so those 9 could never match a UTF-8 file at commit time or
at push time. The tracked sweep and ``identity_gate.py`` read UTF-8 with
replacement, which closes that half but turns a cp1252-encoded file's non-ASCII
letters into U+FFFD, so a value saved by a cp1252 tool could never match there.

THIS IS A DELIBERATE BEHAVIOUR CHANGE, ruled by the orchestrator at 13:43:
decode as UTF-8 when valid, else cp1252, in every reader of the wordlist. On
the real tree it changes no verdict (the record shows the sweeps still read
PASS); it makes 9 needles reachable that were not.

AND THE SHAPE PRINTED FOR A HIT. ``redact`` replaced ``[A-Za-z0-9]`` only, so
a hit on a non-ASCII value would have printed that value's accented letters --
and a non-cp1252 character in a hit line could crash the print on a cp1252
console. A shape now carries no letter or digit of any script, and nothing
outside ASCII.

RED FIRST, on the operator's box: the UTF-8 cases below fail on the old blob
sweep and the old pre-commit gate (locale cp1252 there -- a UTF-8 locale would
have read them), the cp1252 cases fail on the old tracked sweep and the old
``identity_gate.py`` (UTF-8 with replacement, on every platform), and the
shape test fails on the old ``redact``. Every needle here is SYNTHETIC and
names no one.
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"

#: Invented for this file, non-ASCII on purpose (o-umlaut, i-diaeresis); it
#: names no one. Written with escapes because tracked files are ASCII.
PLANTED_NON_ASCII = "Qu\u00f6rvex\u00efndale"
LINE = f"a line naming {PLANTED_NON_ASCII} in prose\n"
AS_UTF8 = LINE.encode("utf-8")
AS_CP1252 = LINE.encode("cp1252")

_GIT_ENV = {
    "GIT_AUTHOR_NAME": "fixture",
    "GIT_AUTHOR_EMAIL": "fixture@example.com",
    "GIT_COMMITTER_NAME": "fixture",
    "GIT_COMMITTER_EMAIL": "fixture@example.com",
    "GIT_CONFIG_NOSYSTEM": "1",
}


def _load(name: str, alias: str):
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location(alias, SCRIPTS / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _synthetic(*_a, **_k):
    return {"planted_class": {PLANTED_NON_ASCII}}


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """A git repository with the planted line in BOTH encodings, committed AND
    staged, so every reader -- blob, tracked, index -- has something to read."""
    root = tmp_path / "work"
    root.mkdir()
    env = dict(os.environ)
    env.update(_GIT_ENV)
    for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
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
    (root / "utf8.md").write_bytes(AS_UTF8)
    (root / "cp1252.md").write_bytes(AS_CP1252)
    git("add", "utf8.md", "cp1252.md")
    git("commit", "-q", "--no-verify", "-m", "plant")
    tip = git("rev-parse", "HEAD")
    # Staged as well, for the two commit-time gates: same bytes, new paths.
    (root / "staged_utf8.md").write_bytes(AS_UTF8)
    (root / "staged_cp1252.md").write_bytes(AS_CP1252)
    git("add", "staged_utf8.md", "staged_cp1252.md")
    return root, base, tip


# ---------------------------------------------------------------------------
# The rule itself
# ---------------------------------------------------------------------------


def test_the_rule_reads_utf8_as_utf8_and_anything_else_as_cp1252():
    tracked = _load("sweep_tracked_for_identity", "_tracked_rule")
    assert tracked.decode_text(AS_UTF8) == LINE
    assert tracked.decode_text(AS_CP1252) == LINE
    assert tracked.decode_text(b"one\r\ntwo\rthree") == "one\ntwo\nthree"
    # 0x81 is one of the five bytes cp1252 leaves undefined: replaced, not raised.
    assert tracked.decode_text(b"\xff\x81") == "\u00ff\ufffd"


def test_a_shape_carries_no_letter_of_the_value_and_nothing_outside_ascii():
    tracked = _load("sweep_tracked_for_identity", "_tracked_shape")
    shape = tracked.redact(LINE + " \u2192 \u00e9t\u00e9 42")
    assert shape.isascii(), shape
    assert "\u00f6" not in shape and "\u00ef" not in shape
    want = "x xxxx xxxxxx " + "x" * len(PLANTED_NON_ASCII) + " xx xxxxx"
    assert shape.startswith(want), shape


# ---------------------------------------------------------------------------
# Each reader of the wordlist, on the planted value in both encodings
# ---------------------------------------------------------------------------


def test_the_blob_sweep_catches_the_value_in_utf8_and_in_cp1252(
        repo, monkeypatch, capsys):
    root, base, tip = repo
    sweep = _load("sweep_blobs_for_identity", "_blob_one_way")
    monkeypatch.setattr(sweep, "REPO", root)
    monkeypatch.setattr(sweep, "load_wordlist", _synthetic)
    assert sweep.main(["prog", f"{base}..{tip}"]) == 1
    out = capsys.readouterr().out
    assert "utf8.md:1  [planted_class]" in out, out
    assert "cp1252.md:1  [planted_class]" in out, out
    assert PLANTED_NON_ASCII not in out and out.isascii(), out


def test_the_tracked_sweep_catches_the_value_in_utf8_and_in_cp1252(
        repo, monkeypatch, capsys):
    root, _base, _tip = repo
    tracked = _load("sweep_tracked_for_identity", "_tracked_one_way")
    monkeypatch.setattr(tracked, "REPO", root)
    monkeypatch.setattr(tracked, "tracked", lambda: ["utf8.md", "cp1252.md"])
    monkeypatch.setattr(tracked, "load_wordlist", _synthetic)
    assert tracked.main() == 1
    out = capsys.readouterr().out
    assert "HIT utf8.md:1 [planted_class]" in out, out
    assert "HIT cp1252.md:1 [planted_class]" in out, out
    assert PLANTED_NON_ASCII not in out and out.isascii(), out


def test_the_pre_commit_gate_refuses_the_value_in_utf8_and_in_cp1252(
        repo, monkeypatch, capsys):
    root, _base, _tip = repo
    gate = _load("pre_commit_identity_gate", "_pre_commit_one_way")
    monkeypatch.setattr(gate, "REPO", root)
    monkeypatch.setattr(gate, "_load_wordlist", _synthetic)
    assert gate.main() == 1
    err = capsys.readouterr().err
    assert "staged_utf8.md:1  [planted_class]" in err, err
    assert "staged_cp1252.md:1  [planted_class]" in err, err
    assert PLANTED_NON_ASCII not in err and err.isascii(), err


def test_identity_gate_finds_the_value_in_utf8_and_in_cp1252(repo, monkeypatch):
    root, _base, _tip = repo
    gate = _load("identity_gate", "_identity_gate_one_way")
    monkeypatch.setattr(gate, "REPO", root)

    class Wordlist:
        ALLOWED: set = set()
        load_wordlist = staticmethod(_synthetic)

    for rel in ("staged_utf8.md", "staged_cp1252.md"):
        text = gate.staged_blob(rel)
        assert gate.value_findings(Wordlist, rel, text), rel
