"""The bytes handed to the browser are the bytes whose digest was compared.

THE WINDOW THIS FILE CLOSES (lane U, 2026-10-10). ``writes.perform`` re-read
the file's digest at the drain point, compared it with the digest the preview
printed, and then handed the browser the PATH. A browser reads a path when it
is handed one -- or later, when the page reads the file -- so a file swapped
AFTER the comparison and BEFORE that read uploaded bytes nobody compared. The
digest check was real; it guarded the wrong moment.

THE FIX IS TO HAND OVER WHAT WAS CHECKED. The drain point now reads the file
ONCE, compares the digest of exactly those bytes, and hands the browser those
bytes as a payload (Playwright's ``files=[{name, mimeType, buffer}]``). A swap
on disk after the read changes nothing the browser holds.

HOW THE SWAP IS PLACED, and why the test does not depend on the code it
tests. :class:`_SwapAtTheHandOff` wraps the page and rewrites the file on disk
at the last possible instant -- inside the hand-off call, before it is passed
on. That is after any check the code under test can make, whatever its order,
so the same test measures the old code and the new one.

RED FIRST, recorded in ``_audit/2026-09-28-lane-u-uploads.md`` section 4:
on the parent commit both tests below FAILED -- the node held the swapped
bytes, and the type the browser reported was the one the file's name implied
rather than the one its bytes declare -- and they pass on the hand-off this
file pins.
"""

from __future__ import annotations

import pytest

from linkedin_server import attachments, config, uploads, writes
from tests.test_writes import (  # noqa: F401 - fixtures used by injection
    FixtureNavigator,
    browser_page,
    writes_on,
)
from tests.test_writes_nine import FEED_MARKUP

#: Bytes the preview reads and prints a digest of.
ORIGINAL = b"\x89PNG\r\n\x1a\n" + b"approved-bytes|" * 24
#: Bytes put under the same path after every check has passed.
SWAPPED = b"\x89PNG\r\n\x1a\n" + b"SWAPPED-AFTER-THE-CHECK|" * 24

#: The vehicle's address and a page whose one control is a real file input.
TARGET_URL = "https://www.linkedin.com/preload/sharebox/"
FILE_INPUT_MARKUP = (
    "<!doctype html><html><body>"
    "<form id='f'><input type='file' id='upload-target'></form>"
    "</body></html>"
)


@pytest.fixture()
def root(tmp_path, monkeypatch):
    """The declared upload root, pointed at a temp directory (see test_uploads)."""
    directory = tmp_path / "uploads"
    directory.mkdir()
    monkeypatch.setattr(config, "UPLOAD_ROOT", directory)
    return directory


class _SwapAtTheHandOff:
    """A page that rewrites the file on disk inside the hand-off call.

    Everything else is the real page: attribute access falls through to it,
    so navigation, reads and the file input are Chromium's own.
    """

    def __init__(self, page, path, replacement: bytes) -> None:
        self._page = page
        self._path = path
        self._replacement = replacement
        self.swaps = 0

    async def set_input_files(self, selector, files, **kwargs):
        self._path.write_bytes(self._replacement)
        self.swaps += 1
        return await self._page.set_input_files(selector, files, **kwargs)

    def __getattr__(self, name):
        return getattr(self._page, name)


async def _granted(page, root, monkeypatch, *, name: str, data: bytes):
    """A real grant for an upload: preview off a live read, token redeemed.

    The vehicle is ``publish_post`` forced into ``UPLOAD_ACTIONS``, the same
    one ``tests/test_uploads.py`` section 10 uses and for the same reasons: a
    one-component target that is wholly the path, and a constant address.
    """
    monkeypatch.setattr(writes, "UPLOAD_ACTIONS", frozenset({"publish_post"}))
    path = root / name
    path.write_bytes(data)
    spec = writes.spec_for_action("publish_post")
    block = await writes.preview(
        spec,
        target=str(path),
        navigator=FixtureNavigator({writes.FEED_URL: FEED_MARKUP}),
        page=page,
    )
    grant = writes.consume(block["to_confirm"], action="publish_post", target=str(path))
    return grant, path, block


async def _arm(page, spec, grant, anchor):
    """The arm a wiring supplies: a measured file input, classified as one."""
    return (
        "composer_present",
        "a file input, for the test",
        "#upload-target",
        writes.UPLOAD_CONTROL_KIND,
    )


async def _on_the_node(page) -> tuple[bytes, str, str]:
    """What the browser actually holds: the bytes, the name and the type."""
    raw = await page.locator("#upload-target").evaluate(
        "async el => el.files.length"
        " ? [Array.from(new Uint8Array(await el.files[0].arrayBuffer())),"
        "    el.files[0].name, el.files[0].type]"
        " : [[], '', '']"
    )
    return bytes(raw[0]), raw[1], raw[2]


async def test_a_file_swapped_after_the_check_does_not_reach_the_browser(
    writes_on, browser_page, root, monkeypatch
):
    """**THE WINDOW, MEASURED ON THE NODE.**

    The swap is real (asserted: the disk holds the new bytes and the swap
    happened once, inside the hand-off) and the browser must still hold the
    bytes he was shown. On the path hand-off it held the swapped ones.
    """
    grant, path, block = await _granted(
        browser_page, root, monkeypatch, name="photo.png", data=ORIGINAL
    )
    monkeypatch.setattr(writes, "_live_control", _arm)
    page = _SwapAtTheHandOff(browser_page, path, SWAPPED)

    out = await writes.perform(
        FixtureNavigator({TARGET_URL: FILE_INPUT_MARKUP}), page, grant
    )

    assert page.swaps == 1, "the swap must have happened inside the hand-off"
    assert path.read_bytes() == SWAPPED, "the disk must hold other bytes now"
    held, held_name, _held_type = await _on_the_node(browser_page)
    assert held != SWAPPED, (
        "THE BROWSER RECEIVED BYTES NOBODY COMPARED: the file was swapped "
        "after the digest check and the hand-off read the path."
    )
    assert held == ORIGINAL
    assert held_name == "photo.png"
    # AND THE REPORT NAMES THE DIGEST OF WHAT WAS HANDED, which is the
    # preview's -- the swapped file's digest appears nowhere.
    assert out["uploaded"]["sha256_prefix"] == block["file"]["sha256_prefix"]
    assert out["uploaded"]["handed_over"] == "the verified bytes, not the path"


async def test_the_type_handed_over_is_the_type_read_from_the_bytes(
    writes_on, browser_page, root, monkeypatch
):
    """The browser is told what the bytes ARE, not what the name implies.

    A PNG saved as ``notes.txt``: on the path hand-off the browser typed it
    from the name (``text/plain``). The preview prints the type read from the
    bytes, so the hand-off declares that one -- one reading, used twice. Not a
    refusal: no extension is refused anywhere (``uploads.py`` says why).
    """
    grant, _path, block = await _granted(
        browser_page, root, monkeypatch, name="notes.txt", data=ORIGINAL
    )
    monkeypatch.setattr(writes, "_live_control", _arm)

    await writes.perform(
        FixtureNavigator({TARGET_URL: FILE_INPUT_MARKUP}), browser_page, grant
    )

    held, held_name, held_type = await _on_the_node(browser_page)
    assert held == ORIGINAL
    assert held_name == "notes.txt"
    assert held_type == "image/png", held_type
    assert block["file"]["type_from_bytes"].startswith("image/png")


async def test_an_untouched_file_is_handed_over_whole(
    writes_on, browser_page, root, monkeypatch
):
    """THE POSITIVE CONTROL: no swap, and the node holds exactly the file."""
    grant, path, block = await _granted(
        browser_page, root, monkeypatch, name="photo.png", data=ORIGINAL
    )
    monkeypatch.setattr(writes, "_live_control", _arm)

    out = await writes.perform(
        FixtureNavigator({TARGET_URL: FILE_INPUT_MARKUP}), browser_page, grant
    )

    held, held_name, held_type = await _on_the_node(browser_page)
    assert (held, held_name, held_type) == (ORIGINAL, "photo.png", "image/png")
    assert path.read_bytes() == ORIGINAL
    assert out["uploaded"]["files_handed_to_the_browser"] == 1


def test_the_one_read_carries_the_digest_of_exactly_its_own_bytes(root):
    """Offline: the digest the drain point compares is of the bytes it hands.

    ``read_once`` returns the bytes and their digest together, and the digest
    is the path guard's own algorithm (``uploads.digest_of``) over those
    bytes -- so the comparison in ``perform`` and the hand-off are one
    reading, not two.
    """
    path = root / "photo.png"
    path.write_bytes(ORIGINAL)
    upload = uploads.resolve_upload_file(str(path))
    verified = attachments.read_once(upload)
    assert verified.data == ORIGINAL
    assert verified.digest == uploads.digest_of(upload)
    assert verified.as_payload() == {
        "name": "photo.png", "mimeType": "image/png", "buffer": ORIGINAL
    }
    path.write_bytes(SWAPPED)
    assert verified.data == ORIGINAL, "a frozen read must not follow the disk"
    assert attachments.read_once(upload).digest != verified.digest


def test_the_one_read_re_runs_the_path_guard_at_the_drain_point(root):
    """A file that turned into a directory after the preview is refused, by name.

    The preview checked a regular file; by the drain point the same path is a
    directory. The read refuses with the path guard's own words rather than
    reading anything.
    """
    path = root / "photo.png"
    path.write_bytes(ORIGINAL)
    upload = uploads.resolve_upload_file(str(path))
    path.unlink()
    path.mkdir()
    with pytest.raises(Exception) as caught:
        attachments.read_once(upload)
    assert "is a directory" in str(caught.value)


@pytest.mark.parametrize(
    ("data", "mime", "family"),
    [
        (b"\x89PNG\r\n\x1a\n" + b"x" * 8, "image/png", "image"),
        (b"\xff\xd8\xff\xe0" + b"x" * 8, "image/jpeg", "image"),
        (b"GIF89a" + b"x" * 8, "image/gif", "image"),
        (b"RIFF\x00\x00\x00\x00WEBPVP8 ", "image/webp", "image"),
        (b"\x00\x00\x00\x18ftypisom" + b"x" * 8, "video/mp4", "video"),
        (b"\x00\x00\x00\x14ftypqt  " + b"x" * 8, "video/quicktime", "video"),
        (b"%PDF-1.7\n" + b"x" * 8, "application/pdf", "document"),
        (b"Testing a tool, ignore this.\n", "text/plain", "document"),
        (b"\x00\x01\x02\x03binary", attachments.UNRECOGNISED_TYPE, "other"),
    ],
)
def test_the_type_is_read_from_the_signature(data, mime, family):
    """Each signature, and the unrecognised case reported rather than refused."""
    got_mime, _label, got_family = attachments.sniff(data)
    assert (got_mime, got_family) == (mime, family)
