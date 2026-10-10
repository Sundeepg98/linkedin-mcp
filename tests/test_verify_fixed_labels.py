"""``scripts/verify_fixed_labels.py``: a fixed label read off a KEYED skeleton, from a closed vocabulary only.

Each test plants a skeleton written the way the live lane writes one -- every
value that is not LinkedIn's kept word replaced by
``_probe_live_lane_session_2.value_shape`` under a key -- and reads it back
with the instrument. Shown failing, which is what lets it into the register:

* THE KEY DECIDES IT. The same skeleton read with another key counts 0 for
  every shaped label and still counts the verbatim one -- so a count above 0
  is a measurement, not an artefact of the reader.
* AN EXACT CHECK. A decorated label (``School (3)``) is neither counted as
  ``School`` nor hidden: it counts 0, which the instrument's own output says
  it cannot read as absence.
* NO LABEL FROM A CALLER. The parser takes a skeleton and a key and nothing
  else; a label is a literal of the module.
* NOTHING OF THE PAGE, NO HASH, NO KEY in what it prints.

Nothing here reaches LinkedIn, an account, a browser or another worktree.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import verify_fixed_labels as vfl  # noqa: E402
from _probe_live_lane_session_2 import value_shape  # noqa: E402

KEY = bytes(range(32))
OTHER_KEY = bytes(range(1, 33))


def _skeleton(key: bytes) -> str:
    """A small skeleton: a menu with a verbatim Save, a shaped Not interested,
    a shaped Report post on an aria-label, a decorated School, and a shaped
    value that is nobody's label."""
    shaped = lambda text: value_shape(text, key)  # noqa: E731
    return "\n".join((
        "<!doctype html>",
        '<div role="menu">',
        '<div role="menuitem"><p>Save</p></div>',
        '<div role="menuitem"><p>%s</p></div>' % shaped("Not interested"),
        '<a role="menuitem" aria-label="%s" href="https://www.linkedin.com/feed/"></a>' % shaped("Report post"),
        "</div>",
        '<label for="%s">%s</label>' % (shaped("filter-1"), shaped("School (3)")),
        "<p>%s</p>" % shaped("Somebody Example"),
    ))


def test_a_planted_label_is_counted_verbatim_and_by_keyed_shape():
    counts = vfl.count_labels(_skeleton(KEY), KEY)
    assert counts["Save"] == 1
    assert counts["Not interested"] == 1
    assert counts["Report post"] == 1
    assert counts["Embed this post"] == 0


def test_the_key_decides_it_another_key_counts_only_the_verbatim_word():
    counts = vfl.count_labels(_skeleton(KEY), OTHER_KEY)
    assert counts["Not interested"] == 0
    assert counts["Report post"] == 0
    assert counts["Save"] == 1


def test_a_decorated_label_is_not_counted_as_the_bare_one():
    counts = vfl.count_labels(_skeleton(KEY), KEY)
    assert counts["School"] == 0


def test_no_argument_takes_a_label():
    options = {
        option
        for action in vfl.build_parser()._actions
        for option in action.option_strings
    }
    assert options == {"-h", "--help", "--skeleton", "--key"}


def test_every_vocabulary_label_is_a_short_ascii_interface_string():
    flat = vfl.labels()
    assert len(flat) == len(set(flat))
    for label in flat:
        assert label.isascii() and label.strip() == label and 1 <= len(label) <= 40


def test_the_output_carries_no_hash_no_key_and_nothing_of_the_page(tmp_path, capsys):
    skeleton = tmp_path / "planted.skeleton.html"
    skeleton.write_text(_skeleton(KEY), encoding="utf-8")
    key = tmp_path / "shape.key"
    key.write_text(KEY.hex(), encoding="utf-8")
    assert vfl.main(["--skeleton", str(skeleton), "--key", str(key)]) == 0
    printed = capsys.readouterr().out
    assert re.search(r"[0-9a-f]{8}", printed) is None
    assert KEY.hex() not in printed
    assert "Somebody" not in printed and "filter-1" not in printed
    assert "Not interested" in printed and "NOT SAID" in printed


def test_an_unreadable_key_is_refused_without_quoting_it(tmp_path, capsys):
    skeleton = tmp_path / "planted.skeleton.html"
    skeleton.write_text(_skeleton(KEY), encoding="utf-8")
    key = tmp_path / "shape.key"
    key.write_text("not hex at all", encoding="utf-8")
    assert vfl.main(["--skeleton", str(skeleton), "--key", str(key)]) == 2
    assert "not hex" not in capsys.readouterr().out
