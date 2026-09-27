"""No tracked text file opens with a bare model-id line.

THE CALL (orchestrator, 2026-09-27 19:52, to lane G): a bare model-id first
line in a tracked document is model attribution -- the class the operator's
no-attribution rule exists for, in a file instead of a commit trailer.
Nineteen `_audit/` records opened with one (the id, a blank line, then the
title), across nine lanes' records from 2026-09-23 on; every one was removed
the same day, and this file keeps the line out.

WHAT IT IS ABOUT, AND WHAT IT IS NOT. An attribution HEADER: the WHOLE first
line is a model id and nothing else -- the anchored shape the orchestrator
gave, ``^claude-[a-z0-9.-]+(\\[1m\\])?$``. Prose that MENTIONS a model is not
touched, on line 1 or anywhere: this repository's records measure which model
their agents ran and say so in sentences, and a measurement is not a byline.
The control at the bottom holds that half, so the rule cannot widen into
policing prose without a test going red.

WHY THE TRACKED SET. A header in an ignored file is published nowhere; a
header in a tracked one is served with the repository. The enumeration is
``git ls-files``, so the impact gate runs this file on every change.
"""
from __future__ import annotations

import pathlib
import re
import subprocess

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]

#: THE WHOLE FIRST LINE, as ruled: a model id, and at most the context-window
#: suffix the nineteen carried. Anchored at both ends, so a sentence that
#: contains an id is not one.
MODEL_ID_LINE = re.compile(r"^claude-[a-z0-9.-]+(\[1m\])?$")

#: How far into a file the binary sniff reads -- the convention git itself uses.
_SNIFF = 8192


def first_line(data: bytes) -> str | None:
    """The first line as text -- a UTF-8 byte-order mark and a carriage return
    removed, because a Windows checkout writes both a header and its CRLF --
    or ``None`` for a binary file."""
    if b"\0" in data[:_SNIFF]:
        return None
    line = data.split(b"\n", 1)[0].rstrip(b"\r")
    if line.startswith(b"\xef\xbb\xbf"):
        line = line[3:]
    return line.decode("utf-8", "replace")


def opens_with_a_model_id(data: bytes) -> bool:
    line = first_line(data)
    return line is not None and MODEL_ID_LINE.match(line) is not None


def offenders(root: pathlib.Path = REPO) -> list[str]:
    """Every tracked file under ``root`` whose first line is a bare model id."""
    listing = subprocess.run(
        ["git", "ls-files", "-z"], cwd=root, capture_output=True, check=True
    ).stdout
    found = []
    for name in (part.decode("utf-8") for part in listing.split(b"\0") if part):
        try:
            data = (root / name).read_bytes()
        except OSError:
            continue  # tracked but absent from this checkout: nothing is served
        if opens_with_a_model_id(data):
            found.append(name)
    return found


def test_no_tracked_file_opens_with_a_model_id_line():
    found = offenders()
    assert found == [], (
        "these tracked files open with a bare model-id line -- model "
        "attribution in a file, which the operator's no-attribution rule "
        "forbids as it forbids a commit trailer. Delete the line (and the "
        "blank line under it):\n    " + "\n    ".join(found)
    )


# ---------------------------------------------------------------------------
# The controls: shown failing on a planted document, and shown passing prose
# ---------------------------------------------------------------------------


def _repo_with(tmp_path: pathlib.Path, files: dict[str, bytes]) -> pathlib.Path:
    """A throwaway repository tracking exactly ``files``."""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    for name, data in files.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    subprocess.run(["git", "add", "--", *files], cwd=tmp_path, check=True)
    return tmp_path


#: THE SHAPE THE NINETEEN CARRIED, byte for byte on a Windows checkout: the id,
#: a CRLF, a blank line, then the document's own title.
PLANTED = b"claude-opus-5-5[1m]\r\n\r\n# A record of some lane\r\n\r\nBody.\r\n"


def test_the_guard_convicts_a_planted_document(tmp_path):
    """THE CONTROL THAT CAN FAIL: the real shape, tracked, is found by the
    same enumeration the guard runs -- and only it."""
    root = _repo_with(tmp_path, {
        "_audit/planted.md": PLANTED,
        "_audit/clean.md": b"# A record of some lane\n\nBody.\n",
    })
    assert offenders(root) == ["_audit/planted.md"]


@pytest.mark.parametrize(
    "data",
    [
        PLANTED,
        b"claude-opus-5-5\n# Title\n",
        b"claude-sonnet-5\n",
        b"claude-example-0[1m]",
        b"\xef\xbb\xbfclaude-fable-5\r\n",
    ],
    ids=["the measured shape", "no window suffix", "another family", "no newline at all", "behind a BOM"],
)
def test_every_bare_id_header_is_convicted(data):
    assert opens_with_a_model_id(data), data


@pytest.mark.parametrize(
    "data",
    [
        b"# Title\n\nEvery child's transcript reads `claude-opus-5-5` throughout.\n",
        b"Children ran claude-opus-5-5[1m] throughout this lane.\n",
        b"claude-opus-5-5[1m] is the model every child ran.\n",
        b"# Title\nclaude-opus-5-5[1m]\n",
        b"  claude-opus-5-5[1m]\n",
        b"CLAUDE-OPUS-5-5\n",
        b"\x00\x01claude-opus-5-5[1m]\n",
    ],
    ids=[
        "prose in the body",
        "prose on line 1",
        "a sentence opening with the id",
        "the id below line 1",
        "indented, so not a bare line",
        "not the lowercase id shape",
        "a binary file",
    ],
)
def test_a_document_that_mentions_a_model_is_left_alone(data):
    """THE OTHER HALF: this rule is about attribution headers, not prose. A
    file that MENTIONS a model -- on line 1 or anywhere -- passes, and so does
    a binary file, which has no lines."""
    assert not opens_with_a_model_id(data), data


def test_the_prose_control_passes_the_whole_guard_too(tmp_path):
    """And through the same enumeration, not just the predicate: a tracked
    record that measures its children's model in prose is not an offender."""
    root = _repo_with(tmp_path, {
        "_audit/measured.md": (
            b"# A record\n\nEvery assistant message in the four transcripts "
            b"carries `claude-opus-5-5`, measured rather than assumed.\n"
        ),
    })
    assert offenders(root) == []
