"""Write ``tests/fixtures/live8/messaging_composer.html`` from the live lane's
session-8 skeleton of the messaging page. Lane U, 2026-10-10.

WHAT THE CAPTURE IS, MEASURED (counts only, ``_audit/2026-09-28-lane-u-uploads.md``
section 5): the live lane's ``lk_thread`` load of 14:20, saved as a SKELETON
(``_state/live8/lk_thread.skeleton.html``, untracked, never committed). It
draws the messaging page with the NEW-MESSAGE composer in its detail pane --
the heading "New message", one recipient typeahead, no message list, no
conversation title, no active row -- not an opened conversation. Its reply
form is the composer's: one ``main form.msg-form``, one editor, one Send
(disabled), and two ``div.msg-form__upload-attachment`` wrappers, each one
``input[type=file]`` beside one labelled button.

WHAT THIS WRITES. The shipped reduction, imported and not rewritten:
``_probe_live_lane_session_2.tracked_copy`` -- every keyed shape of a value
becomes ONE ``x``, an id reference keeps only its 8-hex key, LinkedIn's own
words stay -- with ONE substitution made before it runs:

    THE TWO ``accept`` DECLARATIONS. The skeleton keeps each as a keyed
    shape, which the copy would turn into ``x``, and an ``x`` satisfies
    neither declaration the aim cross-checks. Each is replaced by the
    declaration this server recorded live on 2026-09-05 (and already tracks,
    ``tests/test_send_attachment.py``) ONLY WHEN THE SHAPE AGREES EXACTLY --
    letters, digits and length. ``image/*`` is L5 D0 n7; the documents
    declaration is L52 D1 n85. A token of any other shape refuses the build.
    The keyed hash is not used: the key stays with the live lane.

It prints sizes and counts, never a value, and writes nothing but the fixture.

    python scripts/_build_live8_composer_fixture.py --capture <skeleton path>
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from _probe_live_lane_session_2 import _KEYED_SHAPE, tracked_copy  # noqa: E402

REPO = HERE.parent
OUT = REPO / "tests" / "fixtures" / "live8" / "messaging_composer.html"

#: The two declarations, as recorded live on 2026-09-05 and tracked since.
IMAGES = "image/*"
DOCUMENTS = ("image/*,.ai,.psd,.pdf,.doc,.docx,.ppt,.pptx,.pps,.ppsx,.xls,"
             ".xlsx,.txt,.eml,.mov,.mp4")

#: A file input's accept attribute holding one keyed shape. The skeleton writes
#: ``accept`` after ``class`` and before ``type="file"``.
_ACCEPT = re.compile(r'(<input\b[^>]*\baccept=")(\{L\d+D\d+n\d+:[0-9a-f]{8}\})("[^>]*\btype="file")')


def shape(text: str) -> tuple[int, int, int]:
    return (sum(c.isalpha() for c in text), sum(c.isdigit() for c in text), len(text))


def substitute_accepts(skeleton: str) -> tuple[str, list[str]]:
    """Replace each file input's accept shape by the declaration it matches."""
    by_shape = {shape(IMAGES): IMAGES, shape(DOCUMENTS): DOCUMENTS}
    assert len(by_shape) == 2, "the two declarations must differ in shape"
    seen: list[str] = []

    def one(match: "re.Match[str]") -> str:
        token = _KEYED_SHAPE.fullmatch(match.group(2))
        assert token, "not a keyed shape"
        key = (int(token.group(1)), int(token.group(2)), int(token.group(3)))
        if key not in by_shape:
            raise SystemExit("REFUSING: an accept shape matches neither recorded declaration.")
        value = by_shape[key]
        seen.append("images" if value == IMAGES else "images_and_documents")
        return match.group(1) + value + match.group(3)

    return _ACCEPT.sub(one, skeleton), seen


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--capture", required=True, help="the session-8 skeleton")
    args = parser.parse_args(argv)
    skeleton = Path(args.capture).read_text(encoding="utf-8")
    substituted, seen = substitute_accepts(skeleton)
    if sorted(seen) != ["images", "images_and_documents"]:
        raise SystemExit(f"REFUSING: {len(seen)} accept declaration(s) matched; the measured shape is two, one of each.")
    copy = tracked_copy(substituted)
    leftover = len(_KEYED_SHAPE.findall(copy))
    if leftover:
        raise SystemExit(f"REFUSING: {leftover} keyed shape(s) survived the reduction.")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(copy, encoding="ascii", newline="\n")
    print(f"wrote {OUT.relative_to(REPO).as_posix()}: {len(copy)} bytes, "
          f"declarations {sorted(seen)}, 0 keyed shapes left")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
