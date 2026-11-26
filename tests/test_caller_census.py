"""The AST caller census (scripts/caller_census.py) and the deletion it licensed.

READ-CARDS-DELETION (ruled 2026-11-26, registered in integration 4): "the
first lane touching server.py deletes server._read_cards if an AST caller
census shows no caller". Lane infra26 ran the census, found no caller, and
deleted it; its record is _audit/2026-11-26-infra26.md, section 1.

Two halves:

1. THE CONTROLS. A census that cannot convict is not one, so every channel it
   claims -- a bare call, an attribute on each import spelling, getattr, an
   import, a relative import, an unbindable receiver, an unreadable file -- is
   PLANTED in a throwaway package and must be counted; a same-named function
   in another module and a string mention must be listed and NOT counted; and
   a clean package must pass.
2. THE DELETION. On the tracked tree, server._read_cards has no definition and
   no reference by any counted channel. Red on 3c656df (the definition was
   there), green after the deletion.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import caller_census as cc  # noqa: E402

TARGET = "linkedin_server.server"
NAME = "_read_cards"

_SERVER = "def _read_cards():\n    return 1\n"

#: file -> (source, the kinds the census must report for it, counted?)
PLANTS = {
    "direct": ("linkedin_server/server.py",
               _SERVER + "\nasync def caller():\n    return _read_cards()\n",
               {"DIRECT"}, True),
    "passed-as-a-value": ("linkedin_server/server.py",
                          _SERVER + "\nTABLE = {'cards': _read_cards}\n", {"DIRECT"}, True),
    "attribute": ("pkg_user.py",
                  "from linkedin_server import server\n\nserver._read_cards()\n",
                  {"ATTRIBUTE"}, True),
    "attribute-alias": ("pkg_user.py",
                        "import linkedin_server.server as srv\n\nf = srv._read_cards\n",
                        {"ATTRIBUTE"}, True),
    "dotted-chain": ("pkg_user.py",
                     "import linkedin_server.server\n\nf = linkedin_server.server._read_cards\n",
                     {"ATTRIBUTE"}, True),
    "package-chain": ("pkg_user.py",
                      "import linkedin_server\n\nf = linkedin_server.server._read_cards\n",
                      {"ATTRIBUTE"}, True),
    "getattr": ("pkg_user.py",
                "from linkedin_server import server\n\nf = getattr(server, '_read_cards')\n",
                {"GETATTR"}, True),
    "hasattr": ("pkg_user.py",
                "from linkedin_server import server as s\n\nok = hasattr(s, '_read_cards')\n",
                {"GETATTR"}, True),
    "import": ("pkg_user.py",
               "from linkedin_server.server import _read_cards as rc\n\nf = rc\n",
               {"IMPORT", "DIRECT"}, True),
    "relative-import": ("linkedin_server/neighbour.py",
                        "from .server import _read_cards\n", {"IMPORT"}, True),
    "relative-module": ("linkedin_server/neighbour.py",
                        "from . import server\n\nf = server._read_cards\n",
                        {"ATTRIBUTE"}, True),
    "unbindable-receiver": ("pkg_user.py",
                            "import importlib\n\nm = importlib.import_module('x')\n"
                            "f = m._read_cards\n", {"UNRESOLVED"}, True),
    "unreadable-file": ("pkg_user.py", "def broken(:\n", {"PARSE-FAILED"}, True),
    "same-name-elsewhere": ("pkg_user.py",
                            "from linkedin_server import search_vertical_results\n\n"
                            "f = search_vertical_results._read_cards\n", {"OTHER"}, False),
    "string-mention": ("pkg_user.py",
                       "PATH = 'linkedin_server.server._read_cards'\n", {"STRING"}, False),
}


def _plant(tmp_path: Path, rel: str, source: str) -> Path:
    root = tmp_path / "repo"
    (root / "linkedin_server").mkdir(parents=True)
    (root / "linkedin_server" / "__init__.py").write_text("", encoding="utf-8")
    if rel != "linkedin_server/server.py":
        (root / "linkedin_server" / "server.py").write_text(_SERVER, encoding="utf-8")
    (root / rel).write_text(source, encoding="utf-8")
    return root


@pytest.mark.parametrize("plant", sorted(PLANTS))
def test_each_planted_channel_is_reported_and_only_callers_are_counted(tmp_path, plant):
    rel, source, kinds, is_caller = PLANTS[plant]
    root = _plant(tmp_path, rel, source)
    hits, n = cc.census(TARGET, NAME, repo=str(root), tracked=False)
    assert n >= 2
    found = {h.kind for h in hits if h.rel == rel and h.kind != "DEF"}
    assert kinds <= found, (plant, sorted(found), hits)
    assert bool(cc.counted(hits)) is is_caller, (plant, cc.render(hits, n, TARGET, NAME))


def test_THIS_CONTROL_CAN_PASS_a_package_with_no_caller_reads_no_caller(tmp_path):
    root = _plant(tmp_path, "pkg_user.py", "from linkedin_server import server\n\nx = 1\n")
    hits, n = cc.census(TARGET, NAME, repo=str(root), tracked=False)
    assert [h.kind for h in hits] == ["DEF"], hits
    assert cc.counted(hits) == []
    assert cc.render(hits, n, TARGET, NAME).endswith("VERDICT: NO CALLER")


def test_an_extra_root_is_read_too(tmp_path):
    root = _plant(tmp_path, "pkg_user.py", "x = 1\n")
    runner = tmp_path / "runner"
    runner.mkdir()
    (runner / "runner.py").write_text(
        "from linkedin_server import server\n\nserver._read_cards()\n", encoding="utf-8")
    hits, _ = cc.census(TARGET, NAME, repo=str(root), extra=[str(runner)], tracked=False)
    assert [h.rel for h in cc.counted(hits)] == ["extra:runner.py"], hits


def test_the_deleted_card_reader_has_no_definition_and_no_caller():
    hits, n = cc.census(TARGET, NAME, repo=str(REPO))
    assert n > 300, "the census read only %d tracked files" % n
    assert not [h for h in hits if h.kind == "DEF"], (
        "server._read_cards is defined again; READ-CARDS-DELETION removed it\n"
        + cc.render(hits, n, TARGET, NAME))
    assert cc.counted(hits) == [], cc.render(hits, n, TARGET, NAME)
